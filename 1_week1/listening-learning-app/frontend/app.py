import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set path manually for torch
torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)] 

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_dir))

# Import after environment setup
from exercise_generator import ExercisesGenerator
from audio_generator import AudioGenerator
# Initialize generators at startup
try:
    generator = ExercisesGenerator()
    audio_generator = AudioGenerator()
except Exception as e:
    logger.error(f"Error initializing generators: {e}")
    generator = None
    audio_generator = None

def display_multiple_choice_exercise(exercise):
    """Display a multiple choice exercise in an interactive way"""
    if not exercise:
        st.error("No exercise generated")
        return
    
    # Initialize session state for exercise and answers if not exists
    if 'current_exercise' not in st.session_state:
        st.session_state.current_exercise = exercise
        st.session_state.user_answers = {}
        st.session_state.submitted = False
        
        # Generate audio when exercise is first loaded
        try:
            logger.info(f"Starting audio generation for content: {exercise['content'][:100]}...")  # Log first 100 chars
            audio_files = audio_generator.generate_audio(
                exercise_id="current",
                content={'content': exercise['content']}
            )
            logger.info(f"Audio generation returned: {audio_files}")
            
            if 'content' in audio_files:
                audio_path = audio_files['content']
                logger.info(f"Attempting to read audio from: {audio_path}")
                
                # Check if path exists and is readable
                if not os.path.exists(audio_path):
                    logger.error(f"Audio file does not exist at path: {audio_path}")
                    raise FileNotFoundError(f"Audio file not found: {audio_path}")
                    
                # Check file size
                file_size = os.path.getsize(audio_path)
                logger.info(f"Audio file size: {file_size} bytes")
                
                with open(audio_path, 'rb') as f:
                    st.session_state.current_audio = f.read()
                logger.info("Successfully loaded audio file into session state")
            else:
                logger.error(f"No 'content' key in audio_files: {audio_files}")
                raise KeyError("No 'content' key in audio files response")
            
        except Exception as e:
            logger.error(f"Error generating/loading audio: {e}", exc_info=True)
            st.error(f"Could not generate audio for this exercise: {str(e)}")
            st.session_state.current_audio = None
    
    # Create a container for the exercise content
    exercise_container = st.container()
    
    with exercise_container:
        st.write("### Listen to the Dialog")
        if st.session_state.get('current_audio'):
            st.audio(st.session_state.current_audio)
        else:
            st.error("Audio not available")
        
        # Add a button to show/hide text content
        if st.button("Show/Hide Text"):
            st.session_state.show_text = not st.session_state.get('show_text', False)
            
        if st.session_state.get('show_text'):
            st.write("### Content")
            st.write(st.session_state.current_exercise.get('content', ''))
        
        st.write("### Questions")
        correct_count = 0
        total_questions = len(st.session_state.current_exercise.get('questions', []))
        
        for i, question in enumerate(st.session_state.current_exercise.get('questions', []), 1):
            st.write(f"\n**Question {i}:** {question.get('question', '')}")
            
            # Create radio buttons for options
            options = question.get('options', [])
            question_key = f"question_{i}"
            correct_answer = question.get('correct_answer')
            
            # Initialize this question's answer in session state if not exists
            if question_key not in st.session_state.user_answers:
                st.session_state.user_answers[question_key] = None
            
            # If submitted, show colored options
            if st.session_state.submitted and st.session_state.user_answers.get(question_key):
                user_answer = st.session_state.user_answers[question_key]
                is_correct = user_answer == correct_answer
                if is_correct:
                    correct_count += 1
                
                # Display options with coloring
                for option in options:
                    if option == correct_answer and option == user_answer:
                        st.success(f"✓ {option}")
                    elif option == correct_answer:
                        st.success(f"✓ {option} (Correct answer)")
                    elif option == user_answer:
                        st.error(f"✗ {option} (Your answer)")
                    else:
                        st.write(f"  {option}")
            else:
                # Create radio buttons for selection
                user_answer = st.radio(
                    f"Select answer for question {i}",
                    options,
                    key=f"radio_{question_key}",
                    index=None,
                    label_visibility="collapsed"
                )
                
                # Update session state when answer changes
                if user_answer is not None:
                    st.session_state.user_answers[question_key] = user_answer
    
    # Create a container for the submit button and final score
    result_container = st.container()
    
    with result_container:
        # Submit button
        if st.button("Submit Answers", key="submit_button"):
            if any(answer is None for answer in st.session_state.user_answers.values()):
                st.error("Please answer all questions before submitting.")
            else:
                st.session_state.submitted = True
                st.rerun()
        
        # Show final score if submitted
        if st.session_state.submitted:
            st.write("---")  # Divider
            score_percentage = (correct_count / total_questions) * 100
            if score_percentage >= 70:
                st.success(f"### Final Score: {score_percentage:.1f}%\nYou got {correct_count} out of {total_questions} questions correct!")
            else:
                st.error(f"### Final Score: {score_percentage:.1f}%\nYou got {correct_count} out of {total_questions} questions correct!")

def display_dialog_matching_exercise(exercise):
    """Display a dialog matching exercise in a formatted way"""
    if not exercise:
        st.error("No exercise generated")
        return
        
    st.write("### Dialogs")
    for dialog in exercise.get('dialogs', []):
        st.write(f"- {dialog}")
        
    st.write("\n### Images")
    for image in exercise.get('images', []):
        st.write(f"- {image}")
        
    st.write("\n### Correct Matches")
    for dialog, image in exercise.get('correct_matches', {}).items():
        st.write(f"\n**Dialog:** {dialog}")
        st.write(f"**Matches with:** {image}")

def main():
    st.title("Listening learning")
    
    if not generator or not audio_generator:
        st.error("Could not initialize exercise or audio generator. Please check your credentials.")
        return
    
    # Create tabs for different exercise types
    exercise_type = st.sidebar.radio(
        "Select Exercise Type",
        ["Multiple Choice", "Dialog Matching"]
    )
    
    # Topics dropdown
    topics = [
        "Ordering food at a restaurant",
        "Taking the train",
        "Shopping for clothes",
        "Making a hotel reservation",
        "Asking for directions"
    ]
    selected_topic = st.selectbox("Select a topic", topics)
    
    # Generate button
    if st.button("Generate Exercise", key="generate_button"):
        with st.spinner("Generating exercise..."):
            try:
                if exercise_type == "Multiple Choice":
                    exercise = generator.generate_multiple_choice(selected_topic)
                    logger.info(f"Generated exercise: {exercise}")
                    
                    # Validate exercise structure
                    if not exercise:
                        raise ValueError("Generated exercise is None")
                    if not isinstance(exercise, dict):
                        raise ValueError(f"Exercise should be a dict, got {type(exercise)}")
                    if 'content' not in exercise or 'questions' not in exercise:
                        raise ValueError(f"Exercise missing required fields. Got keys: {exercise.keys()}")
                    if not exercise['questions']:
                        raise ValueError("No questions in the exercise")
                    
                    # Set session state before displaying
                    st.session_state.current_exercise = exercise
                    st.session_state.user_answers = {}
                    st.session_state.submitted = False
                    
                else:  # Dialog Matching
                    exercise = generator.generate_dialog_matching(selected_topic)
                    display_dialog_matching_exercise(exercise)
            except Exception as e:
                logger.error(f"Error generating exercise: {e}", exc_info=True)
                st.error(f"Error generating exercise: {str(e)}\nPlease try again or select a different topic.")
    
    # Display current exercise if it exists
    if hasattr(st.session_state, 'current_exercise') and st.session_state.current_exercise:
        display_multiple_choice_exercise(st.session_state.current_exercise)

if __name__ == "__main__":
    main() 
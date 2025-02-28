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
    
    # Create a container for the exercise content
    exercise_container = st.container()
    
    with exercise_container:
        st.write("### Content")
        st.write(st.session_state.current_exercise.get('content', ''))
        
        st.write("### Questions")
        for i, question in enumerate(st.session_state.current_exercise.get('questions', []), 1):
            st.write(f"\n**Question {i}:** {question.get('question', '')}")
            
            # Create radio buttons for options
            options = question.get('options', [])
            question_key = f"question_{i}"
            
            # Initialize this question's answer in session state if not exists
            if question_key not in st.session_state.user_answers:
                st.session_state.user_answers[question_key] = None
                
            # Create radio buttons and update session state
            answer = st.radio(
                f"Select answer for question {i}",
                options,
                key=f"radio_{question_key}",
                index=None,
                label_visibility="collapsed"
            )
            
            # Update session state when answer changes
            if answer is not None:
                st.session_state.user_answers[question_key] = answer
    
    # Create a container for the submit button and results
    result_container = st.container()
    
    with result_container:
        # Submit button
        if st.button("Submit Answers", key="submit_button"):
            st.session_state.submitted = True
        
        # Show results if submitted
        if st.session_state.submitted:
            st.write("---")  # Divider
            st.write("### Results")
            
            correct_count = 0
            total_questions = len(st.session_state.current_exercise.get('questions', []))
            
            for i, question in enumerate(st.session_state.current_exercise.get('questions', []), 1):
                question_key = f"question_{i}"
                user_answer = st.session_state.user_answers.get(question_key)
                correct_answer = question.get('correct_answer')
                
                is_correct = user_answer == correct_answer
                if is_correct:
                    correct_count += 1
                
                # Display results with color-coding
                st.markdown(
                    f"**Question {i}:** "
                    f"{'✅' if is_correct else '❌'} "
                    f"Your answer: {user_answer}\n\n"
                    f"Correct answer: {correct_answer}"
                )
            
            # Display final score
            score_percentage = (correct_count / total_questions) * 100
            st.write(f"\n### Final Score: {score_percentage:.1f}%")
            st.write(f"You got {correct_count} out of {total_questions} questions correct!")

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

# Initialize generator at startup
try:
    generator = ExercisesGenerator()
except Exception as e:
    logger.error(f"Error initializing generator: {e}")
    generator = None

def main():
    st.title("Listening learning")
    
    if not generator:
        st.error("Could not initialize exercise generator. Please check your AWS credentials.")
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
        # Clear previous exercise state when generating new one
        st.session_state.current_exercise = None
        st.session_state.user_answers = {}
        st.session_state.submitted = False
        
        with st.spinner("Generating exercise..."):
            try:
                if exercise_type == "Multiple Choice":
                    exercise = generator.generate_multiple_choice(selected_topic)
                    display_multiple_choice_exercise(exercise)
                else:  # Dialog Matching
                    exercise = generator.generate_dialog_matching(selected_topic)
                    display_dialog_matching_exercise(exercise)
            except Exception as e:
                logger.error(f"Error generating exercise: {e}")
                st.error(f"Error generating exercise: {str(e)}")
    
    # Display current exercise if it exists
    if hasattr(st.session_state, 'current_exercise') and st.session_state.current_exercise:
        display_multiple_choice_exercise(st.session_state.current_exercise)

if __name__ == "__main__":
    main() 
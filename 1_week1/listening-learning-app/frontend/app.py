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
        
    st.write("### Content")
    st.write(exercise.get('content', ''))
    
    # Store user answers in session state
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
        st.session_state.submitted = False
    
    st.write("### Questions")
    for i, question in enumerate(exercise.get('questions', []), 1):
        st.write(f"\n**Question {i}:** {question.get('question', '')}")
        
        # Create radio buttons for options
        options = question.get('options', [])
        question_key = f"question_{i}"
        st.session_state.user_answers[question_key] = st.radio(
            f"Select answer for question {i}",
            options,
            key=question_key,
            label_visibility="collapsed"
        )
    
    # Submit button
    if st.button("Submit Answers"):
        st.session_state.submitted = True
        
        # Calculate and display score
        correct_count = 0
        total_questions = len(exercise.get('questions', []))
        
        st.write("### Results")
        for i, question in enumerate(exercise.get('questions', []), 1):
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
    if st.button("Generate Exercise"):
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

if __name__ == "__main__":
    main() 
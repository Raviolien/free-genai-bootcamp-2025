import streamlit as st
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_dir))

# Import after adding backend to path
from exercise_generator import ExercisesGenerator

def display_multiple_choice_exercise(exercise):
    """Display a multiple choice exercise in a formatted way"""
    if not exercise:
        st.error("No exercise generated")
        return
        
    st.write("### Content")
    st.write(exercise.get('content', ''))
    
    st.write("### Questions")
    for i, question in enumerate(exercise.get('questions', []), 1):
        st.write(f"\n**Question {i}:** {question.get('question', '')}")
        for option in question.get('options', []):
            st.write(f"- {option}")
        st.write(f"*Correct answer:* {question.get('correct_answer', '')}")

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

def init_session_state():
    """Initialize session state variables"""
    if 'generator' not in st.session_state:
        try:
            st.session_state.generator = ExercisesGenerator()
        except Exception as e:
            st.error(f"Error initializing exercise generator: {str(e)}")
            st.session_state.generator = None

def main():
    st.title("Listening learning")
    
    # Initialize session state
    init_session_state()
    
    if not st.session_state.generator:
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
                    exercise = st.session_state.generator.generate_multiple_choice(selected_topic)
                    display_multiple_choice_exercise(exercise)
                else:  # Dialog Matching
                    exercise = st.session_state.generator.generate_dialog_matching(selected_topic)
                    display_dialog_matching_exercise(exercise)
            except Exception as e:
                st.error(f"Error generating exercise: {str(e)}")

if __name__ == "__main__":
    main() 
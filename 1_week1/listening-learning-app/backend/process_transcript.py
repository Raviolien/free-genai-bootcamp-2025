import os
from pathlib import Path
import json
import boto3
from datetime import datetime

class TranscriptProcessor:
    def __init__(self):
        """
        Initialize the processor with AWS Bedrock client
        """
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'  # or your preferred region
        )
        self.transcripts_dir = Path(__file__).parent / "transcripts"
        self.exercises_dir = Path(__file__).parent / "exercises"
        
        # Create exercises directory if it doesn't exist
        self.exercises_dir.mkdir(exist_ok=True)

    def process_transcript(self, transcript_file: str) -> None:
        """
        Process a transcript file and extract exercises
        
        Args:
            transcript_file (str): Name of the transcript file
        """
        transcript_path = self.transcripts_dir / transcript_file
        
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript file {transcript_file} not found")

        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_text = f.read()

        # Extract exercises using Amazon Bedrock
        exercises = self._extract_exercises(transcript_text, transcript_file)
        
        # Save different types of exercises to separate files
        self._save_exercises(exercises, transcript_file)

    def _extract_exercises(self, transcript: str, transcript_file: str) -> dict:
        """
        Use Amazon Bedrock to extract exercises from transcript
        
        Args:
            transcript (str): Full transcript text
            transcript_file (str): Name of the transcript file
            
        Returns:
            dict: Dictionary containing different types of exercises
        """
        prompt = """
        This is a French language test transcript. Some parts may be in English. 
        The transcript is structured as follows:
        1. First part: Exercise content and questions
           - Multiple choice questions with their content and options
           - Dialog matching exercises with their content
           - Other types of exercises
        2. Last part: Answers section
           - Sometimes contains full content repeated with answers
           - Sometimes only contains questions and correct answers
           
        Please analyze both parts and:
        1. Match questions from the first part with their answers from the last part
        2. For multiple choice: Match the audio content with its related questions
        3. For dialog matching: Extract dialogs and their image matches
        4. For other exercises: Extract exercise type, content and solution

        Important:
        - Extract and output only the French text (ignore English translations)
        - Match content from first part with answers from last part
        - Group questions by their related audio/dialog content
        - Include all options mentioned in the first part
        - Use correct answers from the answers section
        - Ignore exercise instructions and filler text
        - The content should be a complete text with proper punctuation, using periods (.) at the end of sentences

        Format the output as a JSON with the following structure (all text in French):
        {
            "multiple_choice": [
                {
                    "content": "text of the audio/dialog content",
                    "questions": [
                        {
                            "question": "question text",
                            "options": ["option1", "option2", ...],
                            "correct_answer": "answer from answers section"
                        }
                    ]
                }
            ],
            "dialog_matching": [
                {
                    "dialogs": ["dialog1", "dialog2", ...],
                    "images": ["image_description1", "image_description2", ...],
                    "correct_matches": {"dialog1": "imageA", ...}
                }
            ],
            "other_exercises": [
                {
                    "type": "exercise_type",
                    "content": "exercise_content",
                    "solution": "solution from answers section"
                }
            ]
        }
        """

        full_prompt = f"{prompt}\n\nHere's the transcript:\n{transcript}"
        
        messages = [{
            "role": "user",
            "content": [{"text": full_prompt}]
        }]

        try:
            # Call Bedrock's converse endpoint
            response = self.client.converse(
                modelId='amazon.nova-micro-v1:0',
                messages=messages,
                inferenceConfig={"temperature": 0}
            )
            
            # Parse the response text
            response_text = response['output']['message']['content'][0]['text']
            
            # Get video ID from transcript filename
            video_id = transcript_file.split('.')[0]  # Remove file extension
            
            # Save raw response to file using video ID
            raw_response_path = self.exercises_dir / f"{video_id}_model_response.json"
            with open(raw_response_path, 'w', encoding='utf-8') as f:
                f.write(response_text)
            
            # Extract the JSON part from the response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_text = response_text[start:end]
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                    return {
                        "multiple_choice": [],
                        "dialog_matching": [],
                        "other_exercises": []
                    }
            return {
                "multiple_choice": [],
                "dialog_matching": [],
                "other_exercises": []
            }
            
        except Exception as e:
            print(f"Error processing: {str(e)}")
            return {
                "multiple_choice": [],
                "dialog_matching": [],
                "other_exercises": []
            }

    def _save_exercises(self, exercises: dict, original_filename: str) -> None:
        """
        Save extracted exercises to separate files in plain text format
        
        Args:
            exercises (dict): Dictionary containing different types of exercises
            original_filename (str): Name of the original transcript file
        """
        base_name = original_filename.rsplit('.', 1)[0]

        # Save multiple choice exercises
        if exercises.get('multiple_choice'):
            mc_path = self.exercises_dir / f"{base_name}_multiple_choice.txt"
            with open(mc_path, 'w', encoding='utf-8') as f:
                for exercise in exercises['multiple_choice']:
                    f.write(f"Content: {exercise['content']}\n\n")
                    for question in exercise['questions']:
                        f.write(f"Question: {question['question']}\n")
                        for option in question['options']:
                            f.write(f"- {option}\n")
                        f.write(f"Correct answer: {question['correct_answer']}\n\n")
                    f.write("\n")

        # Save dialog matching exercises
        if exercises.get('dialog_matching'):
            dm_path = self.exercises_dir / f"{base_name}_dialog_matching.txt"
            with open(dm_path, 'w', encoding='utf-8') as f:
                for exercise in exercises['dialog_matching']:
                    f.write("Dialogs:\n")
                    for dialog in exercise['dialogs']:
                        f.write(f"- {dialog}\n")
                    f.write("\nImages:\n")
                    for image in exercise['images']:
                        f.write(f"- {image}\n")
                    f.write("\nCorrect matches:\n")
                    for dialog, image in exercise['correct_matches'].items():
                        f.write(f"Dialog: {dialog}\nMatches with: {image}\n\n")

        # Save other exercises
        if exercises.get('other_exercises'):
            other_path = self.exercises_dir / f"{base_name}_other_exercises.txt"
            with open(other_path, 'w', encoding='utf-8') as f:
                for exercise in exercises['other_exercises']:
                    if exercise.get('content'):
                        f.write(f"Content: {exercise['content']}\n")
                    if exercise.get('type'):
                        f.write(f"Type: {exercise['type']}\n")
                    if exercise.get('solution'):
                        f.write(f"Solution: {exercise['solution']}\n")
                    f.write("\n")

if __name__ == "__main__":
    # Initialize processor
    processor = TranscriptProcessor()
    
    # Process all transcript files in the directory
    for transcript_file in processor.transcripts_dir.glob('*.txt'):
        # Get base name without extension
        base_name = transcript_file.stem
        
        # Check if files already exist
        model_response_path = processor.exercises_dir / f"{base_name}_model_response.json"
        multiple_choice_path = processor.exercises_dir / f"{base_name}_multiple_choice.txt"
        dialog_matching_path = processor.exercises_dir / f"{base_name}_dialog_matching.txt"
        other_exercises_path = processor.exercises_dir / f"{base_name}_other_exercises.txt"
        
        # Skip if any of the files exist
        if any([
            model_response_path.exists(),
            multiple_choice_path.exists(),
            dialog_matching_path.exists(),
            other_exercises_path.exists()
        ]):
            print(f"Skipping {transcript_file.name} - exercises already exist")
            continue

        # Process file if no exercises exist
        try:
            processor.process_transcript(transcript_file.name)
            print(f"Successfully processed {transcript_file.name}")
        except Exception as e:
            print(f"Error processing {transcript_file.name}: {str(e)}") 
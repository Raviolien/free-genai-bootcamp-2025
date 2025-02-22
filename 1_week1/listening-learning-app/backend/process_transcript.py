import os
from pathlib import Path
import json
import boto3

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
        exercises = self._extract_exercises(transcript_text)
        
        # Save different types of exercises to separate files
        self._save_exercises(exercises, transcript_file)

    def _extract_exercises(self, transcript: str) -> dict:
        """
        Use Amazon Bedrock to extract exercises from transcript
        
        Args:
            transcript (str): Full transcript text
            
        Returns:
            dict: Dictionary containing different types of exercises
        """
        prompt = """
        Please analyze this French language test transcript and extract:
        1. Multiple choice exercises (including questions, options, and correct answers)
        2. Dialog matching exercises (including dialogs, images to match, and correct matches)
        3. Any other types of exercises

        Format the output as a JSON with the following structure:
        {
            "multiple_choice": [
                {
                    "question": "text",
                    "options": ["option1", "option2", ...],
                    "correct_answer": "answer"
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
                    "solution": "solution"
                }
            ]
        }

        Extract only the actual exercises, questions, and answers. Ignore instructions and filler text.
        Provide only the JSON output, no additional text.
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
            
            # Parse the response text as JSON
            response_text = response['output']['message']['content'][0]['text']
            
            # Clean up the response text by removing markdown code block
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```'):
                # Remove the opening ```json and closing ``` if present
                cleaned_text = cleaned_text.split('\n', 1)[1]  # Remove first line
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text.rsplit('\n', 1)[0]  # Remove last line
            
            try:
                return json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Raw response: {response_text}")
                return {
                    "multiple_choice": [],
                    "dialog_matching": [],
                    "other_exercises": []
                }
            
        except Exception as e:
            print(f"Error calling Bedrock API: {e}")
            return {
                "multiple_choice": [],
                "dialog_matching": [],
                "other_exercises": []
            }

    def _save_exercises(self, exercises: dict, original_filename: str) -> None:
        """
        Save extracted exercises to separate files
        
        Args:
            exercises (dict): Dictionary containing different types of exercises
            original_filename (str): Name of the original transcript file
        """
        base_name = original_filename.rsplit('.', 1)[0]

        # Save multiple choice exercises
        if exercises.get('multiple_choice'):
            mc_path = self.exercises_dir / f"{base_name}_multiple_choice.txt"
            with open(mc_path, 'w', encoding='utf-8') as f:
                json.dump(exercises['multiple_choice'], f, ensure_ascii=False, indent=2)

        # Save dialog matching exercises
        if exercises.get('dialog_matching'):
            dm_path = self.exercises_dir / f"{base_name}_dialog_matching.txt"
            with open(dm_path, 'w', encoding='utf-8') as f:
                json.dump(exercises['dialog_matching'], f, ensure_ascii=False, indent=2)

        # Save other exercises
        if exercises.get('other_exercises'):
            other_path = self.exercises_dir / f"{base_name}_other_exercises.txt"
            with open(other_path, 'w', encoding='utf-8') as f:
                json.dump(exercises['other_exercises'], f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Initialize processor and process transcripts
    processor = TranscriptProcessor()
    
    # Process all transcript files in the directory
    for transcript_file in processor.transcripts_dir.glob('*.txt'):
        try:
            processor.process_transcript(transcript_file.name)
            print(f"Successfully processed {transcript_file.name}")
        except Exception as e:
            print(f"Error processing {transcript_file.name}: {str(e)}") 
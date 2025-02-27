from pathlib import Path
import json
from typing import List, Dict, Optional
import boto3
from vector_store import ExerciseVectorStore

class ExercisesGenerator:
    def __init__(self, region_name: str = "us-east-1"):
        """
        Initialize the exercises generator
        
        Args:
            region_name (str): AWS region name
        """
        self.bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name
        )
        self.vector_store = ExerciseVectorStore()

    def _get_example_exercises(self, exercise_type: str, topic: str, n_examples: int = 2) -> List[Dict]:
        """Get example exercises from the vector store to use as context"""
        return self.vector_store.query_similar_exercises(
            query=topic,
            exercise_type=exercise_type,
            n_results=n_examples
        )

    def _format_multiple_choice_examples(self, examples: List[Dict]) -> str:
        """Format multiple choice examples into a string"""
        formatted = "Here are some example multiple choice exercises:\n\n"
        for ex in examples:
            formatted += f"Content: {ex.get('content', '')}\n"
            for q in ex.get('questions', []):
                formatted += f"Question: {q.get('question', '')}\n"
                for opt in q.get('options', []):
                    formatted += f"- {opt}\n"
                formatted += f"Correct answer: {q.get('correct_answer', '')}\n\n"
        return formatted

    def _format_dialog_matching_examples(self, examples: List[Dict]) -> str:
        """Format dialog matching examples into a string"""
        formatted = "Here are some example dialog matching exercises:\n\n"
        for ex in examples:
            formatted += "Dialogs:\n"
            for dialog in ex.get('dialogs', []):
                formatted += f"- {dialog}\n"
            formatted += "\nImages:\n"
            for image in ex.get('images', []):
                formatted += f"- {image}\n"
            formatted += "\nCorrect matches:\n"
            for dialog, image in ex.get('correct_matches', {}).items():
                formatted += f"Dialog: {dialog}\n"
                formatted += f"Matches with: {image}\n\n"
        return formatted

    def generate_multiple_choice(self, topic: str) -> Dict:
        """Generate a new multiple choice exercise"""
        examples = self._get_example_exercises("multiple_choice", topic)
        examples_text = self._format_multiple_choice_examples(examples)
        
        prompt = f"""Based on these example exercises:

{examples_text}
Generate a new multiple choice exercise about {topic}. 
Use the same format as the examples, with Content, Questions, Options, and Correct answers.
Please generate exactly 4 questions.
Make sure the exercise is educational and the correct answers are clearly indicated.
The content should be a complete text with proper punctuation, using periods (.) at the end of sentences."""

        print("\nMultiple Choice Prompt:")
        print("=" * 80)
        print(prompt)
        print("=" * 80)
        
        conversation = [
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ]
        
        response = self.bedrock.converse(
            modelId="amazon.nova-micro-v1:0",
            messages=conversation,
            inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
        )
        
        print("\nRaw response:")
        print(json.dumps(response, indent=2))  # Pretty print the response

        response_text = response['output']['message']['content'][0]['text']
        print("\nGenerated Exercise:")
        print("=" * 80)
        print(response_text)
        print("=" * 80)
               
        return self._parse_multiple_choice_response(response_text)

    def generate_dialog_matching(self, topic: str) -> Dict:
        """Generate a new dialog matching exercise"""
        examples = self._get_example_exercises("dialog_matching", topic)
        examples_text = self._format_dialog_matching_examples(examples)
        
        prompt = f"""Based on these example exercises:

{examples_text}
Generate a new dialog matching exercise about {topic}.
Use the same format as the examples, with Dialogs, Images, and Correct matches.
Please generate exactly 5 dialogs.
The content should be a complete text with proper punctuation, using periods (.) at the end of sentences.
Make sure the dialogs and images are related and the matches make logical sense."""

        print("\nDialog Matching Prompt:")
        print("=" * 80)
        print(prompt)
        print("=" * 80)
        
        conversation = [
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ]
        
        response = self.bedrock.converse(
            modelId="amazon.nova-micro-v1:0",
            messages=conversation,
            inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
        )
        
        print("\nRaw response:")
        print(json.dumps(response, indent=2))  # Pretty print the response

        response_text = response['output']['message']['content'][0]['text']
        print("\nGenerated Exercise:")
        print("=" * 80)
        print(response_text)
        print("=" * 80)
            
        return self._parse_dialog_matching_response(response_text)

    def _parse_multiple_choice_response(self, content: str) -> Dict:
        """Parse the generated multiple choice response into structured format"""
        exercise = {'content': '', 'questions': []}
        current_question = None
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('Content:'):
                exercise['content'] = line.replace('Content:', '').strip()
            elif line.startswith('Question:'):
                if current_question:
                    exercise['questions'].append(current_question)
                current_question = {
                    'question': line.replace('Question:', '').strip(),
                    'options': [],
                    'correct_answer': None
                }
            elif line.startswith('- '):
                if current_question:
                    current_question['options'].append(line.replace('- ', '').strip())
            elif line.startswith('Correct answer:'):
                if current_question:
                    current_question['correct_answer'] = line.replace('Correct answer:', '').strip()
                    exercise['questions'].append(current_question)
                    current_question = None
                    
        return exercise

    def _parse_dialog_matching_response(self, content: str) -> Dict:
        """Parse the generated dialog matching response into structured format"""
        exercise = {'dialogs': [], 'images': [], 'correct_matches': {}}
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line == 'Dialogs:':
                current_section = 'dialogs'
            elif line == 'Images:':
                current_section = 'images'
            elif line == 'Correct matches:':
                current_section = 'matches'
            elif line.startswith('- '):
                item = line.replace('- ', '').strip()
                if current_section == 'dialogs':
                    exercise['dialogs'].append(item)
                elif current_section == 'images':
                    exercise['images'].append(item)
            elif line.startswith('Dialog:'):
                dialog = line.replace('Dialog:', '').strip()
            elif line.startswith('Matches with:'):
                image = line.replace('Matches with:', '').strip()
                exercise['correct_matches'][dialog] = image
                
        return exercise

if __name__ == "__main__":
    # Example usage
    generator = ExercisesGenerator()
    
    # Generate a multiple choice exercise
    #print("\nGenerating multiple choice exercise about ordering food:")
    #mc_exercise = generator.generate_multiple_choice("ordering food at a restaurant")
    #print(json.dumps(mc_exercise, indent=2))
    
    # Generate a dialog matching exercise
    print("\nGenerating dialog matching exercise about train travel:")
    dm_exercise = generator.generate_dialog_matching("taking the train")
    print(json.dumps(dm_exercise, indent=2)) 
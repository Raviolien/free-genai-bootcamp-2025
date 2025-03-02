from audio_generator import AudioGenerator
from exercise_generator import ExercisesGenerator
import json
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

def create_restaurant_mc_exercise():
    try:
        # Initialize generators with error handling
        try:
            exercise_gen = ExercisesGenerator()
        except ClientError as e:
            print(f"Error initializing AWS Bedrock: {str(e)}")
            raise
        except Exception as e:
            print(f"Error initializing exercise generator: {str(e)}")
            raise

        audio_gen = AudioGenerator()

        # Generate exercise content
        exercise = exercise_gen.generate_multiple_choice(
            topic="ordering food at a restaurant"
        )

        # Validate exercise format
        if not exercise or 'content' not in exercise:
            raise ValueError("Generated exercise is missing required content")

        # Generate audio for the content
        audio_files = audio_gen.generate_audio(
            exercise_id="restaurant_mc",
            content={"content": exercise["content"]}
        )

        # Add audio file path to exercise
        exercise["audio"] = audio_files["content"]

        # Save exercise to JSON file
        output_dir = Path(__file__).parent / "data" / "exercises" / "restaurant_mc"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "exercise.json", "w", encoding="utf-8") as f:
            json.dump(exercise, f, ensure_ascii=False, indent=2)
            
        print(f"Exercise created successfully!")
        print(f"Audio file: {audio_files['content']}")
        print(f"Exercise file: {output_dir / 'exercise.json'}")

    except Exception as e:
        print(f"Error creating exercise: {str(e)}")
        raise

if __name__ == "__main__":
    create_restaurant_mc_exercise() 
import boto3
from pathlib import Path
import json
from typing import Dict, List

class AudioGenerator:
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the audio generator with AWS Polly client"""
        self.polly = boto3.client('polly', region_name=region_name)
        self.audio_dir = Path(__file__).parent / "data" / "audio"
        self.audio_dir.parent.mkdir(exist_ok=True)
        self.audio_dir.mkdir(exist_ok=True)

    def generate_audio(self, exercise_id: str, content: Dict) -> Dict[str, str]:
        """
        Generate audio files for exercise content and dialogs
        
        Args:
            exercise_id: Unique identifier for the exercise
            content: Dictionary containing exercise content and dialogs
            
        Returns:
            Dict mapping content type to audio file paths
        """
        audio_files = {}
        
        # Generate audio for main content if present
        if 'content' in content:
            audio_path = self._generate_speech(
                text=content['content'],
                filename=f"{exercise_id}_content.mp3"
            )
            audio_files['content'] = str(audio_path)

        # Generate audio for each dialog if present
        if 'dialogs' in content:
            dialog_paths = []
            for i, dialog in enumerate(content['dialogs']):
                audio_path = self._generate_speech(
                    text=dialog,
                    filename=f"{exercise_id}_dialog_{i+1}.mp3"
                )
                dialog_paths.append(str(audio_path))
            audio_files['dialogs'] = dialog_paths

        return audio_files

    def _generate_speech(self, text: str, filename: str) -> Path:
        """
        Generate speech from text using Amazon Polly
        
        Args:
            text: Text to convert to speech
            filename: Name for the output audio file
            
        Returns:
            Path to generated audio file
        """
        try:
            response = self.polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId='Lea',  # French female voice
                LanguageCode='fr-FR',
                Engine='neural'
            )

            audio_path = self.audio_dir / filename
            
            # Save the audio stream to file
            if "AudioStream" in response:
                with open(audio_path, 'wb') as f:
                    f.write(response['AudioStream'].read())
                    
            return audio_path

        except Exception as e:
            print(f"Error generating audio for {filename}: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    generator = AudioGenerator()
    
    # Example multiple choice exercise content (first content block from file)
    exercise_multiple_choice = {
        "content": "Bonjour, je m'appelle Aurélien et j'ai 25 ans. Je travaille dans un laboratoire et j'habite dans une maison à Nantes. Mon plat préféré est le cordon bleu. J'ai un chien qui s'appelle Hubert et je suis célibataire."
    }
    
    # Example dialog matching exercise content (from dialog matching file)
    exercise_dialog_matching = {
        "dialogs": [
            "c'est bientôt l'anniversaire de Sophie ah oui elle est née quel jour le 18 juillet",
            "combien coûte un kilo de pommes s'il vous plaît 2 € le kilo et 5 euros les trois",
            "bonjour une table pour deux s'il vous plaît",
            "pour aller à la gare s'il vous plaît vous devez prendre le bus 71 c'est là-bas au bout de la rue",
            "il joue vraiment bien ces musiciens oui ils sont doués mais je n'aime pas trop la musique classique"
        ]
    }
    
    try:
        # Generate audio for multiple choice exercise
        mc_audio_files = generator.generate_audio("r6RbPc55SAI_mc", exercise_multiple_choice)
        print("\nGenerated multiple choice audio files:")
        print(json.dumps(mc_audio_files, indent=2))
        
        # Generate audio for dialog matching exercise
        dm_audio_files = generator.generate_audio("r6RbPc55SAI_dm", exercise_dialog_matching)
        print("\nGenerated dialog matching audio files:")
        print(json.dumps(dm_audio_files, indent=2))
        
    except Exception as e:
        print(f"Error: {e}") 
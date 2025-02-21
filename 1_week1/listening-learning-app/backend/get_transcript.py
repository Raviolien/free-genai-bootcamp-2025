from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import os
import json
from pathlib import Path

# Define transcripts directory path
TRANSCRIPTS_DIR = Path(__file__).parent / "transcripts"

def extract_video_id(url: str) -> str:
    """
    Extract the video ID from a YouTube URL.
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: YouTube video ID
        
    Raises:
        ValueError: If the URL is invalid or video ID cannot be extracted
    """
    try:
        # Handle different URL formats
        parsed_url = urlparse(url)
        
        if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
            return parsed_url.path[1:]
        
        if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
            elif parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2]
            elif parsed_url.path.startswith('/v/'):
                return parsed_url.path.split('/')[2]
    
        raise ValueError("Could not extract video ID from URL")
    except Exception as e:
        raise ValueError(f"Invalid YouTube URL: {str(e)}")

def get_transcript(url: str, save: bool = True) -> list:
    """
    Get the French transcript from a YouTube video URL and optionally save it to a file.
    
    Args:
        url (str): YouTube video URL
        save (bool): Whether to save the transcript to a file (default: True)
        
    Returns:
        list: List of dictionaries containing transcript segments with 'text', 'start' and 'duration' keys
        
    Raises:
        ValueError: If transcript cannot be retrieved or URL is invalid
        FileNotFoundError: If transcripts directory doesn't exist when trying to save
    """
    try:
        video_id = extract_video_id(url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['fr'])
        
        if save:
            if not TRANSCRIPTS_DIR.exists():
                raise FileNotFoundError("Transcripts directory does not exist. Please create the 'backend/transcripts' directory.")
            save_transcript(video_id, transcript)
            
        return transcript
    except Exception as e:
        raise ValueError(f"Could not get French transcript: {str(e)}")

def save_transcript(video_id: str, transcript: list) -> None:
    """
    Save transcript text to a file in the transcripts directory.
    
    Args:
        video_id (str): YouTube video ID
        transcript (list): List of transcript segments
    """
    # Create transcript file path
    file_path = TRANSCRIPTS_DIR / f"{video_id}.txt"
    
    # Join all transcript text segments
    full_text = "\n".join(entry['text'] for entry in transcript)
    
    # Save to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

if __name__ == "__main__":
    # Example usage
    test_url = "https://www.youtube.com/watch?v=r6RbPc55SAI"
    try:        
        transcript = get_transcript(test_url, save=True)
        print(f"Transcript saved successfully to {TRANSCRIPTS_DIR}")
        print("\nFirst 5 entries:")
        for entry in transcript[:5]:
            print(entry)
    except ValueError as e:
        print(f"Error: {e}") 
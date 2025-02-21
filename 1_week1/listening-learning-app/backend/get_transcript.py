from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

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

def get_transcript(url: str) -> list:
    """
    Get the transcript from a YouTube video URL.
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        list: List of dictionaries containing transcript segments with 'text', 'start' and 'duration' keys
        
    Raises:
        ValueError: If transcript cannot be retrieved or URL is invalid
    """
    try:
        video_id = extract_video_id(url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        raise ValueError(f"Could not get transcript: {str(e)}")

if __name__ == "__main__":
    # Example usage
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    try:
        transcript = get_transcript(test_url)
        for entry in transcript[:5]:  # Print first 5 entries
            print(entry)
    except ValueError as e:
        print(f"Error: {e}") 
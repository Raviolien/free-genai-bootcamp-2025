from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from pathlib import Path

class YoutubeTranscriptDownloader:
    def __init__(self, transcripts_dir: str = "transcripts", language: str = "fr"):
        """
        Initialize the downloader with a directory and language setting.
        
        Args:
            transcripts_dir (str): Name of directory for saving transcripts
            language (str): Language code for transcripts (default: "fr")
        """
        self.transcripts_dir = Path(__file__).parent / transcripts_dir
        self.language = language
        self.current_video_id = None
        self.current_transcript = None

    def get_transcript(self, url: str) -> list:
        """
        Get the transcript from a YouTube video URL.
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            list: List of dictionaries containing transcript segments
            
        Raises:
            ValueError: If transcript cannot be retrieved or URL is invalid
        """
        try:
            self.current_video_id = self._extract_video_id(url)
            self.current_transcript = YouTubeTranscriptApi.get_transcript(
                self.current_video_id, 
                languages=[self.language]
            )
            return self.current_transcript
        except Exception as e:
            raise ValueError(f"Could not get transcript in {self.language}: {str(e)}")

    def save_transcript(self) -> None:
        """
        Save the last retrieved transcript to a file.
        
        Raises:
            ValueError: If no transcript has been retrieved yet
            FileNotFoundError: If transcripts directory doesn't exist
        """
        if not self.current_transcript or not self.current_video_id:
            raise ValueError("No transcript has been retrieved yet")
            
        if not self.transcripts_dir.exists():
            raise FileNotFoundError(f"Directory {self.transcripts_dir} does not exist")
            
        file_path = self.transcripts_dir / f"{self.current_video_id}.txt"
        full_text = "\n".join(entry['text'] for entry in self.current_transcript)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

    def _extract_video_id(self, url: str) -> str:
        """
        Extract the video ID from a YouTube URL.
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            str: YouTube video ID
            
        Raises:
            ValueError: If URL is invalid or video ID cannot be extracted
        """
        try:
            parsed_url = urlparse(url)
            
            if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
                return parsed_url.path[1:]
            
            if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
                if parsed_url.path == '/watch':
                    return parse_qs(parsed_url.query)['v'][0]
                elif parsed_url.path.startswith(('/embed/', '/v/')):
                    return parsed_url.path.split('/')[2]
        
            raise ValueError("Could not extract video ID from URL")
        except Exception as e:
            raise ValueError(f"Invalid YouTube URL: {str(e)}")

if __name__ == "__main__":
    # Example usage
    test_url = "https://www.youtube.com/watch?v=1w3EwRGpubQ&list=PL_Ddcj9mdkpWyWueYp32n4aH83du-9Adv&index=4"
    test_url = "https://www.youtube.com/watch?v=4TvCjKswqDs&list=PL_Ddcj9mdkpWyWueYp32n4aH83du-9Adv&index=5"
    test_url = "https://www.youtube.com/watch?v=r6RbPc55SAI"
    
    try:
        # Create transcripts directory
        Path(__file__).parent.joinpath("transcripts").mkdir(exist_ok=True)
        
        # Initialize downloader and get transcript
        downloader = YoutubeTranscriptDownloader()
        transcript = downloader.get_transcript(test_url)
        downloader.save_transcript()
        
        print(f"Transcript saved successfully to {downloader.transcripts_dir}")
        print("\nFirst 5 entries:")
        for entry in transcript[:5]:
            print(entry)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}") 
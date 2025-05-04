import unittest
import sys
import os

# Add the src directory to the path so we can import modules from it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.utils.platform_utils import detect_platform, get_platform_qualities 
from src.main import Worker

class StreamlinkTest(unittest.TestCase):
    """Tests for streamlink integration"""
    
    def test_platform_detection(self):
        """Test that platforms are correctly detected from URLs"""
        # Test Twitch detection
        self.assertEqual(detect_platform("https://www.twitch.tv/example"), "twitch")
        self.assertEqual(detect_platform("https://twitch.tv/videos/12345"), "twitch")
        
        # Test YouTube detection
        self.assertEqual(detect_platform("https://www.youtube.com/watch?v=abcdefg"), "youtube")
        self.assertEqual(detect_platform("https://youtu.be/abcdefg"), "youtube")
        
        # Test unknown platforms
        self.assertEqual(detect_platform("https://example.com"), "unknown")
    
    def test_platform_qualities(self):
        """Test that platforms have appropriate quality options"""
        # Twitch quality options
        twitch_qualities = get_platform_qualities("twitch")
        self.assertIn("best", twitch_qualities)
        self.assertIn("720p", twitch_qualities)
        self.assertIn("audio_only", twitch_qualities)
        
        # YouTube quality options
        youtube_qualities = get_platform_qualities("youtube")
        self.assertIn("best", youtube_qualities)
        self.assertIn("1080p", youtube_qualities)
        self.assertIn("144p", youtube_qualities)
    
    def test_worker_command_building(self):
        """Test that Worker uses the appropriate downloader based on platform"""
        # Create a test Worker for Twitch
        twitch_worker = Worker(
            stream_url="https://www.twitch.tv/example",
            quality="best",
            output_path="./downloads",
            options={"live_from_start": True}
        )
        
        twitch_command = twitch_worker.build_command()
        
        # The first element should be "streamlink" for Twitch URLs
        self.assertEqual(twitch_command[0], "streamlink")
        
        # Create a test Worker for YouTube
        youtube_worker = Worker(
            stream_url="https://www.youtube.com/watch?v=abcdefg",
            quality="best",
            output_path="./downloads",
            options={"live_from_start": True}
        )
        
        youtube_command = youtube_worker.build_command()
        
        # The first elements should be "python -m yt_dlp" for YouTube URLs
        self.assertEqual(youtube_command[0], "python")
        self.assertEqual(youtube_command[1], "-m")
        self.assertEqual(youtube_command[2], "yt_dlp")

if __name__ == "__main__":
    unittest.main()

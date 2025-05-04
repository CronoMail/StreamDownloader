"""
Platform detection utility for Stream Downloader
"""
import re

def detect_platform(url):
    """
    Detect the streaming platform from a URL
    
    Args:
        url (str): The URL to analyze
        
    Returns:
        str: Platform name - "twitch", "youtube", or "unknown"
    """
    if not url:
        return "unknown"
        
    # Check for Twitch URLs
    if "twitch.tv" in url:
        return "twitch"
    
    # Check for YouTube URLs
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    
    # Unknown platform
    else:
        return "unknown"

def get_platform_qualities(platform):
    """
    Get available quality options for a specific platform
    
    Args:
        platform (str): The platform name ("twitch", "youtube")
        
    Returns:
        list: List of quality options
    """
    if platform == "twitch":
        return [
            "best",
            "1080p60",
            "1080p",
            "720p60",
            "720p",
            "480p",
            "360p",
            "160p",
            "audio_only"
        ]
    elif platform == "youtube":
        return [
            "best",
            "1080p",
            "720p",
            "480p",
            "360p",
            "240p",
            "144p",
            "audio"
        ]
    else:
        return ["best"]

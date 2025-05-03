import sys
import os
import argparse
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

# Import required modules from the existing application
from src.stream_downloader import StreamDownloader
from src.stream_merger import process_stream_download
from src.history_manager import HistoryManager
from src.updater import get_current_version, check_for_updates

def print_banner():
    """Print the application banner"""
    version = get_current_version()
    print("=" * 60)
    print(f"Stream Downloader CLI v{version}")
    print("A tool for downloading Twitch and YouTube livestreams")
    print("=" * 60)
    print("")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import requests
        import yt_dlp
    except ImportError as e:
        print(f"Error: Missing dependency - {str(e)}")
        print("Please install required dependencies with:")
        print("pip install -r requirements.txt")
        return False
    return True

def detect_platform(url):
    """Detect platform from URL"""
    if "twitch.tv" in url:
        return "twitch"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    else:
        return "unknown"

def download_with_yt_dlp(args):
    """Download content using yt-dlp"""
    command = ["yt-dlp"]
    
    # Add URL
    command.append(args.url)
    
    # Quality options
    if args.quality and args.quality != "best":
        command.extend(["-f", args.quality])
    
    # Output template
    output_path = args.output
    if not os.path.isabs(output_path):
        output_path = os.path.join(os.getcwd(), output_path)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Build output template
    if args.template:
        output_template = args.template
    else:
        output_template = "%(title)s-%(id)s.%(ext)s"
    
    command.extend(["-o", os.path.join(os.path.dirname(output_path), output_template)])
    
    # Live options
    if args.live:
        command.append("--live-from-start")
    
    # Cookies file
    if args.cookies:
        command.extend(["--cookies", args.cookies])
    
    # Other options
    if args.thumbnail:
        command.append("--write-thumbnail")
    if args.metadata:
        command.append("--add-metadata")
    if args.keep_fragments:
        command.append("--keep-fragments")
    if args.verbose:
        command.append("-v")
    
    print(f"Running command: {' '.join(command)}")
    
    # Record start time
    start_time = time.time()
    
    # Execute the download command
    try:
        result = subprocess.run(command, check=True)
        
        duration = time.time() - start_time
        print(f"\nDownload completed in {duration:.2f} seconds")
        
        # Save to history if enabled
        if not args.no_history:
            save_to_history(args, True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError: Download failed with exit code {e.returncode}")
        
        # Save failed download to history if enabled
        if not args.no_history:
            save_to_history(args, False, error=str(e))
        
        return False

def save_to_history(args, success, error=None):
    """Save download information to history"""
    try:
        history_manager = HistoryManager()
        
        download_info = {
            "url": args.url,
            "platform": detect_platform(args.url),
            "quality": args.quality,
            "output_path": os.path.abspath(args.output),
            "timestamp": datetime.now().isoformat(),
            "success": success
        }
        
        if error:
            download_info["error_message"] = error
        
        history_manager.add_download(download_info)
        print(f"Download {'success' if success else 'failure'} saved to history")
    except Exception as e:
        print(f"Warning: Failed to save to history - {str(e)}")

def print_history(count=None, platform=None):
    """Print download history"""
    try:
        history_manager = HistoryManager()
        downloads = history_manager.get_downloads(count, platform)
        
        if not downloads:
            print("No download history found")
            return
        
        print("\nDownload History:")
        print("-" * 80)
        
        for i, download in enumerate(downloads):
            # Format timestamp
            timestamp = download.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                timestamp = "Unknown date"
            
            platform = download.get("platform", "Unknown")
            url = download.get("url", "Unknown URL")
            quality = download.get("quality", "Unknown")
            success = "✓" if download.get("success", False) else "✗"
            
            print(f"{i+1}. [{success}] {timestamp} - {platform}: {url} ({quality})")
        
        print("-" * 80)
    except Exception as e:
        print(f"Error accessing history: {str(e)}")

def clear_history():
    """Clear download history"""
    try:
        history_manager = HistoryManager()
        history_manager.clear_history()
        print("Download history cleared successfully")
    except Exception as e:
        print(f"Error clearing history: {str(e)}")

def check_for_app_updates():
    """Check for application updates"""
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    print("Checking for updates...")
    
    try:
        update_info = check_for_updates(current_version)
        
        if update_info['update_available']:
            print(f"New version available: {update_info['latest_version']}")
            print(f"Release URL: {update_info['release_url']}")
            if update_info['release_notes']:
                print("\nRelease Notes:")
                print(update_info['release_notes'])
        else:
            print("You are using the latest version.")
    except Exception as e:
        print(f"Error checking for updates: {str(e)}")

def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(description="Stream Downloader CLI")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download a stream")
    download_parser.add_argument("url", help="URL of the stream to download")
    download_parser.add_argument("-o", "--output", default=".", help="Output directory or file path")
    download_parser.add_argument("-q", "--quality", default="best", help="Video quality to download")
    download_parser.add_argument("-t", "--template", help="Output filename template")
    download_parser.add_argument("--live", action="store_true", help="Download live stream from start")
    download_parser.add_argument("--thumbnail", action="store_true", help="Save thumbnail")
    download_parser.add_argument("--metadata", action="store_true", help="Add metadata")
    download_parser.add_argument("--keep-fragments", action="store_true", help="Keep fragments after merging")
    download_parser.add_argument("--cookies", help="Path to cookies file for members-only content")
    download_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    download_parser.add_argument("--no-history", action="store_true", help="Don't save to download history")
    
    # History command
    history_parser = subparsers.add_parser("history", help="Manage download history")
    history_parser.add_argument("--count", type=int, help="Number of history items to show")
    history_parser.add_argument("--platform", choices=["youtube", "twitch"], help="Filter by platform")
    history_parser.add_argument("--clear", action="store_true", help="Clear download history")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Check for application updates")
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check if dependencies are installed
    if not check_dependencies():
        return
    
    # Execute the selected command
    if args.command == "download":
        download_with_yt_dlp(args)
    
    elif args.command == "history":
        if args.clear:
            clear_history()
        else:
            print_history(args.count, args.platform)
    
    elif args.command == "update":
        check_for_app_updates()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
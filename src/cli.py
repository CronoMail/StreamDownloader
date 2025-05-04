import sys
import os
import argparse
import subprocess
import time
import json
import shutil
import threading
from datetime import datetime
from pathlib import Path
import inquirer
from colorama import init, Fore, Style, Back

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Import required modules from the existing application
from src.stream_downloader import StreamDownloader
from src.stream_merger import process_stream_download
from src.history_manager import HistoryManager
from src.updater import get_current_version, check_for_updates
from src.spinner import Spinner
from src.cli_help import get_main_help, get_command_help

def print_banner():
    """Print the application banner"""
    version = get_current_version()
    
    # Get terminal width for centered text
    terminal_width = shutil.get_terminal_size().columns
    
    # ASCII Art Banner
    banner = [
        "╔═══════════════════════════════════════════════════════════════╗",
        "║                                                               ║",
        "║   ███████╗████████╗██████╗ ███████╗ █████╗ ███╗   ███╗       ║",
        "║   ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗████╗ ████║       ║",
        "║   ███████╗   ██║   ██████╔╝█████╗  ███████║██╔████╔██║       ║",
        "║   ╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║       ║",
        "║   ███████║   ██║   ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║       ║",
        "║   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝       ║",
        "║                                                               ║",
        "║   ██████╗  ██████╗ ██╗    ██╗███╗   ██╗██╗      ██████╗  █████╗ ██████╗ ███████╗██████╗  ║",
        "║   ██╔══██╗██╔═══██╗██║    ██║████╗  ██║██║     ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗ ║",
        "║   ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║██║     ██║   ██║███████║██║  ██║█████╗  ██████╔╝ ║",
        "║   ██║  ██║██║   ██║██║███╗██║██║╚██╗██║██║     ██║   ██║██╔══██║██║  ██║██╔══╝  ██╔══██╗ ║",
        "║   ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║███████╗╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║ ║",
        "║   ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝ ║",
        "║                                                               ║",
        f"╚═══════════════════ v{version} ═════════════════════╝"
    ]
    
    print()
    for line in banner:
        print(Fore.CYAN + line.center(terminal_width))
        
    print(f"\n{Fore.YELLOW}A powerful tool for downloading Twitch and YouTube livestreams\n".center(terminal_width))
    print(Style.RESET_ALL)

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

def fetch_available_formats(url):
    """Fetch available formats for a URL using yt-dlp"""
    print(f"{Fore.YELLOW}Fetching available formats for {url}...")
    
    try:
        with Spinner(message=f"{Fore.YELLOW}Analyzing stream...", color=Fore.CYAN) as spinner:
            list_command = ["yt-dlp", "--list-formats", url]
            result = subprocess.run(list_command, capture_output=True, text=True)
            
            spinner.update_message(f"{Fore.YELLOW}Processing format information...")
            
            if result.returncode == 0:
                formats = []
                for line in result.stdout.split('\n'):
                    # Parse format lines
                    if line.strip() and 'format code' not in line and '---' not in line:
                        if any(res in line for res in ['1080', '720', '480', '360', '240', '144']):
                            formats.append(line.strip())
                return formats
            else:
                print(f"{Fore.RED}Error retrieving formats: {result.stderr}")
                return None
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}")
        return None
    
    return None

def download_with_yt_dlp(args):
    """Download content using yt-dlp with progress display"""
    # Check if we need to list formats first
    if hasattr(args, 'list_formats') and args.list_formats:
        list_command = ["yt-dlp", "--list-formats", args.url]
        print(f"{Fore.GREEN}Fetching available formats: {Fore.WHITE}{' '.join(list_command)}")
        
        try:
            result = subprocess.run(list_command, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"\n{Fore.CYAN}Available formats for {args.url}:")
                print(f"{Fore.WHITE}{result.stdout}")
                
                # Ask if user wants to continue with download
                continue_download = input(f"{Fore.YELLOW}Continue with download? (Y/n): ").strip().lower()
                if continue_download and continue_download[0] == 'n':
                    print(f"{Fore.YELLOW}Download canceled.")
                    return False
            else:
                print(f"{Fore.RED}Error retrieving formats: {result.stderr}")
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}")
    
    command = ["yt-dlp"]
    
    # Add URL
    command.append(args.url)
    
    # Quality options with fallback for specific resolutions
    if hasattr(args, 'quality') and args.quality and args.quality != "best":
        if hasattr(args, 'use_fallback') and args.use_fallback:
            # Create a format string with fallbacks for common resolutions
            if args.quality.startswith("1080"):
                format_str = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/720p/best"
            elif args.quality.startswith("720"):
                format_str = "bestvideo[height<=720]+bestaudio/best[height<=720]/480p/best"
            elif args.quality.startswith("480"):
                format_str = "bestvideo[height<=480]+bestaudio/best[height<=480]/360p/best"
            else:
                format_str = args.quality
            command.extend(["-f", format_str])
        else:
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
    if hasattr(args, 'template') and args.template:
        output_template = args.template
    else:
        output_template = "%(title)s-%(id)s.%(ext)s"
    
    command.extend(["-o", os.path.join(os.path.dirname(output_path), output_template)])
    
    # Live options
    if hasattr(args, 'live') and args.live:
        command.append("--live-from-start")
    
    # Cookies file
    if hasattr(args, 'cookies') and args.cookies:
        command.extend(["--cookies", args.cookies])
    
    # Other options
    if hasattr(args, 'thumbnail') and args.thumbnail:
        command.append("--write-thumbnail")
    if hasattr(args, 'metadata') and args.metadata:
        command.append("--add-metadata")
    if hasattr(args, 'keep_fragments') and args.keep_fragments:
        command.append("--keep-fragments")
    if hasattr(args, 'verbose') and args.verbose:
        command.append("-v")
    
    # New options
    if hasattr(args, 'proxy') and args.proxy:
        command.extend(["--proxy", args.proxy])
    if hasattr(args, 'retries') and args.retries is not None:
        command.extend(["--retries", str(args.retries)])
    if hasattr(args, 'timeout') and args.timeout is not None:
        command.extend(["--socket-timeout", str(args.timeout)])
    if hasattr(args, 'quiet') and args.quiet:
        command.append("--quiet")
    if hasattr(args, 'abort_on_error') and args.abort_on_error:
        command.append("--abort-on-error")
    
    # Add progress visualization
    command.append("--progress")
    
    print(f"{Fore.GREEN}Running command: {Fore.WHITE}{' '.join(command)}")
    
    # Record start time
    start_time = time.time()
    
    # Create spinner animation
    spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    spinner_idx = 0
    
    # Execute the download command
    try:
        # Use Popen to capture output in real-time
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Keep track of the last lines for status display
        last_status = ""
        has_error = False
        while process.poll() is None:
            line = process.stdout.readline()
            if line:
                # Clear previous line and print current status with spinner
                if "[download]" in line or "[ffmpeg]" in line:
                    # Extract download percentage if available
                    if "%" in line:
                        last_status = line.strip()
                        spinner_char = spinner_chars[spinner_idx % len(spinner_chars)]
                        print(f"\r{Fore.CYAN}{spinner_char} {Fore.YELLOW}{last_status}", end='')
                        spinner_idx += 1
                    else:
                        print(f"\r{Fore.YELLOW}{line.strip()}", end='')
                elif "ERROR:" in line:
                    has_error = True
                    print(f"\n{Fore.RED}{line.strip()}")
                else:
                    print(f"{Fore.WHITE}{line.strip()}")
            time.sleep(0.1)
        
        # Make sure we print a newline after progress
        print()
        
        # Check if the process completed successfully
        if process.returncode == 0:
            duration = time.time() - start_time
            print(f"\n{Fore.GREEN}Download completed in {duration:.2f} seconds")
            
            # Save to history if enabled
            if not hasattr(args, 'no_history') or not args.no_history:
                save_to_history(args, True)
            
            return True
        else:
            error_message = f"Exit code {process.returncode}"
            
            # Check if this is a format error and suggest solutions
            if "Requested format is not available" in last_status:
                print(f"\n{Fore.RED}Error: The requested quality ({args.quality}) is not available for this stream.")
                print(f"{Fore.YELLOW}Suggestions:")
                print(f"{Fore.WHITE}1. Use '--list-formats' to see all available formats")
                print(f"{Fore.WHITE}2. Try using 'best' quality instead of a specific resolution")
                print(f"{Fore.WHITE}3. Use the fallback option ('--use-fallback') to automatically try lower qualities")
                
                # Ask if the user wants to retry with 'best' quality
                if not hasattr(args, 'no_interactive') or not args.no_interactive:
                    retry = input(f"\n{Fore.YELLOW}Retry download with 'best' quality? (Y/n): ").strip().lower()
                    if not retry or retry[0] != 'n':
                        print(f"{Fore.GREEN}Retrying with best quality...")
                        args.quality = "best"
                        return download_with_yt_dlp(args)
                
                error_message = f"Requested quality ({args.quality}) not available"
            
            print(f"\n{Fore.RED}Error: Download failed with exit code {process.returncode}")
            
            # Save failed download to history if enabled
            if not hasattr(args, 'no_history') or not args.no_history:
                save_to_history(args, False, error=error_message)
            
            # Try to mux any fragments that were already downloaded
            output_dir = os.path.dirname(os.path.abspath(args.output))
            fragments_dir = None
            
            # Check for fragments in the output directory
            for subdir in os.listdir(output_dir):
                if os.path.isdir(os.path.join(output_dir, subdir)) and subdir.startswith("NA_"):
                    potential_fragments_dir = os.path.join(output_dir, subdir)
                    if any(f.endswith(".ts") for f in os.listdir(potential_fragments_dir)):
                        fragments_dir = potential_fragments_dir
                        break
            
            # If fragments directory is found, try to mux the fragments
            if fragments_dir:
                print(f"{Fore.CYAN}Found partially downloaded fragments. Attempting to mux available content...")
                
                # Define output file path (using the fragments directory name as a base)
                output_filename = f"{os.path.basename(fragments_dir)}_partial.mp4"
                output_file = os.path.join(output_dir, output_filename)
                
                # Prepare options for processing
                options = {
                    "keep_fragments": hasattr(args, 'keep_fragments') and args.keep_fragments,
                    "metadata": {
                        "title": f"Partial download - {os.path.basename(fragments_dir)}",
                        "comment": "This is a partial download that encountered an error."
                    }
                }
                
                # Process the downloaded fragments
                try:
                    if process_stream_download(fragments_dir, output_file, options):
                        print(f"{Fore.GREEN}Successfully merged available fragments: {output_file}")
                    else:
                        print(f"{Fore.RED}Failed to merge fragments. The download was too short or fragments are corrupted.")
                except Exception as merge_error:
                    print(f"{Fore.RED}Error merging fragments: {str(merge_error)}")
            
            return False
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Download cancelled by user.")
        
        # Try to mux any fragments that were already downloaded
        output_dir = os.path.dirname(os.path.abspath(args.output))
        fragments_dir = None
        
        # Check for fragments in the output directory
        for subdir in os.listdir(output_dir):
            if os.path.isdir(os.path.join(output_dir, subdir)) and subdir.startswith("NA_"):
                potential_fragments_dir = os.path.join(output_dir, subdir)
                if any(f.endswith(".ts") for f in os.listdir(potential_fragments_dir)):
                    fragments_dir = potential_fragments_dir
                    break
        
        # If fragments directory is found, try to mux the fragments
        if fragments_dir:
            print(f"{Fore.CYAN}Found partially downloaded fragments. Attempting to mux available content...")
            
            # Define output file path (using the fragments directory name as a base)
            output_filename = f"{os.path.basename(fragments_dir)}_partial.mp4"
            output_file = os.path.join(output_dir, output_filename)
            
            # Prepare options for processing
            options = {
                "keep_fragments": hasattr(args, 'keep_fragments') and args.keep_fragments,
                "metadata": {
                    "title": f"Partial download - {os.path.basename(fragments_dir)}",
                    "comment": "This is a partial download that was cancelled by the user."
                }
            }
            
            # Process the downloaded fragments
            try:
                if process_stream_download(fragments_dir, output_file, options):
                    print(f"{Fore.GREEN}Successfully merged available fragments: {output_file}")
                else:
                    print(f"{Fore.RED}Failed to merge fragments. The download was too short or fragments are corrupted.")
            except Exception as merge_error:
                print(f"{Fore.RED}Error merging fragments: {str(merge_error)}")
        else:
            print(f"{Fore.YELLOW}No downloaded fragments found to merge.")
        
        # Save to history as canceled
        if not hasattr(args, 'no_history') or not args.no_history:
            save_to_history(args, False, error="Cancelled by user")
        
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"\n{Fore.RED}Error: Download failed with exit code {e.returncode}")
        
        # Save failed download to history if enabled
        if not hasattr(args, 'no_history') or not args.no_history:
            save_to_history(args, False, error=str(e))
        
        # Try to mux any fragments that were already downloaded
        output_dir = os.path.dirname(os.path.abspath(args.output))
        fragments_dir = None
        
        # Check for fragments in the output directory
        for subdir in os.listdir(output_dir):
            if os.path.isdir(os.path.join(output_dir, subdir)) and subdir.startswith("NA_"):
                potential_fragments_dir = os.path.join(output_dir, subdir)
                if any(f.endswith(".ts") for f in os.listdir(potential_fragments_dir)):
                    fragments_dir = potential_fragments_dir
                    break
        
        # If fragments directory is found, try to mux the fragments
        if fragments_dir:
            print(f"{Fore.CYAN}Found partially downloaded fragments. Attempting to mux available content...")
            
            # Define output file path (using the fragments directory name as a base)
            output_filename = f"{os.path.basename(fragments_dir)}_partial.mp4"
            output_file = os.path.join(output_dir, output_filename)
            
            # Prepare options for processing
            options = {
                "keep_fragments": hasattr(args, 'keep_fragments') and args.keep_fragments,
                "metadata": {
                    "title": f"Partial download - {os.path.basename(fragments_dir)}",
                    "comment": "This is a partial download that failed with error."
                }
            }
            
            # Process the downloaded fragments
            try:
                if process_stream_download(fragments_dir, output_file, options):
                    print(f"{Fore.GREEN}Successfully merged available fragments: {output_file}")
                else:
                    print(f"{Fore.RED}Failed to merge fragments. The download was too short or fragments are corrupted.")
            except Exception as merge_error:
                print(f"{Fore.RED}Error merging fragments: {str(merge_error)}")
        
        return False
        
    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}")
        
        # Save failed download to history if enabled
        if not hasattr(args, 'no_history') or not args.no_history:
            save_to_history(args, False, error=str(e))
        
        # Try to mux any fragments that were already downloaded
        output_dir = os.path.dirname(os.path.abspath(args.output))
        fragments_dir = None
        
        # Check for fragments in the output directory
        for subdir in os.listdir(output_dir):
            if os.path.isdir(os.path.join(output_dir, subdir)) and subdir.startswith("NA_"):
                potential_fragments_dir = os.path.join(output_dir, subdir)
                if any(f.endswith(".ts") for f in os.listdir(potential_fragments_dir)):
                    fragments_dir = potential_fragments_dir
                    break
        
        # If fragments directory is found, try to mux the fragments
        if fragments_dir:
            print(f"{Fore.CYAN}Found partially downloaded fragments. Attempting to mux available content...")
            
            # Define output file path (using the fragments directory name as a base)
            output_filename = f"{os.path.basename(fragments_dir)}_partial.mp4"
            output_file = os.path.join(output_dir, output_filename)
            
            # Prepare options for processing
            options = {
                "keep_fragments": hasattr(args, 'keep_fragments') and args.keep_fragments,
                "metadata": {
                    "title": f"Partial download - {os.path.basename(fragments_dir)}",
                    "comment": "This is a partial download that encountered an exception."
                }
            }
            
            # Process the downloaded fragments
            try:
                if process_stream_download(fragments_dir, output_file, options):
                    print(f"{Fore.GREEN}Successfully merged available fragments: {output_file}")
                else:
                    print(f"{Fore.RED}Failed to merge fragments. The download was too short or fragments are corrupted.")
            except Exception as merge_error:
                print(f"{Fore.RED}Error merging fragments: {str(merge_error)}")
        
        return False

def save_to_history(args, success, error=None):
    """Save download information to history"""
    url = args.url
    platform = detect_platform(url)
    
    history_entry = {
        "url": url,
        "platform": platform,
        "timestamp": datetime.now().isoformat(),
        "output_path": args.output,
        "success": success
    }
    
    if hasattr(args, 'quality'):
        history_entry["quality"] = args.quality
    
    if error:
        history_entry["error_message"] = error
    
    history_manager = HistoryManager()
    history_manager.add_download(history_entry)
    
    print(f"{Fore.GREEN}Download saved to history.")

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

def interactive_download():
    """Interactive download interface similar to twt downloader"""
    # Make sure download directory exists
    download_dir = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir, exist_ok=True)
        print(f"{Fore.GREEN}Created 'downloads' folder for saving streams.")
    
    # Ask for stream URL
    questions = [
        inquirer.Text(
            'stream_url',
            message=f"{Fore.CYAN}Enter the stream URL (YouTube or Twitch):",
            validate=lambda _, x: len(x) > 10 and ('youtube.com' in x or 'twitch.tv' in x or 'youtu.be' in x)
        )
    ]
    
    answers = inquirer.prompt(questions)
    if not answers:
        print(f"{Fore.RED}Operation cancelled.")
        return
    
    url = answers['stream_url']
    
    # Detect platform
    platform = detect_platform(url)
    if platform == "unknown":
        print(f"{Fore.RED}Error: URL must be from YouTube or Twitch.")
        return
    
    print(f"\n{Fore.GREEN}Detected platform: {Fore.WHITE}{platform.upper()}")
    
    # Get available qualities
    print(f"\n{Fore.YELLOW}Fetching stream information and available qualities...")
    
    # Use a spinner while fetching qualities
    with Spinner(message=f"{Fore.YELLOW}Analyzing stream...", color=Fore.CYAN) as spinner:
        # For a real implementation, we would get the actual qualities from the stream
        # This is simplified for the example - add a short delay to simulate fetching
        time.sleep(1.5)
        spinner.update_message(f"{Fore.YELLOW}Processing stream metadata...")
        time.sleep(1)
        
    if platform == "youtube":
        qualities = ["1080p", "720p", "480p", "360p", "best"]
    else:  # twitch
        qualities = ["1080p60", "720p60", "720p", "480p", "360p", "160p", "best"]
    
    # Ask for quality
    quality_question = [
        inquirer.List(
            'quality',
            message=f"{Fore.CYAN}Select stream quality:",
            choices=qualities,
        )
    ]
    
    # Add option to list all available formats
    list_formats_first = False
    format_question = [
        inquirer.Confirm(
            'list_formats',
            message=f"{Fore.CYAN}Would you like to see all available formats first?",
            default=False
        )
    ]
    
    format_answer = inquirer.prompt(format_question)
    if format_answer and format_answer['list_formats']:
        list_formats_first = True
        # Fetch and display available formats
        formats = fetch_available_formats(url)
        if formats:
            print(f"\n{Fore.CYAN}Available formats for {url}:")
            for idx, fmt in enumerate(formats):
                print(f"{Fore.WHITE}{idx+1}. {fmt}")
        
    quality_answer = inquirer.prompt(quality_question)
    if not quality_answer:
        print(f"{Fore.RED}Operation cancelled.")
        return
    
    selected_quality = quality_answer['quality']
    
    # Ask if user wants to enable automatic quality fallback
    fallback_question = [
        inquirer.Confirm(
            'use_fallback',
            message=f"{Fore.CYAN}Enable automatic quality fallback if selected quality is unavailable?",
            default=True
        )
    ]
    
    fallback_answer = inquirer.prompt(fallback_question)
    use_fallback = fallback_answer and fallback_answer['use_fallback']
    
    # Generate default filename based on URL and date
    default_filename = f"{platform}_stream_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    
    # Ask for output filename
    filename_question = [
        inquirer.Text(
            'filename',
            message=f"{Fore.CYAN}Enter output filename (without extension):",
            default=default_filename
        )
    ]
    
    filename_answer = inquirer.prompt(filename_question)
    if not filename_answer:
        print(f"{Fore.RED}Operation cancelled.")
        return
    
    filename = filename_answer['filename']
    
    # Ask for additional options
    options_questions = [
        inquirer.Confirm('thumbnail', message=f"{Fore.CYAN}Save thumbnail?", default=True),
        inquirer.Confirm('metadata', message=f"{Fore.CYAN}Add metadata?", default=True),
        inquirer.Confirm('keep_fragments', message=f"{Fore.CYAN}Keep fragments after merging?", default=False),
        inquirer.Confirm('live', message=f"{Fore.CYAN}Download from live stream start (if available)?", default=True),
        inquirer.Confirm('list_formats', message=f"{Fore.CYAN}List all available formats before downloading?", default=False),
        inquirer.Confirm('use_fallback', message=f"{Fore.CYAN}Auto-fallback to lower quality if selected quality unavailable?", default=True)
    ]
    
    options_answers = inquirer.prompt(options_questions)
    if not options_answers:
        print(f"{Fore.RED}Operation cancelled.")
        return
    
    # Cookies file for members-only content
    cookies_question = [
        inquirer.Confirm('need_cookies', message=f"{Fore.CYAN}Is this members-only content requiring cookies?", default=False)
    ]
    
    cookies_answer = inquirer.prompt(cookies_question)
    if not cookies_answer:
        print(f"{Fore.RED}Operation cancelled.")
        return
    
    cookies_path = None
    if cookies_answer['need_cookies']:
        cookies_path_question = [
            inquirer.Text(
                'cookies_path',
                message=f"{Fore.CYAN}Enter path to cookies.txt file:",
            )
        ]
        cookies_path_answer = inquirer.prompt(cookies_path_question)
        if cookies_path_answer:
            cookies_path = cookies_path_answer['cookies_path']
    
    output_path = os.path.join(download_dir, filename)
    
    print(f"\n{Fore.GREEN}Starting download with the following settings:")
    print(f"{Fore.YELLOW}URL: {Fore.WHITE}{url}")
    print(f"{Fore.YELLOW}Platform: {Fore.WHITE}{platform}")
    print(f"{Fore.YELLOW}Quality: {Fore.WHITE}{selected_quality}")
    print(f"{Fore.YELLOW}Output: {Fore.WHITE}{output_path}")
    print(f"{Fore.YELLOW}Save thumbnail: {Fore.WHITE}{options_answers['thumbnail']}")
    print(f"{Fore.YELLOW}Add metadata: {Fore.WHITE}{options_answers['metadata']}")
    print(f"{Fore.YELLOW}Keep fragments: {Fore.WHITE}{options_answers['keep_fragments']}")
    print(f"{Fore.YELLOW}Download from live start: {Fore.WHITE}{options_answers['live']}")
    print(f"{Fore.YELLOW}List formats: {Fore.WHITE}{options_answers['list_formats']}")
    print(f"{Fore.YELLOW}Use quality fallback: {Fore.WHITE}{use_fallback}")
    print(f"{Fore.YELLOW}Using cookies: {Fore.WHITE}{cookies_path is not None}")
    
    # Confirm download
    confirm_question = [
        inquirer.Confirm('confirm', message=f"\n{Fore.CYAN}Start download with these settings?", default=True)
    ]
    
    confirm_answer = inquirer.prompt(confirm_question)
    if not confirm_answer or not confirm_answer['confirm']:
        print(f"{Fore.RED}Download cancelled.")
        return
    
    # Create an args object similar to what argparse would provide
    class Args:
        pass
    
    args = Args()
    args.url = url
    args.output = output_path
    args.quality = selected_quality
    args.template = None
    args.thumbnail = options_answers['thumbnail']
    args.metadata = options_answers['metadata']
    args.keep_fragments = options_answers['keep_fragments']
    args.live = options_answers['live']
    args.cookies = cookies_path
    args.verbose = False
    args.no_history = False
    args.list_formats = options_answers['list_formats']
    args.use_fallback = use_fallback
    args.no_interactive = False
    
    # Start the download
    download_success = download_with_yt_dlp(args)
    
    if download_success:
        # Wait for user to press a key before exiting
        print(f"\n{Fore.GREEN}Download complete! Press Enter to return to the menu...")
        input()
    else:
        print(f"\n{Fore.RED}Download failed. Press Enter to return to the menu...")
        input()

def interactive_history():
    """Interactive history viewer"""
    history_manager = HistoryManager()
    
    with Spinner(message=f"{Fore.YELLOW}Loading download history...", color=Fore.CYAN) as spinner:
        downloads = history_manager.get_downloads()
        time.sleep(0.5)  # Short delay to show the spinner
    
    if not downloads:
        print(f"\n{Fore.YELLOW}No download history found.")
        input(f"{Fore.CYAN}Press Enter to return to the menu...")
        return
    
    print(f"\n{Fore.CYAN}Download History ({len(downloads)} entries):")
    print(f"{Fore.YELLOW}{'ID':4} {'Date':16} {'Platform':8} {'Status':8} {'URL'}")
    print(f"{Fore.YELLOW}{'-'*80}")
    
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
        success = f"{Fore.GREEN}✓" if download.get("success", False) else f"{Fore.RED}✗"
        
        print(f"{i+1:4} {timestamp:16} {platform:8} {success:8} {url[:40]}{'...' if len(url) > 40 else ''}")
    
    print(f"{Fore.YELLOW}{'-'*80}")
    
    # Options for history
    questions = [
        inquirer.List(
            'action',
            message=f"{Fore.CYAN}Select action:",
            choices=[
                ('View details of an entry', 'view'),
                ('Clear all history', 'clear'),
                ('Return to main menu', 'back')
            ],
        )
    ]
    
    answers = inquirer.prompt(questions)
    if not answers:
        return
    
    if answers['action'] == 'view':
        id_question = [
            inquirer.Text(
                'id',
                message=f"{Fore.CYAN}Enter entry ID to view details:",
                validate=lambda _, x: x.isdigit() and 1 <= int(x) <= len(downloads)
            )
        ]
        
        id_answer = inquirer.prompt(id_question)
        if id_answer:
            entry_id = int(id_answer['id']) - 1
            download = downloads[entry_id]
            
            print(f"\n{Fore.CYAN}Download Details:")
            print(f"{Fore.YELLOW}URL: {Fore.WHITE}{download.get('url', 'Unknown')}")
            print(f"{Fore.YELLOW}Platform: {Fore.WHITE}{download.get('platform', 'Unknown')}")
            print(f"{Fore.YELLOW}Quality: {Fore.WHITE}{download.get('quality', 'Unknown')}")
            print(f"{Fore.YELLOW}Output Path: {Fore.WHITE}{download.get('output_path', 'Unknown')}")
            print(f"{Fore.YELLOW}Timestamp: {Fore.WHITE}{download.get('timestamp', 'Unknown')}")
            
            # Format status with color
            success = download.get('success', False)
            status_color = Fore.GREEN if success else Fore.RED
            status_text = "Success" if success else "Failed"
            print(f"{Fore.YELLOW}Status: {status_color}{status_text}")
            
            if 'error_message' in download:
                print(f"{Fore.YELLOW}Error: {Fore.RED}{download.get('error_message')}")
            
            # Ask if user wants to retry the download
            if not success:
                retry_question = [
                    inquirer.Confirm(
                        'retry',
                        message=f"{Fore.CYAN}Would you like to retry this download?",
                        default=False
                    )
                ]
                
                retry_answer = inquirer.prompt(retry_question)
                if retry_answer and retry_answer['retry']:
                    # Create args object for download
                    class Args:
                        pass
                    
                    args = Args()
                    args.url = download.get('url', '')
                    args.output = download.get('output_path', os.path.join(os.getcwd(), "downloads"))
                    args.quality = download.get('quality', 'best')
                    args.template = None
                    args.thumbnail = True
                    args.metadata = True
                    args.keep_fragments = False
                    args.live = True
                    args.cookies = None
                    args.verbose = False
                    args.no_history = False
                    args.list_formats = False
                    args.use_fallback = True
                    args.no_interactive = False
                    
                    print(f"\n{Fore.GREEN}Retrying download...")
                    download_with_yt_dlp(args)
                    
                    input(f"\n{Fore.CYAN}Press Enter to return to history...")
                    interactive_history()
                    return
            
            input(f"\n{Fore.CYAN}Press Enter to return to history...")
            interactive_history()
    
    elif answers['action'] == 'clear':
        confirm = [
            inquirer.Confirm(
                'confirm',
                message=f"{Fore.RED}Are you sure you want to clear all download history?",
                default=False
            )
        ]
        
        confirm_answer = inquirer.prompt(confirm)
        if confirm_answer and confirm_answer['confirm']:
            with Spinner(message=f"{Fore.YELLOW}Clearing history...", color=Fore.CYAN) as spinner:
                clear_history()
                time.sleep(0.5)  # Short delay to show the spinner
            print(f"{Fore.GREEN}History cleared successfully!")
            input(f"{Fore.CYAN}Press Enter to return to the menu...")
    
    # Return to main menu happens automatically

def show_help():
    """Display help information in the interactive mode"""
    # Clear screen for better visuals
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print_banner()
    
    print(f"{Fore.CYAN}{'='*80}")
    print(f"{Fore.YELLOW}Stream Downloader Help".center(80))
    print(f"{Fore.CYAN}{'='*80}\n")
    
    # Basic usage
    print(f"{Fore.GREEN}Basic Usage:")
    print(f"{Fore.WHITE}  Stream Downloader is a tool for downloading Twitch and YouTube livestreams.")
    print(f"{Fore.WHITE}  You can use it in interactive mode or with command-line arguments.\n")
    
    # Interactive mode commands
    print(f"{Fore.GREEN}Interactive Mode Commands:")
    print(f"{Fore.YELLOW}  Download a stream {Fore.WHITE}- Download video from Twitch or YouTube")
    print(f"{Fore.YELLOW}  View download history {Fore.WHITE}- Browse and manage previous downloads")
    print(f"{Fore.YELLOW}  Check for updates {Fore.WHITE}- See if a new version is available")
    print(f"{Fore.YELLOW}  Help {Fore.WHITE}- Display this help information")
    print(f"{Fore.YELLOW}  Exit {Fore.WHITE}- Close the application\n")
    
    # Command line options
    print(f"{Fore.GREEN}Command Line Options:")
    print(f"{Fore.YELLOW}  python stream-dl.py [options] command [command-options]")
    print()
    print(f"{Fore.YELLOW}  Global Options:")
    print(f"{Fore.WHITE}    -i, --interactive     Run in interactive mode with a user-friendly interface")
    print(f"{Fore.WHITE}    -h, --help            Show this help message and exit")
    print()
    print(f"{Fore.YELLOW}  Commands:")
    print(f"{Fore.WHITE}    download              Download a stream")
    print(f"{Fore.WHITE}    history               Manage download history")
    print(f"{Fore.WHITE}    update                Check for application updates")
    print()
    print(f"{Fore.YELLOW}  Download Command Options:")
    print(f"{Fore.WHITE}    python stream-dl.py download URL [options]")
    print(f"{Fore.WHITE}    URL                   URL of the stream to download")
    print(f"{Fore.WHITE}    -o, --output PATH     Output directory or file path")
    print(f"{Fore.WHITE}    -q, --quality QUALITY Video quality to download (default: best)")
    print(f"{Fore.WHITE}    -t, --template FORMAT Output filename template")
    print(f"{Fore.WHITE}    --live                Download live stream from start")
    print(f"{Fore.WHITE}    --thumbnail           Save thumbnail")
    print(f"{Fore.WHITE}    --metadata            Add metadata")
    print(f"{Fore.WHITE}    --keep-fragments      Keep fragments after merging")
    print(f"{Fore.WHITE}    --cookies PATH        Path to cookies file for members-only content")
    print(f"{Fore.WHITE}    -v, --verbose         Enable verbose output")
    print(f"{Fore.WHITE}    --no-history          Don't save to download history")
    print(f"{Fore.WHITE}    --proxy URL           Use proxy for downloading")
    print(f"{Fore.WHITE}    --retries NUMBER      Number of retry attempts (default: 3)")
    print(f"{Fore.WHITE}    --timeout SECONDS     Connection timeout in seconds (default: 30)")
    print(f"{Fore.WHITE}    --quiet               Suppress all output except errors")
    print(f"{Fore.WHITE}    --abort-on-error      Abort on first error")
    print(f"{Fore.WHITE}    --list-formats        List all available formats before downloading")
    print(f"{Fore.WHITE}    --use-fallback        Auto-fallback to lower quality if selected quality unavailable")
    print(f"{Fore.WHITE}    --no-interactive      Don't prompt for retries or confirmations")
    print()
    print(f"{Fore.YELLOW}  History Command Options:")
    print(f"{Fore.WHITE}    python stream-dl.py history [options]")
    print(f"{Fore.WHITE}    --count NUMBER        Number of history items to show")
    print(f"{Fore.WHITE}    --platform PLATFORM   Filter by platform (youtube or twitch)")
    print(f"{Fore.WHITE}    --clear               Clear download history")
    print()
    
    # Examples
    print(f"{Fore.GREEN}Examples:")
    print(f"{Fore.WHITE}  python stream-dl.py --interactive")
    print(f"{Fore.WHITE}  python stream-dl.py download https://youtube.com/watch?v=XXXX --quality 1080p")
    print(f"{Fore.WHITE}  python stream-dl.py download https://twitch.tv/username --live --thumbnail")
    print(f"{Fore.WHITE}  python stream-dl.py download https://youtube.com/watch?v=XXXX --list-formats")
    print(f"{Fore.WHITE}  python stream-dl.py download https://youtube.com/watch?v=XXXX --use-fallback")
    print(f"{Fore.WHITE}  python stream-dl.py history --count 10 --platform youtube")
    print(f"{Fore.WHITE}  python stream-dl.py update\n")
    
    input(f"{Fore.CYAN}Press Enter to return to the menu...")

def interactive_menu():
    """Show interactive main menu"""
    while True:
        # Clear screen for better visuals
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print_banner()
        
        questions = [
            inquirer.List(
                'action',
                message=f"{Fore.CYAN}Select an option:",
                choices=[
                    ('Download a stream', 'download'),
                    ('View download history', 'history'),
                    ('Check for updates', 'update'),
                    ('Help', 'help'),
                    ('Exit', 'exit')
                ],
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            print(f"{Fore.RED}Operation cancelled.")
            break
        
        if answers['action'] == 'download':
            interactive_download()
        elif answers['action'] == 'history':
            interactive_history()
        elif answers['action'] == 'update':
            check_for_app_updates()
            input(f"\n{Fore.CYAN}Press Enter to return to the menu...")
        elif answers['action'] == 'help':
            show_help()
        elif answers['action'] == 'exit':
            print(f"{Fore.GREEN}Thank you for using Stream Downloader CLI!")
            break

def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(description="Stream Downloader CLI")
    
    # Add a special argument for interactive mode
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode with a user-friendly interface"
    )
    
    # Add version argument
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show version information and exit"
    )
    
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
    download_parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    download_parser.add_argument("--no-history", action="store_true", help="Don't save to download history")
    download_parser.add_argument("--proxy", help="Use proxy for downloading. Format: http://[user:pass@]host:port/")
    download_parser.add_argument("--retries", type=int, default=3, help="Number of retry attempts (default: 3)")
    download_parser.add_argument("--timeout", type=int, default=30, help="Connection timeout in seconds (default: 30)")
    download_parser.add_argument("--quiet", action="store_true", help="Suppress all output except errors")
    download_parser.add_argument("--abort-on-error", action="store_true", help="Abort on first error")
    download_parser.add_argument("--list-formats", action="store_true", help="List all available formats before downloading")
    download_parser.add_argument("--use-fallback", action="store_true", help="Auto-fallback to lower quality if selected quality unavailable")
    download_parser.add_argument("--no-interactive", action="store_true", help="Don't prompt for retries or confirmations")
    
    # History command
    history_parser = subparsers.add_parser("history", help="Manage download history")
    history_parser.add_argument("--count", type=int, help="Number of history items to show")
    history_parser.add_argument("--platform", choices=["youtube", "twitch"], help="Filter by platform")
    history_parser.add_argument("--clear", action="store_true", help="Clear download history")
    history_parser.add_argument("--export", help="Export history to a JSON file")
    history_parser.add_argument("--import", dest="import_file", help="Import history from a JSON file")
    history_parser.add_argument("--retry", type=int, help="Retry a specific history entry by ID")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Check for application updates")
    update_parser.add_argument("--force", action="store_true", help="Force update check ignoring cache")
    
    # Help command
    help_parser = subparsers.add_parser("help", help="Show help information for a specific command")
    help_parser.add_argument("topic", nargs='?', help="Command to get help for")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show version and exit if requested
    if args.version:
        version = get_current_version()
        print(f"Stream Downloader v{version}")
        return
    
    # If interactive mode is specified or no arguments provided, show the interactive menu
    if args.interactive or len(sys.argv) == 1:
        interactive_menu()
        return
    
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
        elif args.export:
            # Export functionality - implementation would be needed
            print(f"Exporting history to {args.export}...")
        elif args.import_file:
            # Import functionality - implementation would be needed
            print(f"Importing history from {args.import_file}...")
        elif args.retry is not None:
            # Retry functionality - implementation would be needed
            print(f"Retrying download with ID {args.retry}...")
        else:
            print_history(args.count, args.platform)
    
    elif args.command == "update":
        check_for_app_updates(force=args.force if hasattr(args, 'force') else False)
    
    elif args.command == "help":
        if args.topic:
            # Show help for specific command
            print(f"Help for command: {args.topic}")
            if args.topic == "download":
                download_parser.print_help()
            elif args.topic == "history":
                history_parser.print_help()
            elif args.topic == "update":
                update_parser.print_help()
            else:
                print(f"Unknown help topic: {args.topic}")
        else:
            # Show general help
            parser.print_help()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\nError: {str(e)}")

"""
Enhanced Stream Downloader CLI
This updated implementation provides better fragment tracking
"""

import sys
import os
import argparse
import subprocess
import time
import json
import shutil
import threading
import re
from datetime import datetime
from pathlib import Path
try:
    import inquirer # type: ignore
    from colorama import init, Fore, Style, Back # type: ignore
    # Initialize colorama for cross-platform colored output
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    print("Warning: colorama and/or inquirer not installed. Running in basic mode.")
    # Fallback Fore class
    class Fore:
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        CYAN = ''
        MAGENTA = ''
        WHITE = ''
    class Style:
        RESET_ALL = ''
        BRIGHT = ''
    class Back:
        BLACK = ''

# Import required modules from the existing application
try:
    from src.stream_downloader import StreamDownloader
    from src.stream_merger import process_stream_download
    from src.history_manager import HistoryManager
    from src.updater import get_current_version, check_for_updates
    from src.spinner import Spinner
    from src.cli_help import get_main_help, get_command_help
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the correct directory.")
    sys.exit(1)

# Create function to handle fragment tracking
def save_to_history(args, success, error_message=None):
    """Save download information to history"""
    try:
        history_manager = HistoryManager()
        url = args.url
        quality = args.quality if hasattr(args, 'quality') else "best"
        output = args.output if hasattr(args, 'output') else None
        
        # Create history entry
        history_entry = {
            "url": url,
            "quality": quality,
            "output": output,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": success
        }
        
        if error_message:
            history_entry["error"] = error_message
            
        # Add to history
        history_manager.add_entry(history_entry)
        
    except Exception as e:
        print(f"{Fore.RED}Error saving to history: {str(e)}")

def download_with_yt_dlp(args):
    """Download content using yt-dlp with progress display and fragment tracking"""
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
    
    # Build command
    command = ["yt-dlp"]
    
    # Add URL
    command.append(args.url)
    
    # Quality options with fallback for specific resolutions
    if hasattr(args, 'quality') and args.quality and args.quality != "best":
        if hasattr(args, 'use_fallback') and args.use_fallback:
            # Create a format string with fallbacks for common resolutions
            if args.quality.startswith("1080"):
                command.extend(["-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"])
            elif args.quality.startswith("720"):
                command.extend(["-f", "bestvideo[height<=720]+bestaudio/best[height<=720]/best"])
            elif args.quality.startswith("480"):
                command.extend(["-f", "bestvideo[height<=480]+bestaudio/best[height<=480]/best"])
            elif args.quality.startswith("360"):
                command.extend(["-f", "bestvideo[height<=360]+bestaudio/best[height<=360]/best"])
            else:
                command.extend(["-f", args.quality])
        else:
            command.extend(["-f", args.quality])
    
    # Add output path
    if hasattr(args, 'output') and args.output:
        # Check if the output is a directory or includes a filename
        output_path = args.output
        if not os.path.splitext(output_path)[1]:  # No file extension, assume directory
            # Ensure directory exists
            os.makedirs(output_path, exist_ok=True)
            # Use template if provided, otherwise default template
            if hasattr(args, 'template') and args.template:
                output_path = os.path.join(output_path, args.template)
            else:
                output_path = os.path.join(output_path, "%(title)s-%(id)s.%(ext)s")
        
        command.extend(["-o", output_path])
    
    # Add option for live streams if enabled
    if hasattr(args, 'live') and args.live:
        if not (hasattr(args, 'no_live_from_start') and args.no_live_from_start):
            command.append("--live-from-start")
    
    # Add thumbnail option if enabled
    if hasattr(args, 'thumbnail') and args.thumbnail:
        command.append("--write-thumbnail")
        
    # Add metadata option if enabled
    if hasattr(args, 'metadata') and args.metadata:
        command.append("--add-metadata")
        
    # Add fragments option if enabled
    if hasattr(args, 'keep_fragments') and args.keep_fragments:
        command.append("--keep-fragments")
    
    # Add cookies file if specified
    if hasattr(args, 'cookies') and args.cookies:
        command.extend(["--cookies", args.cookies])
    
    # Add proxy if specified
    if hasattr(args, 'proxy') and args.proxy:
        command.extend(["--proxy", args.proxy])
        
    # Add retries if specified
    if hasattr(args, 'retries') and args.retries is not None:
        command.extend(["--retries", str(args.retries)])
        
    # Add timeout if specified
    if hasattr(args, 'timeout') and args.timeout is not None:
        command.extend(["--socket-timeout", str(args.timeout)])
        
    # Add verbose option if enabled
    if hasattr(args, 'verbose') and args.verbose:
        command.append("--verbose")
        
    # Add progress visualization
    command.append("--progress")
    
    print(f"{Fore.GREEN}Running command: {Fore.WHITE}{' '.join(command)}")
    
    # Record start time
    start_time = time.time()
    
    # Create spinner animation
    spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    spinner_idx = 0
    
    # Track fragment counts
    video_fragments = {"current": 0, "total": 0}
    audio_fragments = {"current": 0, "total": 0}
    
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
                # Check for fragment download information
                if "Downloading fragment" in line:
                    fragment_match = re.search(r'Downloading fragment (\d+) of (\d+)(?:\s+\(audio\))?', line)
                    if fragment_match:
                        current = int(fragment_match.group(1))
                        total = int(fragment_match.group(2))
                        
                        # Check if this is an audio fragment
                        is_audio = "(audio)" in line
                        
                        # Update fragment tracking
                        if is_audio:
                            audio_fragments["current"] = current
                            audio_fragments["total"] = total
                            color = Fore.MAGENTA
                            prefix = "Audio"
                        else:
                            video_fragments["current"] = current
                            video_fragments["total"] = total
                            color = Fore.BLUE
                            prefix = "Video"
                        
                        # Calculate percentage
                        percent = int((current / total) * 100)
                        
                        # Create a progress bar
                        bar_length = 20
                        filled_length = int(bar_length * current / total)
                        bar = '█' * filled_length + '░' * (bar_length - filled_length)
                        
                        # Show fragment progress and also total progress
                        status_text = f"{prefix} fragment: {current}/{total} [{bar}] {percent}%"
                        if video_fragments["total"] > 0 and audio_fragments["total"] > 0:
                            status_text += f" | Video: {video_fragments['current']}/{video_fragments['total']} | Audio: {audio_fragments['current']}/{audio_fragments['total']}"
                        
                        print(f"\r{color}{status_text}", end='')
                        spinner_idx += 1
                        continue
                
                # Handle other output types
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
            
            # Print fragment summary
            if video_fragments["total"] > 0 or audio_fragments["total"] > 0:
                print(f"{Fore.CYAN}Fragment summary:")
                if video_fragments["total"] > 0:
                    print(f"{Fore.BLUE}Video fragments: {video_fragments['current']}/{video_fragments['total']} complete")
                if audio_fragments["total"] > 0:
                    print(f"{Fore.MAGENTA}Audio fragments: {audio_fragments['current']}/{audio_fragments['total']} complete")
            
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
                        args.quality = "best"
                        return download_with_yt_dlp(args)
            
            # Handle Twitch stream errors and offer solutions
            if "no formats that can be downloaded from the start" in last_status:
                print(f"\n{Fore.RED}Error: This Twitch stream doesn't support downloading from the beginning.")
                print(f"{Fore.YELLOW}Suggestion: Retry without the --live-from-start flag")
                
                # Ask if user wants to retry without live-from-start
                if not hasattr(args, 'no_interactive') or not args.no_interactive:
                    retry = input(f"\n{Fore.YELLOW}Retry without --live-from-start? (Y/n): ").strip().lower()
                    if not retry or retry[0] != 'n':
                        args.no_live_from_start = True
                        return download_with_yt_dlp(args)
                
            print(f"\n{Fore.RED}Error: Download failed with exit code {process.returncode}")
            
            # Save failed download to history if enabled
            if not hasattr(args, 'no_history') or not args.no_history:
                save_to_history(args, False, error_message)
            
            return False
    
    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}")
        return False

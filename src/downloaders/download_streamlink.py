"""
Streamlink downloader implementation for Twitch streams
"""
import os
import subprocess
import time
import re
from datetime import datetime
from colorama import Fore, Style

def download_with_streamlink(args, output_path):
    """Download Twitch content using streamlink with progress display"""
    command = ["streamlink"]
    
    # Add URL
    command.append(args.url)
    
    # Quality options with fallback for specific resolutions
    if hasattr(args, 'quality') and args.quality and args.quality != "best":
        command.append(args.quality)
    else:
        command.append("best")
    
    # Output path
    command.extend(["-o", output_path])
    
    # Force progress bar display
    command.append("--force-progress")
    
    # Add option to retry on connection errors
    command.extend(["--retry-max", str(getattr(args, 'retries', 3))])
    command.extend(["--retry-streams", "5"])
    
    # Add default stream timeout options
    command.extend(["--stream-timeout", str(getattr(args, 'timeout', 30))])
    
    # Cookies file for authenticated streams
    if hasattr(args, 'cookies') and args.cookies:
        command.extend(["--twitch-cookies", args.cookies])
    
    # Set low latency for live streams if requested
    if hasattr(args, 'no_live_from_start') and args.no_live_from_start:
        command.append("--twitch-low-latency")
    
    # Set logging level
    if hasattr(args, 'verbose') and args.verbose:
        command.append("--loglevel")
        command.append("debug")
    elif hasattr(args, 'quiet') and args.quiet:
        command.append("--loglevel")
        command.append("error")
    else:
        command.append("--loglevel")
        command.append("info")
    
    print(f"{Fore.GREEN}Running streamlink command: {Fore.WHITE}{' '.join(command)}")
    
    # Record start time
    start_time = time.time()
    
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
                # Process streamlink output
                if "[download]" in line or "progress" in line.lower():
                    # Extract download statistics if available
                    if "%" in line:
                        last_status = line.strip()
                        print(f"\r{Fore.CYAN}● {Fore.YELLOW}{last_status}", end='')
                elif "error" in line.lower():
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
            return True
        else:
            error_message = f"Exit code {process.returncode}"
            print(f"\n{Fore.RED}Error: Download failed with exit code {process.returncode}")
            
            if "404" in last_status:
                print(f"{Fore.YELLOW}The stream might be offline or the URL is invalid.")
            elif "403" in last_status:
                print(f"{Fore.YELLOW}Access denied. The stream might require authentication.")
                print(f"{Fore.WHITE}Try providing a cookies file with --cookies option.")
            
            return False
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Download cancelled by user.")
        return False
        
    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}")
        return False

"""
CLI help module for Stream Downloader
Contains help text and documentation for the CLI interface
"""

from colorama import Fore, Style

def get_main_help():
    """Return the main help text for the CLI"""
    help_text = f"""
{Fore.CYAN}{'='*80}
{Fore.YELLOW}Stream Downloader Help{Style.RESET_ALL}
{Fore.CYAN}{'='*80}

{Fore.GREEN}Basic Usage:{Style.RESET_ALL}
  Stream Downloader is a tool for downloading Twitch and YouTube livestreams.
  You can use it in interactive mode or with command-line arguments.

{Fore.GREEN}Interactive Mode Commands:{Style.RESET_ALL}
  {Fore.YELLOW}Download a stream {Fore.WHITE}- Download video from Twitch or YouTube
  {Fore.YELLOW}View download history {Fore.WHITE}- Browse and manage previous downloads
  {Fore.YELLOW}Check for updates {Fore.WHITE}- See if a new version is available
  {Fore.YELLOW}Help {Fore.WHITE}- Display this help information
  {Fore.YELLOW}Exit {Fore.WHITE}- Close the application

{Fore.GREEN}Command Line Options:{Style.RESET_ALL}
  {Fore.YELLOW}python stream-dl.py [options] command [command-options]{Style.RESET_ALL}

  {Fore.YELLOW}Global Options:{Style.RESET_ALL}
    -i, --interactive     Run in interactive mode with a user-friendly interface
    -h, --help            Show this help message and exit
    -v, --version         Show version information and exit

  {Fore.YELLOW}Commands:{Style.RESET_ALL}
    download              Download a stream
    history               Manage download history
    update                Check for application updates
    help                  Show help for a specific command

{Fore.GREEN}Examples:{Style.RESET_ALL}
  python stream-dl.py --interactive
  python stream-dl.py download https://youtube.com/watch?v=XXXX --quality 1080p
  python stream-dl.py download https://twitch.tv/username --live --thumbnail
  python stream-dl.py history --count 10 --platform youtube
  python stream-dl.py update
  python stream-dl.py help download
"""
    return help_text

def get_download_help():
    """Return the help text for the download command"""
    help_text = f"""
{Fore.CYAN}{'='*80}
{Fore.YELLOW}Stream Downloader - Download Command Help{Style.RESET_ALL}
{Fore.CYAN}{'='*80}

{Fore.GREEN}Usage:{Style.RESET_ALL}
  python stream-dl.py download URL [options]

{Fore.GREEN}Arguments:{Style.RESET_ALL}
  {Fore.YELLOW}URL{Style.RESET_ALL}                    URL of the stream to download

{Fore.GREEN}Options:{Style.RESET_ALL}
  {Fore.YELLOW}-o, --output PATH{Style.RESET_ALL}      Output directory or file path
  {Fore.YELLOW}-q, --quality QUALITY{Style.RESET_ALL}  Video quality to download (default: best)
  {Fore.YELLOW}-t, --template FORMAT{Style.RESET_ALL}  Output filename template
  {Fore.YELLOW}--live{Style.RESET_ALL}                 Download live stream from start
  {Fore.YELLOW}--thumbnail{Style.RESET_ALL}            Save thumbnail
  {Fore.YELLOW}--metadata{Style.RESET_ALL}             Add metadata
  {Fore.YELLOW}--keep-fragments{Style.RESET_ALL}       Keep fragments after merging
  {Fore.YELLOW}--cookies PATH{Style.RESET_ALL}         Path to cookies file for members-only content
  {Fore.YELLOW}--verbose{Style.RESET_ALL}              Enable verbose output
  {Fore.YELLOW}--no-history{Style.RESET_ALL}           Don't save to download history
  {Fore.YELLOW}--proxy URL{Style.RESET_ALL}            Use proxy for downloading
  {Fore.YELLOW}--retries NUMBER{Style.RESET_ALL}       Number of retry attempts (default: 3)
  {Fore.YELLOW}--timeout SECONDS{Style.RESET_ALL}      Connection timeout in seconds (default: 30)
  {Fore.YELLOW}--quiet{Style.RESET_ALL}                Suppress all output except errors
  {Fore.YELLOW}--abort-on-error{Style.RESET_ALL}       Abort on first error

{Fore.GREEN}Examples:{Style.RESET_ALL}
  python stream-dl.py download https://youtube.com/watch?v=XXXX --quality 1080p
  python stream-dl.py download https://twitch.tv/username --live --thumbnail
  python stream-dl.py download https://youtube.com/watch?v=XXXX --cookies cookies.txt
"""
    return help_text

def get_history_help():
    """Return the help text for the history command"""
    help_text = f"""
{Fore.CYAN}{'='*80}
{Fore.YELLOW}Stream Downloader - History Command Help{Style.RESET_ALL}
{Fore.CYAN}{'='*80}

{Fore.GREEN}Usage:{Style.RESET_ALL}
  python stream-dl.py history [options]

{Fore.GREEN}Options:{Style.RESET_ALL}
  {Fore.YELLOW}--count NUMBER{Style.RESET_ALL}         Number of history items to show
  {Fore.YELLOW}--platform PLATFORM{Style.RESET_ALL}    Filter by platform (youtube or twitch)
  {Fore.YELLOW}--clear{Style.RESET_ALL}                Clear download history
  {Fore.YELLOW}--export FILE{Style.RESET_ALL}          Export history to a JSON file
  {Fore.YELLOW}--import FILE{Style.RESET_ALL}          Import history from a JSON file
  {Fore.YELLOW}--retry ID{Style.RESET_ALL}             Retry a specific history entry by ID

{Fore.GREEN}Examples:{Style.RESET_ALL}
  python stream-dl.py history
  python stream-dl.py history --count 10
  python stream-dl.py history --platform youtube
  python stream-dl.py history --clear
  python stream-dl.py history --export history_backup.json
"""
    return help_text

def get_update_help():
    """Return the help text for the update command"""
    help_text = f"""
{Fore.CYAN}{'='*80}
{Fore.YELLOW}Stream Downloader - Update Command Help{Style.RESET_ALL}
{Fore.CYAN}{'='*80}

{Fore.GREEN}Usage:{Style.RESET_ALL}
  python stream-dl.py update [options]

{Fore.GREEN}Options:{Style.RESET_ALL}
  {Fore.YELLOW}--force{Style.RESET_ALL}                Force update check ignoring cache

{Fore.GREEN}Examples:{Style.RESET_ALL}
  python stream-dl.py update
  python stream-dl.py update --force
"""
    return help_text

def get_command_help(command):
    """Return the help text for a specific command"""
    if command == "download":
        return get_download_help()
    elif command == "history":
        return get_history_help()
    elif command == "update":
        return get_update_help()
    else:
        return get_main_help()

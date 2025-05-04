# Stream Downloader v1.0.0-beta

This is the first beta release of Stream Downloader, a modern application for downloading Twitch and YouTube livestreams with both GUI and CLI interfaces.

## Features

- **Multi-Platform Support**: Download livestreams from Twitch and YouTube
- **Dual Interfaces**: 
  - User-friendly GUI with advanced controls
  - **NEW** - Interactive CLI with colorful menu interface and progress animations
  - Traditional command-line arguments for scripting and automation
- **Advanced Stream Handling**: Downloads and processes live stream fragments 
- **Modern User Interface**: 
  - Clean GUI design with light and dark themes
  - Interactive, colorful CLI experience similar to twt folder downloader
- **History Management**: Track, manage, and retry your download history 

## What's New in This Version

- Added a powerful interactive CLI interface with:
  - Colorful ASCII art and styled text
  - Menu-driven interface with arrow key navigation
  - **NEW** - Integrated comprehensive help system with command documentation
  - **NEW** - "Help" option in interactive menu with detailed usage information
  - **NEW** - Enhanced command-line options with advanced parameters:
    - Proxy support for region-restricted content
    - Customizable retry and timeout settings
    - Error handling options (quiet mode, abort-on-error)
    - Support for command-specific help topics
  - Spinner animations for downloads and operations
  - Interactive download history management with retry functionality
  - Real-time download progress visualization
- Improved error handling and user feedback
- Better mobile/Termux environment compatibility with interactive CLI
- Added retry functionality for failed downloads
- **NEW** - Added import/export functionality for download history
- **NEW** - Added history management with sorting, filtering, and retry options
- **NEW** - Added version display with `--version` flag

## Installation

### Option 1: Binary Release (Windows)
- Download the `stream-downloader-v1.0.0-beta-win64-binary.zip` file
- Extract the ZIP file
- Run `StreamDownloader.exe`

### Option 2: From Source
- Download the `stream-downloader-v1.0.0-beta.zip` source archive
- Extract the ZIP file
- Install dependencies with `pip install -r requirements.txt`
- Run with `python src/main.py` (GUI) or `python stream-dl.py` (Interactive CLI)

## Requirements

- Python 3.6+ (for source installation)
- FFmpeg (must be installed and in PATH)
- Additional packages for interactive CLI: inquirer, colorama

## Known Issues

- Icon support may be inconsistent on some systems
- Some advanced YouTube features might require additional cookies configuration
- Spinner animation may not display correctly in all terminal environments

## Coming Soon

- Bandwidth control features
- Support for more streaming platforms
- Additional interactive CLI themes and customizations

## Feedback

Please report any issues or suggestions through GitHub Issues.

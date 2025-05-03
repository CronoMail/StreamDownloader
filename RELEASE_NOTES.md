# Stream Downloader v1.0.0-beta

This is the first beta release of Stream Downloader, a modern application for downloading Twitch and YouTube livestreams with both GUI and CLI interfaces.

## Features

- **Multi-Platform Support**: Download livestreams from Twitch and YouTube
- **Dual Interfaces**: Choose between the user-friendly GUI or powerful CLI
- **Advanced Stream Handling**: Downloads and processes live stream fragments 
- **Modern User Interface**: Clean design with light and dark themes
- **History Management**: Track and manage your download history

## Installation

### Option 1: Binary Release (Windows)
- Download the `stream-downloader-v1.0.0-beta-win64-binary.zip` file
- Extract the ZIP file
- Run `StreamDownloader.exe`

### Option 2: From Source
- Download the `stream-downloader-v1.0.0-beta.zip` source archive
- Extract the ZIP file
- Install dependencies with `pip install -r requirements.txt`
- Run with `python src/main.py` or `python stream-dl.py` (CLI)

## Requirements

- Python 3.6+ (for source installation)
- FFmpeg (must be installed and in PATH)

## Known Issues

- Icon support may be inconsistent on some systems
- Some advanced YouTube features might require additional cookies configuration

## Coming Soon

- Mobile/Termux environment improvements
- Bandwidth control features
- Support for more streaming platforms

## Feedback

Please report any issues or suggestions through GitHub Issues.

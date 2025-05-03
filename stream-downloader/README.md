# Stream Downloader

A modern application for downloading Twitch and YouTube livestreams with ease. Available as both a GUI application (built with PyQt5) and a CLI tool, inspired by [ytarchive](https://github.com/Kethsar/ytarchive).

![Stream Downloader Screenshot](resources/screenshot.png)

## Features

- **Multi-Platform Support**: Download livestreams from Twitch and YouTube
- **Dual Interfaces**: Choose between the user-friendly GUI or powerful CLI
- **Advanced Stream Handling**: 
  - Downloads and processes live stream fragments similar to ytarchive
  - Captures streams from the beginning even when joining late
  - Supports multiple quality options
- **User-Friendly Experience**:
  - Modern, responsive interface with light and dark themes
  - Real-time progress tracking with detailed logs
  - Automatic platform detection from URLs
- **Accessibility Features**:
  - Members-only content support via cookies
  - Proxy configuration for region-restricted content
- **Media Processing**:
  - Thumbnail and metadata embedding
  - Customizable output filename templates
  - Fragment preservation options
- **Organization Tools**:
  - Download history management
  - Export/import history functionality
- **System Integration**:
  - Desktop shortcuts
  - Auto-update functionality
  - Lightweight and efficient resource usage

## Installation

### Prerequisites

- Python 3.6+
- FFmpeg (must be installed and available in your PATH)

### Easy Setup

Run the installer script which will handle dependencies and create shortcuts:

```bash
python install.py
```

### Manual Setup

1. Clone this repository or download the source code:

```bash
git clone https://github.com/Cronomail/stream-downloader.git
cd stream-downloader
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application using one of the methods below

### Building Standalone Executable

To create a standalone executable that doesn't require Python:

```bash
python build.py
```

The executable will be created in the `dist` directory.

## Usage

### GUI Application

1. Start the GUI:

```bash
python src/main.py
```

Or on Windows, you can double-click the `run.bat` file.

2. Enter a Twitch or YouTube stream URL
3. Select the desired quality
4. Choose an output directory
5. Configure any additional options
6. Click "Start Download"

#### GUI Features

- **Download Tab**: Main interface for downloading streams
- **History Tab**: View and manage previous downloads
- **Settings Tab**: Configure application preferences
- **About Tab**: Application information and update checking
- **Theme Toggle**: Switch between light and dark themes
- **Detailed Logging**: View real-time download progress and events

### CLI Application

The command-line interface provides fast access to downloading functionality:

```bash
python stream-dl.py download URL [options]
```

#### Basic Commands

- **Download a stream**:
  ```bash
  python stream-dl.py download https://youtube.com/watch?v=XXXX --quality best
  ```

- **View download history**:
  ```bash
  python stream-dl.py history
  ```

- **Check for updates**:
  ```bash
  python stream-dl.py update
  ```

#### CLI Options

The CLI tool supports extensive options for customization:

```
python stream-dl.py download [URL] [options]

Options:
  -o, --output PATH       Output directory or file path
  -q, --quality QUALITY   Video quality to download (default: best)
  -t, --template FORMAT   Output filename template
  --live                  Download live stream from start
  --thumbnail             Save thumbnail
  --metadata              Add metadata
  --keep-fragments        Keep fragments after merging
  --cookies PATH          Path to cookies file for members-only content
  -v, --verbose           Enable verbose output
  --no-history            Don't save to download history
```

### Advanced Settings

- **Output Filename Template**: Customize how the downloaded files are named using formats like `%(title)s-%(id)s.%(ext)s`
- **Cookies File**: Provide a cookies.txt file for accessing members-only content
- **FFmpeg Path**: Manually specify the FFmpeg executable path if it's not in your system PATH
- **Proxy**: Configure a proxy for downloading geo-restricted content
- **Theme Selection**: Choose between light and dark themes (GUI only)
- **Update Checking**: Enable or disable automatic update checking at startup

## Mobile Usage

The CLI version works on Android via Termux:

1. Install Termux from F-Droid
2. Set up Python environment:
   ```bash
   pkg install python ffmpeg
   ```
3. Clone the repository and install dependencies
4. Run using the CLI interface

## Project Structure

```
stream-downloader/
│
├── src/                       # Source code
│   ├── main.py                # GUI application entry point
│   ├── cli.py                 # CLI implementation
│   ├── stream_downloader.py   # Core download functionality
│   ├── stream_merger.py       # Media processing utilities
│   ├── history_manager.py     # Download history tracking
│   ├── updater.py             # Update checking
│   ├── style.qss              # Light theme stylesheet
│   └── style_dark.qss         # Dark theme stylesheet
│
├── resources/                 # Application resources
│   └── icon.base64            # Base64 encoded icon data
│
├── stream-dl.py               # CLI entry point
├── build.py                   # Build script for creating executables
├── install.py                 # Installation script
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```

## Credits

This application is powered by:

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the download functionality
- [ytarchive](https://github.com/Kethsar/ytarchive) for inspiration and fragment handling logic
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the user interface
- [FFmpeg](https://ffmpeg.org/) for media processing and merging

## License

This project is licensed under the MIT License - see the LICENSE file for details.

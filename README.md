# Stream Downloader

A modern application for downloading Twitch and YouTube livestreams with ease. Available as both a GUI application (built with PyQt5) and a CLI tool, inspired by [ytarchive](https://github.com/Kethsar/ytarchive).

![Stream Downloader Screenshot](resources/screenshot.png)

## Features

- **Multi-Platform Support**: 
  - Download livestreams from Twitch and YouTube
  - Optimized downloads with platform-specific backends:
    - Streamlink for Twitch streams
    - yt-dlp for YouTube and other platforms
- **Dual Interfaces**: 
  - User-friendly GUI with advanced controls
  - Powerful CLI with both interactive and command modes
- **Advanced Stream Handling**: 
  - Downloads and processes live stream fragments similar to ytarchive
  - Captures streams from the beginning even when joining late
  - Supports multiple quality options
  - Displays real-time tracking of video and audio fragments
- **User-Friendly Experience**:
  - Modern, responsive interface with light and dark themes (GUI)
  - Colorful, interactive menu-driven CLI with spinner animations
  - Real-time progress tracking with detailed logs
  - Automatic platform detection from URLs
  - Flexible download options including the ability to disable "live from start" for Twitch streams that don't support it

If you encounter any issues, please check the [Troubleshooting Guide](TROUBLESHOOTING.md) for solutions to common problems.
- **Accessibility Features**:
  - Members-only content support via cookies
  - Proxy configuration for region-restricted content
  - Mobile usage support via Termux on Android
- **Media Processing**:
  - Thumbnail and metadata embedding
  - Customizable output filename templates
  - Fragment preservation options
- **Organization Tools**:
  - Download history management with retry functionality
  - Export/import history functionality
- **System Integration**:
  - Desktop shortcuts
  - Auto-update functionality
  - Lightweight and efficient resource usage

## Project Structure

```
StreamDownloader/
├── src/                  # Source code
│   ├── core/             # Core functionality
│   │   ├── stream_downloader.py
│   │   └── stream_merger.py
│   ├── downloaders/      # Platform-specific downloaders
│   │   ├── download_yt_dlp.py      # YouTube downloader
│   │   └── download_streamlink.py  # Twitch downloader
│   ├── utils/            # Utility modules
│   │   ├── history_manager.py
│   │   ├── platform_utils.py
│   │   ├── spinner.py
│   │   └── updater.py
│   ├── ui/               # User interface components
│   │   ├── cli_help.py
│   │   ├── style.qss
│   │   └── style_dark.qss
│   ├── main.py           # GUI application
│   └── cli.py            # CLI interface
├── app.py                # GUI entry point
├── stream-dl.py          # CLI entry point
├── README.md
└── TROUBLESHOOTING.md
```

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
git clone https://github.com/yourusername/stream-downloader.git
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

The command-line interface provides two ways to interact with the application:

1. **Interactive Mode**: A user-friendly, menu-driven interface with colorful output
2. **Command Mode**: Traditional command-line arguments for scripting and automation

#### Interactive Mode

Run the CLI in interactive mode:

```bash
python stream-dl.py --interactive
# or simply
python stream-dl.py
```

This presents a menu with the following options:
- **Download a stream**: Start a new download with guided wizard
- **View download history**: Browse, search, and manage previous downloads
- **Check for updates**: Check for new versions of the application
- **Help**: Display comprehensive documentation and usage examples
- **Exit**: Quit the application

#### Command Line Options

```bash
python stream-dl.py [options] command [command-options]
```

**Global Options:**
- `-i, --interactive`: Run in interactive mode with a user-friendly interface
- `-h, --help`: Show help message and exit
- `-v, --version`: Show version information and exit

**Commands:**
- `download`: Download a stream
- `history`: Manage download history
- `update`: Check for application updates
- `help`: Show help for a specific command

**Download Command:**
```bash
python stream-dl.py download URL [options]
```
- `URL`: URL of the stream to download
- `-o, --output PATH`: Output directory or file path
- `-q, --quality QUALITY`: Video quality to download (default: best)
- `-t, --template FORMAT`: Output filename template
- `--live`: Download live stream from start
- `--thumbnail`: Save thumbnail
- `--metadata`: Add metadata
- `--keep-fragments`: Keep fragments after merging
- `--cookies PATH`: Path to cookies file for members-only content
- `--verbose`: Enable verbose output
- `--no-history`: Don't save to download history
- `--proxy URL`: Use proxy for downloading. Format: http://[user:pass@]host:port/
- `--retries NUMBER`: Number of retry attempts (default: 3)
- `--timeout SECONDS`: Connection timeout in seconds (default: 30)
- `--quiet`: Suppress all output except errors
- `--abort-on-error`: Abort on first error

**History Command:**
```bash
python stream-dl.py history [options]
```
- `--count NUMBER`: Number of history items to show
- `--platform PLATFORM`: Filter by platform (youtube or twitch)
- `--clear`: Clear download history
- `--export FILE`: Export history to a JSON file
- `--import FILE`: Import history from a JSON file
- `--retry ID`: Retry a specific history entry by ID

**Update Command:**
```bash
python stream-dl.py update [options]
```
- `--force`: Force update check ignoring cache

**Help Command:**
```bash
python stream-dl.py help [topic]
```
- `topic`: Optional command to get specific help for

#### CLI Workflow

```
                    +----------------------+
                    |                      |
                    |  stream-dl.py        |
                    |  (Entry Point)       |
                    |                      |
                    +------+---------------+
                           |
                           |
            +--------------|-------------+
            |                            |
 +----------v-----------+   +-----------v-----------+
 | Interactive Mode     |   | Command Mode          |
 |                      |   |                       |
 | • Colorful UI        |   | • Command Arguments   |
 | • Menu-Driven        |   | • Scriptable          |
 | • Progress Animation |   | • Automation          |
 | • Help System        |   | • Advanced Options    |
 +---------+------------+   +-----------+-----------+
           |                            |
           +------------+---------------+
                        |
                        |
           +------------v---------------+
           |                            |
           |  src/cli.py                |
           |  CLI Implementation        |
           |                            |
           +------------+---------------+
                        |
                        |
         +--------------+--------------+
         |                             |
+--------v--------+   +----------------v---+
|                 |   |                    |
| yt-dlp          |   | History Manager    |
| Stream Download |   | Download Tracking  |
|                 |   |                    |
+--------+--------+   +----------------+---+
         |                             |
         +-------------+--------------+
                       |
                       |
             +---------v----------+
             |                    |
             | FFmpeg             |
             | Media Processing   |
             |                    |
             +--------------------+
```

#### Interactive Mode

Simply run the application without arguments to enter the interactive mode:

```bash
python stream-dl.py
```

This launches a colorful, menu-driven interface similar to the twt folder downloader that allows you to:

- Navigate through menus with arrow keys
- Select options with interactive prompts
- View real-time download progress with animations
- Browse download history with detailed information
- Access built-in help documentation
- Easily retry failed downloads
- Check for application updates

#### Command Mode

For scripting or automation, use the traditional command-line arguments:

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

- **Show help information**:
  ```bash
  python stream-dl.py help [command]
  ```

- **Force interactive mode**:
  ```bash
  python stream-dl.py --interactive
  ```

#### CLI Options

The CLI tool supports extensive options for customization:

```
python stream-dl.py [global-options] command [command-options]

Global Options:
  -i, --interactive      Run in interactive mode with a user-friendly interface
  -v, --version          Show version information and exit
  -h, --help             Show help message and exit

Commands:
  download               Download a stream
  history                Manage download history
  update                 Check for application updates
  help                   Show help information for a specific command

Download Options:
  python stream-dl.py download URL [options]
  URL                    URL of the stream to download
  -o, --output PATH      Output directory or file path
  -q, --quality QUALITY  Video quality to download (default: best)
  -t, --template FORMAT  Output filename template
  --live                 Download live stream from start
  --thumbnail            Save thumbnail
  --metadata             Add metadata
  --keep-fragments       Keep fragments after merging
  --cookies PATH         Path to cookies file for members-only content
  --verbose              Enable verbose output
  --no-history           Don't save to download history
  --proxy URL            Use proxy for downloading
  --retries NUMBER       Number of retry attempts (default: 3)
  --timeout SECONDS      Connection timeout in seconds (default: 30)
  --quiet, -q            Suppress all output except errors
  --abort-on-error       Abort on first error

History Options:
  python stream-dl.py history [options]
  --count NUMBER         Number of history items to show
  --platform PLATFORM    Filter by platform (youtube or twitch)
  --clear                Clear download history
  --export FILE          Export history to a JSON file
  --import FILE          Import history from a JSON file
  --retry ID             Retry a specific history entry by ID

Update Options:
  python stream-dl.py update [options]
  --force                Force update check ignoring cache
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
3. Install required packages:
   ```bash
   pip install inquirer colorama yt-dlp
   ```
4. Clone the repository and install dependencies
5. Run using the interactive CLI for the best mobile experience:
   ```bash
   python stream-dl.py
   ```

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
│   ├── spinner.py             # CLI spinner animation utilities
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

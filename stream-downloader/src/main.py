import sys
import os
import re
import subprocess
import json
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path

# PyQt imports - wrapped in try/except for better error handling
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QComboBox, QProgressBar, 
                               QFileDialog, QTabWidget, QCheckBox, QMessageBox, QSplitter,
                               QTextEdit, QFrame, QGridLayout, QSpacerItem, QSizePolicy,
                               QListWidget, QListWidgetItem, QMenu, QAction, QToolBar,
                               QAbstractItemView)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl, QSize, QSettings, QTimer
    from PyQt5.QtGui import QIcon, QPixmap, QFont, QDesktopServices, QColor
except ImportError:
    print("Error: PyQt5 is required. Please install it with 'pip install PyQt5'")
    sys.exit(1)

# Local imports
from history_manager import HistoryManager
from updater import get_current_version, UpdateChecker, show_update_dialog

# Constants
APP_NAME = "Stream Downloader"
APP_VERSION = "1.0.0"
APP_AUTHOR = "StreamGrab Team"
DEFAULT_OUTPUT_TEMPLATE = "%(title)s-%(id)s.%(ext)s"

class Worker(QThread):
    """Worker thread for handling downloads"""
    progress = pyqtSignal(dict)
    finished = pyqtSignal(bool, str)
    log = pyqtSignal(str)
    
    def __init__(self, stream_url, quality, output_path, options):
        super().__init__()
        self.stream_url = stream_url
        self.quality = quality
        self.output_path = output_path
        self.options = options
        self.process = None
        self.running = False
          def run(self):
        self.running = True
        try:
            # Create command based on options
            command = self.build_command()
            
            # Log the command
            self.log.emit(f"Executing: {' '.join(command)}")
            
            # Start the process
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Flag to track manual cancellation
            self.canceled = False
            
            # Read and process output
            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    self.process.terminate()
                    self.canceled = True
                    break
                    
                self.log.emit(line.strip())
                
                # Parse progress information
                progress_info = self.parse_progress(line)
                if progress_info:
                    self.progress.emit(progress_info)
            
            # Wait for process to complete
            exit_code = self.process.wait()
            
            if self.canceled:
                self.finished.emit(False, "Download stopped by user")
            elif exit_code == 0:
                self.finished.emit(True, "Download completed successfully!")
            else:
                self.finished.emit(False, f"Download failed with exit code {exit_code}")
                
        except Exception as e:
            self.log.emit(f"Error: {str(e)}")
            self.finished.emit(False, str(e))
    
    def build_command(self):
        """Build command based on selected options"""
        command = ["python", "-m", "yt_dlp"]
        
        # Add URL
        command.append(self.stream_url)
        
        # Add quality settings
        if self.quality and self.quality != "best":
            command.extend(["-f", self.quality])
        
        # Add output template
        output_template = os.path.join(self.output_path, self.options.get("output_template", DEFAULT_OUTPUT_TEMPLATE))
        command.extend(["-o", output_template])
        
        # Add option to download live streams
        command.append("--live-from-start")
        
        # Add other options based on checkboxes
        if self.options.get("write_thumbnail", False):
            command.append("--write-thumbnail")
            
        if self.options.get("add_metadata", False):
            command.append("--add-metadata")
        
        if self.options.get("keep_fragments", False):
            command.append("--keep-fragments")
            
        if self.options.get("cookies_file"):
            command.extend(["--cookies", self.options.get("cookies_file")])
            
        # Add verbose output
        command.append("-v")
            
        return command
    
    def parse_progress(self, line):
        """Parse progress information from yt-dlp output"""
        # Match download progress line
        download_match = re.search(r'\[download\]\s+(\d+\.\d+)%\s+of\s+~?(\d+\.\d+)(\w+)\s+at\s+(\d+\.\d+)(\w+)/s', line)
        if download_match:
            percent = float(download_match.group(1))
            size = f"{download_match.group(2)} {download_match.group(3)}"
            speed = f"{download_match.group(4)} {download_match.group(5)}/s"
            return {
                "percent": percent,
                "size": size,
                "speed": speed
            }
            
        # Match download started line
        started_match = re.search(r'\[download\]\s+Destination:\s+(.*)', line)
        if started_match:
            return {
                "status": "started",
                "filename": started_match.group(1)
            }
            
        # Match merging line
        merging_match = re.search(r'\[ffmpeg\]\s+Merging', line)
        if merging_match:
            return {
                "status": "merging"
            }
            
        return None
      def stop(self):
        """Stop the download process"""
        self.running = False
        if self.process:
            try:
                self.process.terminate()
                # Give it a short time to terminate gracefully
                timeout = 3  # seconds
                start_time = time.time()
                while self.process.poll() is None and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                
                # Force kill if it's still running
                if self.process.poll() is None:
                    if os.name == 'nt':  # Windows
                        self.process.kill()
                    else:  # Unix-like
                        import signal
                        os.kill(self.process.pid, signal.SIGKILL)
            except Exception as e:
                # Just log the error, don't crash
                print(f"Error stopping process: {str(e)}")


class TwitchDownloader:
    """Class for handling Twitch-specific download logic"""
    
    @staticmethod
    def get_qualities():
        return [
            "best",
            "720p60",
            "720p",
            "480p",
            "360p",
            "160p",
            "audio_only"
        ]
    
    @staticmethod
    def validate_url(url):
        """Validate if URL is a valid Twitch URL"""
        twitch_patterns = [
            r'^https?://(?:www\.)?twitch\.tv/([^/]+)(?:/video/(\d+))?$',
            r'^https?://(?:www\.)?twitch\.tv/videos/(\d+)$'
        ]
        
        for pattern in twitch_patterns:
            if re.match(pattern, url):
                return True
        return False


class YouTubeDownloader:
    """Class for handling YouTube-specific download logic"""
    
    @staticmethod
    def get_qualities():
        return [
            "best",
            "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "worstvideo+worstaudio/worst"
        ]
    
    @staticmethod
    def validate_url(url):
        """Validate if URL is a valid YouTube URL"""
        youtube_patterns = [
            r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/channel/[\w-]+/live$',
            r'^https?://youtu\.be/[\w-]+'
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url):
                return True
        return False


class StreamDownloaderApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings(APP_AUTHOR, APP_NAME)
        self.worker = None
        self.history_manager = HistoryManager()
        self.current_version = get_current_version()
        self.init_ui()
        self.load_settings()
        
        # Check for updates if enabled
        if self.settings.value("auto_update", True, type=bool):
            self.check_for_updates()
    
    def check_for_updates(self):
        """Check for application updates"""
        self.update_checker = UpdateChecker(self.current_version)
        self.update_checker.update_available.connect(self.on_update_available)
        self.update_checker.start()
    
    def on_update_available(self, latest_version, release_url):
        """Handle notification of available update"""
        show_update_dialog(self, latest_version, release_url)
    
    def init_ui(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Add download tab
        download_tab = self.create_download_tab()
        tabs.addTab(download_tab, "Download")
        
        # Add history tab
        history_tab = self.create_history_tab()
        tabs.addTab(history_tab, "History")
        
        # Add settings tab
        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, "Settings")
        
        # Add about tab
        about_tab = self.create_about_tab()
        tabs.addTab(about_tab, "About")
        
        main_layout.addWidget(tabs)
        
    def create_download_tab(self):
        """Create the download tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # URL Input section
        url_layout = QHBoxLayout()
        url_label = QLabel("Stream URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Twitch or YouTube stream URL")
        self.url_input.textChanged.connect(self.on_url_changed)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # Platform indicator
        platform_layout = QHBoxLayout()
        self.platform_label = QLabel("Platform: ")
        self.platform_indicator = QLabel("Not detected")
        self.platform_indicator.setStyleSheet("font-weight: bold;")
        platform_layout.addWidget(self.platform_label)
        platform_layout.addWidget(self.platform_indicator)
        platform_layout.addStretch()
        layout.addLayout(platform_layout)
        
        # Quality selector
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Quality:")
        self.quality_selector = QComboBox()
        self.quality_selector.addItems(["best"])  # Default option
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_selector)
        layout.addLayout(quality_layout)
        
        # Options section
        options_frame = QFrame()
        options_frame.setFrameShape(QFrame.StyledPanel)
        options_layout = QGridLayout(options_frame)
        
        # Checkboxes for options
        self.write_thumbnail_cb = QCheckBox("Save thumbnail")
        self.add_metadata_cb = QCheckBox("Add metadata")
        self.keep_fragments_cb = QCheckBox("Keep fragments")
        
        options_layout.addWidget(self.write_thumbnail_cb, 0, 0)
        options_layout.addWidget(self.add_metadata_cb, 0, 1)
        options_layout.addWidget(self.keep_fragments_cb, 1, 0)
        
        # Cookies file option
        cookies_layout = QHBoxLayout()
        cookies_label = QLabel("Cookies file:")
        self.cookies_path = QLineEdit()
        self.cookies_path.setReadOnly(True)
        self.cookies_path.setPlaceholderText("Optional: Select cookies file for members-only content")
        cookies_button = QPushButton("Browse...")
        cookies_button.clicked.connect(self.browse_cookies)
        
        cookies_layout.addWidget(cookies_label)
        cookies_layout.addWidget(self.cookies_path)
        cookies_layout.addWidget(cookies_button)
        options_layout.addLayout(cookies_layout, 2, 0, 1, 2)
        
        layout.addWidget(options_frame)
        
        # Output directory
        output_layout = QHBoxLayout()
        output_label = QLabel("Output directory:")
        self.output_path = QLineEdit()
        self.output_path.setReadOnly(True)
        output_button = QPushButton("Browse...")
        output_button.clicked.connect(self.browse_output_dir)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_button)
        layout.addLayout(output_layout)
        
        # Progress section
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        layout.addLayout(progress_layout)
        
        # Log section
        log_label = QLabel("Log:")
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setLineWrapMode(QTextEdit.NoWrap)
        
        layout.addWidget(log_label)
        layout.addWidget(self.log_output)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.download_button = QPushButton("Start Download")
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.start_download)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_download)
        
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        return tab
    
    def create_history_tab(self):
        """Create the history tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_history_context_menu)
        self.history_list.itemDoubleClicked.connect(self.load_from_history)
        
        # Buttons for history management
        button_layout = QHBoxLayout()
        
        clear_button = QPushButton("Clear History")
        clear_button.clicked.connect(self.clear_history)
        
        export_button = QPushButton("Export History")
        export_button.clicked.connect(self.export_history)
        
        import_button = QPushButton("Import History")
        import_button.clicked.connect(self.import_history)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_history)
        
        button_layout.addWidget(clear_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(import_button)
        button_layout.addWidget(refresh_button)
        
        # Add widgets to layout
        layout.addWidget(QLabel("Download History:"))
        layout.addWidget(self.history_list)
        layout.addLayout(button_layout)
        
        # Load history items
        self.refresh_history()
        
        return tab
    
    def refresh_history(self):
        """Refresh the history list"""
        self.history_list.clear()
        downloads = self.history_manager.get_downloads()
        
        for download in downloads:
            item = QListWidgetItem()
            
            # Format the item text
            timestamp = download.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                timestamp = "Unknown date"
                
            platform = download.get("platform", "Unknown")
            title = download.get("title", download.get("url", "Unknown"))
            quality = download.get("quality", "Unknown")
            
            item_text = f"{timestamp} - [{platform}] {title} ({quality})"
            item.setText(item_text)
            
            # Store the download info in the item data
            item.setData(Qt.UserRole, download)
            
            # Set icon based on platform
            if platform.lower() == "youtube":
                item.setForeground(QColor("#FF0000"))  # YouTube red
            elif platform.lower() == "twitch":
                item.setForeground(QColor("#6441A5"))  # Twitch purple
            
            self.history_list.addItem(item)
    
    def show_history_context_menu(self, position):
        """Show context menu for history items"""
        menu = QMenu()
        
        # Get the selected item
        selected_items = self.history_list.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        download_info = item.data(Qt.UserRole)
        
        # Add menu actions
        load_action = menu.addAction("Load URL")
        open_folder_action = menu.addAction("Open Output Folder")
        open_url_action = menu.addAction("Open Stream URL")
        remove_action = menu.addAction("Remove from History")
        
        # Show the menu and handle the selected action
        action = menu.exec_(self.history_list.mapToGlobal(position))
        
        if action == load_action:
            self.load_from_history(item)
        elif action == open_folder_action:
            output_path = download_info.get("output_path")
            if output_path and os.path.exists(output_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))
        elif action == open_url_action:
            url = download_info.get("url")
            if url:
                QDesktopServices.openUrl(QUrl(url))
        elif action == remove_action:
            # Remove the item from history
            downloads = self.history_manager.get_downloads()
            timestamp = download_info.get("timestamp")
            updated_downloads = [d for d in downloads if d.get("timestamp") != timestamp]
            self.history_manager.history["downloads"] = updated_downloads
            self.history_manager._save_history()
            self.refresh_history()
    
    def load_from_history(self, item):
        """Load a download from history"""
        download_info = item.data(Qt.UserRole)
        
        # Set URL
        url = download_info.get("url")
        if url:
            self.url_input.setText(url)
            
        # Set quality if available
        quality = download_info.get("quality")
        if quality:
            index = self.quality_selector.findText(quality)
            if index >= 0:
                self.quality_selector.setCurrentIndex(index)
        
        # Set output path if available and exists
        output_path = download_info.get("output_path")
        if output_path and os.path.exists(output_path):
            self.output_path.setText(output_path)
    
    def clear_history(self):
        """Clear download history"""
        reply = QMessageBox.question(
            self, "Clear History", 
            "Are you sure you want to clear your download history?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.history_manager.clear_history()
            self.refresh_history()
    
    def export_history(self):
        """Export download history to a file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export History", 
            str(Path.home()),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            success = self.history_manager.export_history(file_path)
            if success:
                QMessageBox.information(self, "Export Successful", 
                                       f"History exported to {file_path}")
            else:
                QMessageBox.warning(self, "Export Failed", 
                                   "Failed to export history. Please check the file path.")
    
    def import_history(self):
        """Import download history from a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import History", 
            str(Path.home()),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            success = self.history_manager.import_history(file_path)
            if success:
                self.refresh_history()
                QMessageBox.information(self, "Import Successful", 
                                       "History imported successfully")
            else:
                QMessageBox.warning(self, "Import Failed", 
                                   "Failed to import history. Please check the file format.")
    
    def create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Application Theme:")
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark"])
        self.theme_selector.currentIndexChanged.connect(self.on_theme_changed)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_selector)
        layout.addLayout(theme_layout)
        
        # Output template
        template_layout = QHBoxLayout()
        template_label = QLabel("Output filename template:")
        self.output_template = QLineEdit()
        self.output_template.setText(DEFAULT_OUTPUT_TEMPLATE)
        self.output_template.setPlaceholderText("e.g. %(title)s-%(id)s.%(ext)s")
        
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.output_template)
        
        # Help text
        template_help = QLabel(
            "Available template options:\n"
            "%(title)s - Stream title\n"
            "%(id)s - Stream ID\n"
            "%(channel)s - Channel name\n"
            "%(upload_date)s - Upload date (YYYYMMDD)\n"
            "%(ext)s - File extension\n"
        )
        template_help.setWordWrap(True)
        
        # FFmpeg path
        ffmpeg_layout = QHBoxLayout()
        ffmpeg_label = QLabel("FFmpeg path:")
        self.ffmpeg_path = QLineEdit()
        self.ffmpeg_path.setPlaceholderText("Leave empty to use system FFmpeg")
        ffmpeg_button = QPushButton("Browse...")
        ffmpeg_button.clicked.connect(self.browse_ffmpeg)
        
        ffmpeg_layout.addWidget(ffmpeg_label)
        ffmpeg_layout.addWidget(self.ffmpeg_path)
        ffmpeg_layout.addWidget(ffmpeg_button)
        
        # Advanced options
        advanced_frame = QFrame()
        advanced_frame.setFrameShape(QFrame.StyledPanel)
        advanced_layout = QVBoxLayout(advanced_frame)
        
        advanced_title = QLabel("Advanced Options")
        advanced_title.setStyleSheet("font-weight: bold;")
        
        self.use_proxy_cb = QCheckBox("Use proxy")
        
        proxy_layout = QHBoxLayout()
        proxy_label = QLabel("Proxy URL:")
        self.proxy_url = QLineEdit()
        self.proxy_url.setPlaceholderText("e.g. http://127.0.0.1:8080")
        self.proxy_url.setEnabled(False)
        
        self.use_proxy_cb.toggled.connect(lambda state: self.proxy_url.setEnabled(state))
        
        proxy_layout.addWidget(proxy_label)
        proxy_layout.addWidget(self.proxy_url)
        
        # Auto-update option
        self.auto_update_cb = QCheckBox("Check for updates at startup")
        
        advanced_layout.addWidget(advanced_title)
        advanced_layout.addWidget(self.use_proxy_cb)
        advanced_layout.addLayout(proxy_layout)
        advanced_layout.addWidget(self.auto_update_cb)
        
        # Add to main layout
        layout.addLayout(theme_layout)
        layout.addLayout(template_layout)
        layout.addWidget(template_help)
        layout.addLayout(ffmpeg_layout)
        layout.addWidget(advanced_frame)
        
        # Save settings button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        
        layout.addWidget(save_button)
        layout.addStretch()
        
        return tab
    
    def create_about_tab(self):
        """Create the about tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # App title
        title_label = QLabel(APP_NAME)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Version
        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        
        # Description
        description = QLabel(
            "A modern UI application for downloading Twitch and YouTube live streams.\n"
            "Based on logic from ytarchive and powered by yt-dlp."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        
        # GitHub links
        github_layout = QHBoxLayout()
        github_label = QLabel("Source code:")
        ytarchive_link = QPushButton("ytarchive")
        ytarchive_link.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Kethsar/ytarchive")))
        
        github_layout.addWidget(github_label)
        github_layout.addWidget(ytarchive_link)
        github_layout.addStretch()
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addSpacing(20)
        layout.addWidget(description)
        layout.addSpacing(20)
        layout.addLayout(github_layout)
        layout.addStretch()
        
        return tab
    
    def on_url_changed(self):
        """Handle URL input changes"""
        url = self.url_input.text().strip()
        
        # Reset platform indicator
        self.platform_indicator.setText("Not detected")
        self.platform_indicator.setStyleSheet("font-weight: bold;")
        
        # Update quality options
        self.quality_selector.clear()
        
        if TwitchDownloader.validate_url(url):
            self.platform_indicator.setText("Twitch")
            self.platform_indicator.setStyleSheet("font-weight: bold; color: #6441a5;")
            self.quality_selector.addItems(TwitchDownloader.get_qualities())
            self.download_button.setEnabled(bool(url and self.output_path.text()))
            
        elif YouTubeDownloader.validate_url(url):
            self.platform_indicator.setText("YouTube")
            self.platform_indicator.setStyleSheet("font-weight: bold; color: #ff0000;")
            self.quality_selector.addItems(YouTubeDownloader.get_qualities())
            self.download_button.setEnabled(bool(url and self.output_path.text()))
            
        else:
            # Not a valid URL
            self.quality_selector.addItems(["best"])
            self.download_button.setEnabled(False)
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", 
            self.output_path.text() or str(Path.home())
        )
        
        if directory:
            self.output_path.setText(directory)
            # Enable download button if URL is also valid
            url = self.url_input.text().strip()
            if url and (TwitchDownloader.validate_url(url) or YouTubeDownloader.validate_url(url)):
                self.download_button.setEnabled(True)
    
    def browse_cookies(self):
        """Browse for cookies file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Cookies File", 
            str(Path.home()),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.cookies_path.setText(file_path)
    
    def browse_ffmpeg(self):
        """Browse for FFmpeg executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select FFmpeg Executable", 
            str(Path.home()),
            "Executable Files (*.exe);;All Files (*)"
        )
        
        if file_path:
            self.ffmpeg_path.setText(file_path)
    
    def save_settings(self):
        """Save settings to QSettings"""
        self.settings.setValue("output_template", self.output_template.text())
        self.settings.setValue("ffmpeg_path", self.ffmpeg_path.text())
        self.settings.setValue("use_proxy", self.use_proxy_cb.isChecked())
        self.settings.setValue("proxy_url", self.proxy_url.text())
        self.settings.setValue("last_output_dir", self.output_path.text())
        self.settings.setValue("theme", self.theme_selector.currentText().lower())
        self.settings.setValue("auto_update", self.auto_update_cb.isChecked())
        
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
    
    def load_settings(self):
        """Load settings from QSettings"""
        self.output_template.setText(self.settings.value("output_template", DEFAULT_OUTPUT_TEMPLATE))
        self.ffmpeg_path.setText(self.settings.value("ffmpeg_path", ""))
        self.use_proxy_cb.setChecked(self.settings.value("use_proxy", False, type=bool))
        self.proxy_url.setText(self.settings.value("proxy_url", ""))
        self.proxy_url.setEnabled(self.use_proxy_cb.isChecked())
        self.auto_update_cb.setChecked(self.settings.value("auto_update", True, type=bool))
        
        # Set theme
        theme = self.settings.value("theme", "light").lower()
        index = self.theme_selector.findText(theme.capitalize())
        if index >= 0:
            self.theme_selector.setCurrentIndex(index)
        
        # Set last used output directory if available
        last_dir = self.settings.value("last_output_dir", "")
        if last_dir and os.path.isdir(last_dir):
            self.output_path.setText(last_dir)
    
    def start_download(self):
        """Start the download process"""
        stream_url = self.url_input.text().strip()
        quality = self.quality_selector.currentText()
        output_dir = self.output_path.text()
        
        if not stream_url or not output_dir:
            QMessageBox.warning(self, "Missing Information", "Please provide both a stream URL and output directory.")
            return
        
        if not os.path.isdir(output_dir):
            QMessageBox.warning(self, "Invalid Directory", "The specified output directory does not exist.")
            return
        
        # Gather options
        options = {
            "output_template": self.output_template.text(),
            "write_thumbnail": self.write_thumbnail_cb.isChecked(),
            "add_metadata": self.add_metadata_cb.isChecked(),
            "keep_fragments": self.keep_fragments_cb.isChecked()
        }
        
        # Add cookies file if specified
        if self.cookies_path.text():
            options["cookies_file"] = self.cookies_path.text()
        
        # Add ffmpeg path if specified
        if self.ffmpeg_path.text():
            options["ffmpeg_path"] = self.ffmpeg_path.text()
        
        # Add proxy if enabled
        if self.use_proxy_cb.isChecked() and self.proxy_url.text():
            options["proxy"] = self.proxy_url.text()
        
        # Create and start worker thread
        self.worker = Worker(stream_url, quality, output_dir, options)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.log.connect(self.add_log)
        self.worker.start()
        
        # Update UI
        self.download_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Downloading...")
    
    def stop_download(self):
        """Stop the download process"""
        if self.worker and self.worker.isRunning():
            self.add_log("Stopping download...")
            self.worker.stop()
            
            # Update UI
            self.stop_button.setEnabled(False)
            self.status_label.setText("Stopping...")
    
    def update_progress(self, progress_info):
        """Update progress information"""
        if "percent" in progress_info:
            self.progress_bar.setValue(int(progress_info["percent"]))
            self.status_label.setText(f"Downloading: {progress_info['size']} at {progress_info['speed']}")
        
        elif "status" in progress_info:
            if progress_info["status"] == "started":
                self.status_label.setText(f"Started downloading: {os.path.basename(progress_info.get('filename', ''))}")
            
            elif progress_info["status"] == "merging":
                self.status_label.setText("Merging files...")
                self.progress_bar.setRange(0, 0)  # Show indeterminate progress
    
    def on_download_finished(self, success, message):
        """Handle download finished"""
        # Reset UI
        self.download_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setRange(0, 100)
        
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("Download completed successfully!")
            QMessageBox.information(self, "Download Complete", message)
            
            # Save to history
            download_info = {
                "url": self.url_input.text(),
                "platform": self.platform_indicator.text(),
                "quality": self.quality_selector.currentText(),
                "output_path": self.output_path.text(),
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            self.history_manager.add_download(download_info)
        else:
            self.progress_bar.setValue(0)
            self.status_label.setText(f"Download failed: {message}")
            QMessageBox.warning(self, "Download Failed", message)
            
            # Save failed download to history
            download_info = {
                "url": self.url_input.text(),
                "platform": self.platform_indicator.text(),
                "quality": self.quality_selector.currentText(),
                "output_path": self.output_path.text(),
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error_message": message
            }
            
            self.history_manager.add_download(download_info)
    
    def add_log(self, message):
        """Add message to log output"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_history_item_clicked(self, item):
        """Handle history item click"""
        # Load selected history item details
        index = item.data(Qt.UserRole)
        if index is not None:
            self.load_history_item(index)
    
    def load_history_item(self, index):
        """Load history item details into the UI"""
        if 0 <= index < len(self.history_manager.history):
            item = self.history_manager.history[index]
            self.url_input.setText(item["url"])
            self.quality_selector.setCurrentText(item["quality"])
            self.output_path.setText(item["output_dir"])
            self.write_thumbnail_cb.setChecked(item.get("options", {}).get("write_thumbnail", False))
            self.add_metadata_cb.setChecked(item.get("options", {}).get("add_metadata", False))
            self.keep_fragments_cb.setChecked(item.get("options", {}).get("keep_fragments", False))
            self.cookies_path.setText(item.get("options", {}).get("cookies_file", ""))
            self.ffmpeg_path.setText(item.get("options", {}).get("ffmpeg_path", ""))
            self.proxy_url.setText(item.get("options", {}).get("proxy", ""))
            
            # Update platform indicator
            url = item["url"]
            if TwitchDownloader.validate_url(url):
                self.platform_indicator.setText("Twitch")
                self.platform_indicator.setStyleSheet("font-weight: bold; color: #6441a5;")
            elif YouTubeDownloader.validate_url(url):
                self.platform_indicator.setText("YouTube")
                self.platform_indicator.setStyleSheet("font-weight: bold; color: #ff0000;")
            else:
                self.platform_indicator.setText("Not detected")
                self.platform_indicator.setStyleSheet("font-weight: bold;")
    
    def clear_history(self):
        """Clear the download history"""
        self.history_manager.clear_history()
        self.history_list.clear()
        QMessageBox.information(self, "History Cleared", "Download history has been cleared.")
    
    def on_theme_changed(self, index):
        """Handle theme change"""
        theme = self.theme_selector.currentText().lower()
        
        try:
            # Load the appropriate stylesheet
            if theme == "dark":
                stylesheet_path = os.path.join(os.path.dirname(__file__), "style_dark.qss")
            else:
                stylesheet_path = os.path.join(os.path.dirname(__file__), "style.qss")
                
            with open(stylesheet_path, "r") as f:
                self.parent().setStyleSheet(f.read())
                
            # Save the theme preference
            self.settings.setValue("theme", theme)
        except Exception as e:
            QMessageBox.warning(self, "Theme Error", f"Error applying theme: {str(e)}")


def main():
    """Main application entry point"""
    # Check for yt-dlp
    try:
        subprocess.run(["python", "-m", "pip", "install", "-U", "yt-dlp"], 
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("Warning: Failed to update yt-dlp. The application may still work if it's already installed.")
    
    # Create and run the application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern style
    
    # Create main window
    window = StreamDownloaderApp()
    
    # Apply theme from settings
    settings = QSettings(APP_AUTHOR, APP_NAME)
    theme = settings.value("theme", "light").lower()
    
    # Apply the appropriate stylesheet
    try:
        if theme == "dark":
            stylesheet_path = os.path.join(os.path.dirname(__file__), "style_dark.qss")
        else:
            stylesheet_path = os.path.join(os.path.dirname(__file__), "style.qss")
            
        with open(stylesheet_path, "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Error applying theme: {str(e)}")
    
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

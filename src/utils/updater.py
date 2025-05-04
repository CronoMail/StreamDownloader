import os
import sys
import json
import requests
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal

# Constants
GITHUB_API_URL = "https://api.github.com/repos/CronoMail/StreamDownloader/releases/latest"
VERSION_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "VERSION")

class UpdateChecker(QThread):
    """Thread for checking updates in the background"""
    update_available = pyqtSignal(str, str)
    check_complete = pyqtSignal(bool)
    
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
    
    def run(self):
        """Check for updates in a separate thread"""
        try:
            update_info = check_for_updates(self.current_version)
            
            if update_info['update_available']:
                self.update_available.emit(update_info['latest_version'], update_info['release_url'])
            
            self.check_complete.emit(update_info['update_available'])
        except Exception as e:
            print(f"Error checking for updates: {str(e)}")
            self.check_complete.emit(False)

def get_current_version():
    """Get the current version from VERSION file"""
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as f:
                return f.read().strip()
        else:
            # If VERSION file doesn't exist, write the current version
            with open(VERSION_FILE, 'w') as f:
                f.write("1.0.0")
            return "1.0.0"
    except Exception as e:
        print(f"Error reading version: {str(e)}")
        return "1.0.0"

def check_for_updates(current_version):
    """Check if updates are available"""
    result = {
        'update_available': False,
        'latest_version': current_version,
        'release_url': '',
        'release_notes': ''
    }
    
    try:
        # Make a request to the GitHub API
        response = requests.get(GITHUB_API_URL, timeout=5)
        response.raise_for_status()
        
        release_data = response.json()
        latest_version = release_data['tag_name'].lstrip('v')
        
        # Compare versions (simple string comparison, can be improved)
        if latest_version > current_version:
            result['update_available'] = True
            result['latest_version'] = latest_version
            result['release_url'] = release_data['html_url']
            result['release_notes'] = release_data['body']
        
        return result
    except Exception as e:
        print(f"Error checking for updates: {str(e)}")
        return result

def show_update_dialog(parent, latest_version, release_url):
    """Show a dialog informing the user about available updates"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Update Available")
    msg.setText(f"A new version ({latest_version}) of Stream Downloader is available.")
    msg.setInformativeText("Would you like to download the update?")
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    
    if msg.exec_() == QMessageBox.Yes:
        # Open the release URL in the default browser
        from PyQt5.QtGui import QDesktopServices
        from PyQt5.QtCore import QUrl
        QDesktopServices.openUrl(QUrl(release_url))

def update_version_file(new_version):
    """Update the VERSION file with a new version"""
    try:
        with open(VERSION_FILE, 'w') as f:
            f.write(new_version)
        return True
    except Exception as e:
        print(f"Error updating version file: {str(e)}")
        return False

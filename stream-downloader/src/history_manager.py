import os
import json
import datetime
from pathlib import Path

class HistoryManager:
    """Manages download history and user preferences"""
    
    def __init__(self, history_file=None):
        """Initialize the history manager"""
        if history_file is None:
            # Use default location in user's home directory
            self.history_file = os.path.join(str(Path.home()), '.stream_downloader_history.json')
        else:
            self.history_file = history_file
        
        self.history = self._load_history()
    
    def _load_history(self):
        """Load history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted or can't be read, return empty history
                return {"downloads": [], "preferences": {}}
        else:
            # Return empty history if file doesn't exist
            return {"downloads": [], "preferences": {}}
    
    def _save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            return True
        except IOError:
            return False
    
    def add_download(self, download_info):
        """Add a download to history"""
        # Add timestamp if not provided
        if "timestamp" not in download_info:
            download_info["timestamp"] = datetime.datetime.now().isoformat()
        
        # Add the download to the history
        self.history["downloads"].append(download_info)
        
        # Keep only the last 100 downloads
        if len(self.history["downloads"]) > 100:
            self.history["downloads"] = self.history["downloads"][-100:]
        
        # Save the updated history
        return self._save_history()
    
    def get_downloads(self, count=None, platform=None):
        """Get downloads from history, optionally filtered by platform"""
        downloads = self.history["downloads"]
        
        # Filter by platform if specified
        if platform:
            downloads = [d for d in downloads if d.get("platform") == platform]
        
        # Sort by timestamp, most recent first
        downloads = sorted(downloads, key=lambda d: d.get("timestamp", ""), reverse=True)
        
        # Return only the specified number if count is provided
        if count:
            return downloads[:count]
        else:
            return downloads
    
    def set_preference(self, key, value):
        """Set a user preference"""
        self.history["preferences"][key] = value
        return self._save_history()
    
    def get_preference(self, key, default=None):
        """Get a user preference"""
        return self.history["preferences"].get(key, default)
    
    def clear_history(self):
        """Clear download history"""
        self.history["downloads"] = []
        return self._save_history()
    
    def export_history(self, export_file):
        """Export history to a file"""
        try:
            with open(export_file, 'w') as f:
                json.dump(self.history["downloads"], f, indent=2)
            return True
        except IOError:
            return False
    
    def import_history(self, import_file):
        """Import history from a file"""
        try:
            with open(import_file, 'r') as f:
                imported_data = json.load(f)
            
            if isinstance(imported_data, list):
                # Merge the imported downloads with existing ones
                self.history["downloads"].extend(imported_data)
                
                # Remove duplicates based on URL and timestamp
                unique_downloads = {}
                for download in self.history["downloads"]:
                    key = f"{download.get('url', '')}-{download.get('timestamp', '')}"
                    unique_downloads[key] = download
                
                self.history["downloads"] = list(unique_downloads.values())
                
                # Sort by timestamp
                self.history["downloads"] = sorted(
                    self.history["downloads"], 
                    key=lambda d: d.get("timestamp", ""), 
                    reverse=True
                )
                
                # Keep only the last 100 downloads
                if len(self.history["downloads"]) > 100:
                    self.history["downloads"] = self.history["downloads"][-100:]
                
                # Save the updated history
                return self._save_history()
            else:
                return False
        except (json.JSONDecodeError, IOError):
            return False

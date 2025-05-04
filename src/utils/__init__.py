"""
Utility functions for Stream Downloader
"""

from src.utils.platform_utils import detect_platform, get_platform_qualities
from src.utils.history_manager import HistoryManager
from src.utils.updater import get_current_version, check_for_updates, UpdateChecker, show_update_dialog
from src.utils.spinner import Spinner

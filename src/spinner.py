import sys
import threading
import time
import itertools
from colorama import Fore, Style

class Spinner:
    def __init__(self, message="Loading...", delay=0.1, color=Fore.CYAN):
        """Initialize a new spinner with a message and delay between frames"""
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.delay = delay
        self.message = message
        self.running = False
        self.spinner_thread = None
        self.color = color
        
    def __enter__(self):
        """Start the spinner when used in a with statement"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the spinner when exiting a with statement"""
        self.stop()
        
    def start(self):
        """Start the spinner animation in a separate thread"""
        self.running = True
        sys.stdout.write('\n')  # Ensure spinner starts on a new line
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.daemon = True
        self.spinner_thread.start()
        
    def stop(self):
        """Stop the spinner animation"""
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join()
        sys.stdout.write('\r')
        sys.stdout.write(' ' * (len(self.message) + 10))  # Clear the line
        sys.stdout.write('\r')
        sys.stdout.flush()
    
    def update_message(self, message):
        """Update the spinner message while it's running"""
        self.message = message
        
    def _spin(self):
        """Internal method to display the spinner animation"""
        while self.running:
            frame = next(self.spinner)
            sys.stdout.write(f'\r{self.color}{frame} {self.message}{Style.RESET_ALL}')
            sys.stdout.flush()
            time.sleep(self.delay)

# Export the Spinner class for imports
__all__ = ['Spinner']

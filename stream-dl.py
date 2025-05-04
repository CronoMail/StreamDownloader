#!/usr/bin/env python
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli import main

if __name__ == "__main__":
    # Check if any arguments are provided
    if len(sys.argv) == 1:
        # No args provided, add the interactive flag
        sys.argv.append("--interactive")
    
    main()
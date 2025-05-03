@echo off
echo Starting Stream Downloader...
echo.
python src/main.py
if errorlevel 1 (
    echo.
    echo Error: Failed to start Stream Downloader.
    echo Please ensure Python and required dependencies are installed.
    echo See README.md for installation instructions.
    pause
)

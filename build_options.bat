@echo off
echo Stream Downloader Build Options
echo =================================
echo.
echo 1. Build without icon (recommended if having icon issues)
echo 2. Build with icon (requires valid icon file)
echo 3. Build with console window (for debugging)
echo 4. Exit
echo.

set /p option=Choose an option (1-4): 

if "%option%"=="1" (
    python -c "import re; with open('build.py', 'r') as f: content = f.read(); content = re.sub(r'icon=os\.path\.join.*', '# icon disabled', content); with open('build.py', 'w') as f: f.write(content)"
    python build.py
) else if "%option%"=="2" (
    python -c "import re; with open('build.py', 'r') as f: content = f.read(); content = re.sub(r'# icon disabled|# icon=os\.path\.join.*', 'icon=os.path.join(\'resources\', \'icon.ico\') if os.path.exists(os.path.join(\'resources\', \'icon.ico\')) else None,', content); with open('build.py', 'w') as f: f.write(content)"
    python build.py
) else if "%option%"=="3" (
    python -c "import re; with open('build.py', 'r') as f: content = f.read(); content = re.sub(r'console=False', 'console=True', content); with open('build.py', 'w') as f: f.write(content)"
    python build.py
    python -c "import re; with open('build.py', 'r') as f: content = f.read(); content = re.sub(r'console=True', 'console=False', content); with open('build.py', 'w') as f: f.write(content)"
) else if "%option%"=="4" (
    exit
) else (
    echo Invalid option. Please try again.
    pause
)

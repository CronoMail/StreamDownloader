@echo off
echo.
echo Stream Downloader - Build Menu
echo ============================
echo.
echo Select build type:
echo.
echo 1. Development Build (with console for debugging)
echo 2. Production Build (no console, ready for distribution)
echo 3. Exit
echo.

set /p choice=Enter your choice (1-3): 

if "%choice%"=="1" (
    echo.
    echo Starting development build (with console)...
    echo.
    python -c "import re; import os; content = open('fixed_build.py', 'r').read(); content = content.replace('--windowed', '--console'); with open('temp_build_script.py', 'w') as f: f.write(content); os.system('python temp_build_script.py'); os.remove('temp_build_script.py')"
) else if "%choice%"=="2" (
    echo.
    echo Starting production build (no console)...
    echo.
    python production_build.py
) else if "%choice%"=="3" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
    exit /b 1
)

echo.
if exist dist\StreamDownloader.exe (
    echo Build completed successfully!
    echo Executable is located at: %CD%\dist\StreamDownloader.exe
    echo.
    set /p run_now=Would you like to run the application now? (Y/N): 
    if /i "%run_now%"=="Y" (
        start "" "dist\StreamDownloader.exe"
    )
) else (
    echo Build may have failed, please check error messages above.
)
echo.

#!/usr/bin/env python3
import os
import sys
import glob
import subprocess
import shutil

def build_cli_executable():
    """Build a CLI-only standalone executable using PyInstaller for testing in Codespaces"""
    print("Building Stream Downloader CLI Executable...")
    
    # Install required dependencies
    dependencies = ["pyinstaller", "pillow"]
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "show", dep], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{dep} is already installed.")
        except subprocess.CalledProcessError:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
    
    # Make sure src is in the Python path
    sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
    
    # Clear the build and dist directories if they exist
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name} directory...")
            shutil.rmtree(dir_name)
    
    # Copy all source files to a temporary directory for packaging
    temp_dir = os.path.join(os.getcwd(), 'temp_build')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    os.makedirs(temp_dir)
    
    # Copy all .py files from src
    src_dir = os.path.join(os.getcwd(), 'src')
    for file in os.listdir(src_dir):
        if file.endswith('.py') or file.endswith('.qss'):
            shutil.copy(os.path.join(src_dir, file), os.path.join(temp_dir, file))
    
    # Create a simple entry point for PyInstaller
    entry_file = os.path.join(temp_dir, 'cli_app.py')
    with open(entry_file, 'w') as f:
        f.write("""
import os
import sys

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # Import the CLI module
    from cli import main
    
    # Run the CLI application
    if __name__ == "__main__":
        # Force interactive mode by default
        if len(sys.argv) == 1:
            sys.argv.append("--interactive")
        main()
except ImportError as e:
    print(f"Error importing CLI: {e}")
    sys.exit(1)
""")

    # Build the PyInstaller command
    pyinstaller_cmd = [
        sys.executable, 
        "-m", 
        "PyInstaller",
        "--clean",
        "--name=StreamDownloaderCLI", 
        "--onefile",
        "--console",  # Show console window for CLI version
    ]
    
    # Add data files
    if os.name == 'nt':  # Windows
        pyinstaller_cmd.extend([
            "--add-data", f"{os.path.join(temp_dir, '*.py')};.",
            "--add-data", f"{os.path.join(temp_dir, 'style.qss')};.",
            "--add-data", f"{os.path.join(temp_dir, 'style_dark.qss')};.",
        ])
    else:  # Linux/Mac
        # Add each .py file individually
        for py_file in glob.glob(os.path.join(temp_dir, '*.py')):
            pyinstaller_cmd.extend(["--add-data", f"{py_file}:."])
        # Add style files
        if os.path.exists(os.path.join(temp_dir, 'style.qss')):
            pyinstaller_cmd.extend(["--add-data", f"{os.path.join(temp_dir, 'style.qss')}:."])
        if os.path.exists(os.path.join(temp_dir, 'style_dark.qss')):
            pyinstaller_cmd.extend(["--add-data", f"{os.path.join(temp_dir, 'style_dark.qss')}:."])
    
    # Add imports
    pyinstaller_cmd.extend([
        "--hidden-import=history_manager",
        "--hidden-import=stream_downloader",
        "--hidden-import=stream_merger",
        "--hidden-import=updater",
        "--hidden-import=inquirer",
        "--hidden-import=colorama",
        "--paths", os.path.join(sys.prefix, "Lib", "site-packages"),
        "--paths", temp_dir,
    ])
    
    # Add the entry file
    pyinstaller_cmd.append(entry_file)
    
    print("Running PyInstaller with the following command:")
    print(" ".join(pyinstaller_cmd))
    
    subprocess.check_call(pyinstaller_cmd)
    
    # Clean up temporary files
    shutil.rmtree(temp_dir)
    
    if os.name == 'nt':
        exe_path = os.path.join('dist', 'StreamDownloaderCLI.exe')
    else:
        exe_path = os.path.join('dist', 'StreamDownloaderCLI')
    
    print("\nCLI Build Complete!")
    print(f"Executable created: {exe_path}")
    print("This is a CLI-only version built for testing in environments without GUI support.")
    
    # Make the file executable
    if os.name != 'nt':
        os.chmod(exe_path, 0o755)
        print(f"Made {exe_path} executable")

if __name__ == "__main__":
    build_cli_executable()

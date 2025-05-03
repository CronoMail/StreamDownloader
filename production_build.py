import os
import sys
import subprocess
import shutil

def build_executable():
    """Build a production-ready standalone executable using PyInstaller"""
    print("Building Stream Downloader Production Executable...")
    
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
    entry_file = os.path.join(temp_dir, 'app.py')
    with open(entry_file, 'w') as f:
        f.write("""
import os
import sys
import glob

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # Import the main module
    import main
    
    # Run the application
    if __name__ == "__main__":
        main.main()
except ImportError as e:
    print(f"Error importing main: {e}")
    sys.exit(1)
""")
    
    # Try to use a valid icon if available
    icon_path = None
    if os.path.exists(os.path.join('resources', 'icon.ico')):
        # Verify the icon is valid
        try:
            from PIL import Image
            Image.open(os.path.join('resources', 'icon.ico'))
            icon_path = os.path.join('resources', 'icon.ico')
            print("Using icon file:", icon_path)
        except:
            print("Icon file exists but is not valid. Building without an icon.")

    # Build the PyInstaller command
    pyinstaller_cmd = [
        sys.executable, 
        "-m", 
        "PyInstaller",
        "--clean",
        "--name=StreamDownloader", 
        "--onefile",
        "--windowed",  # No console window in production
        "--add-data", f"{os.path.join(temp_dir, '*.py')}{';.' if os.name == 'nt' else ':'}",
        "--add-data", f"{os.path.join(temp_dir, 'style.qss')}{';.' if os.name == 'nt' else ':'}",
        "--add-data", f"{os.path.join(temp_dir, 'style_dark.qss')}{';.' if os.name == 'nt' else ':'}",
        "--hidden-import=history_manager",
        "--hidden-import=stream_downloader",
        "--hidden-import=stream_merger",
        "--hidden-import=updater",
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--paths", os.path.join(sys.prefix, "Lib", "site-packages"),
        "--paths", temp_dir,
    ]
    
    # Add icon if available
    if icon_path:
        pyinstaller_cmd.extend(["--icon", icon_path])
    
    # Add the entry file
    pyinstaller_cmd.append(entry_file)
    
    print("Running PyInstaller with the following command:")
    print(" ".join(pyinstaller_cmd))
    
    subprocess.check_call(pyinstaller_cmd)
    
    # Clean up temporary files
    shutil.rmtree(temp_dir)
    
    print("\nProduction Build Complete!")
    print(f"Executable created: {os.path.join('dist', 'StreamDownloader.exe')}")
    print("This version has no console window and is ready for distribution.")

if __name__ == "__main__":
    build_executable()

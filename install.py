import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    try:
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Error installing dependencies. Please install them manually with:")
        print("pip install -r requirements.txt")
        return False

def create_icon():
    """Create the icon file from base64 data"""
    print("Creating icon file...")
    
    try:
        # Run the create_icon.py script
        subprocess.check_call([sys.executable, "create_icon.py"])
        return True
    except subprocess.CalledProcessError:
        print("Error creating icon file.")
        return False

def create_desktop_shortcut():
    """Create a desktop shortcut for the application"""
    print("Creating desktop shortcut...")
    
    home_dir = str(Path.home())
    desktop_dir = os.path.join(home_dir, "Desktop")
    
    if not os.path.exists(desktop_dir):
        print("Desktop directory not found.")
        return False
    
    try:
        if platform.system() == "Windows":
            # Create a .bat file shortcut
            shortcut_path = os.path.join(desktop_dir, "Stream Downloader.bat")
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bat_content = f'@echo off\ncd /d "{script_dir}"\npython src\\main.py\n'
            
            with open(shortcut_path, "w") as f:
                f.write(bat_content)
                
        elif platform.system() == "Linux":
            # Create a .desktop file
            shortcut_path = os.path.join(desktop_dir, "stream-downloader.desktop")
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "resources", "icon.ico")
            
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=Stream Downloader
Comment=Download streams from Twitch and YouTube
Exec=python {script_dir}/src/main.py
Icon={icon_path}
Terminal=false
Categories=Utility;Network;
"""
            
            with open(shortcut_path, "w") as f:
                f.write(desktop_content)
                
            # Make it executable
            os.chmod(shortcut_path, 0o755)
            
        else:
            print(f"Creating desktop shortcut not supported on {platform.system()}")
            return False
            
        print(f"Shortcut created at: {shortcut_path}")
        return True
    except Exception as e:
        print(f"Error creating desktop shortcut: {str(e)}")
        return False

def run_installer():
    """Run the installation process"""
    print("=== Stream Downloader Installer ===")
    print("")
    
    # Install dependencies
    if not install_dependencies():
        answer = input("Continue anyway? (y/n): ")
        if answer.lower() != 'y':
            return
    
    # Create icon
    create_icon()
    
    # Ask to create desktop shortcut
    answer = input("Create desktop shortcut? (y/n): ")
    if answer.lower() == 'y':
        create_desktop_shortcut()
    
    print("\nInstallation complete!")
    print("You can now run the application with:")
    print("  python src/main.py")
    print("or by using the run.bat file on Windows")
    
    # Ask to run the application
    answer = input("Run the application now? (y/n): ")
    if answer.lower() == 'y':
        if platform.system() == "Windows":
            os.system("run.bat")
        else:
            os.system("python src/main.py")

if __name__ == "__main__":
    run_installer()

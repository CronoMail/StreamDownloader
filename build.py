import os
import sys
import subprocess

def build_executable():
    """Build a standalone executable using PyInstaller"""
    print("Building Stream Downloader executable...")
    
    # Install PyInstaller if not already installed
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "show", "pyinstaller"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("PyInstaller is already installed.")
    except subprocess.CalledProcessError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Create spec file
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/style.qss', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='StreamDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' if os.path.exists('resources/icon.ico') else None,
)
"""
    
    with open("StreamDownloader.spec", "w") as f:
        f.write(spec_content)
    
    # Create resources directory if it doesn't exist
    if not os.path.exists("resources"):
        os.makedirs("resources")
    
    # Run PyInstaller
    subprocess.check_call([
        sys.executable, 
        "-m", 
        "PyInstaller", 
        "--clean",
        "StreamDownloader.spec"
    ])
    
    print("Build complete!")
    print(f"Executable created: {os.path.join('dist', 'StreamDownloader.exe')}")

if __name__ == "__main__":
    build_executable()

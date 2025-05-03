
# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(    [os.path.join('src', 'main.py')],
    pathex=[os.path.join('.')],
    binaries=[],    datas=[
           (os.path.join('src', 'style.qss'), '.'), 
           (os.path.join('src', 'style_dark.qss'), '.'),
           (os.path.join('src', 'history_manager.py'), 'src'),
           (os.path.join('src', 'stream_downloader.py'), 'src'),
           (os.path.join('src', 'stream_merger.py'), 'src'),
           (os.path.join('src', 'updater.py'), 'src')
    ],
    hiddenimports=['history_manager', 'stream_downloader', 'stream_merger', 'updater'],
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
    runtime_tmpdir=None,    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Temporarily disabled icon due to format issues
    # icon=os.path.join('resources', 'icon.ico') if os.path.exists(os.path.join('resources', 'icon.ico')) else None,
)

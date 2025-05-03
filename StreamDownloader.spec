# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\rimmi\\Downloads\\ef\\temp_build\\app.py'],
    pathex=['C:\\Users\\rimmi\\Downloads\\ef\\.venv\\Lib\\site-packages', 'C:\\Users\\rimmi\\Downloads\\ef\\temp_build'],
    binaries=[],
    datas=[('C:\\Users\\rimmi\\Downloads\\ef\\temp_build\\*.py', '.'), ('C:\\Users\\rimmi\\Downloads\\ef\\temp_build\\style.qss', '.'), ('C:\\Users\\rimmi\\Downloads\\ef\\temp_build\\style_dark.qss', '.')],
    hiddenimports=['history_manager', 'stream_downloader', 'stream_merger', 'updater', 'PyQt5', 'PyQt5.QtWidgets', 'PyQt5.QtCore', 'PyQt5.QtGui'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
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
)

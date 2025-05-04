# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/workspaces/StreamDownloader/temp_build/cli_app.py'],
    pathex=['/usr/local/python/3.12.1/Lib/site-packages', '/workspaces/StreamDownloader/temp_build'],
    binaries=[],
    datas=[('/workspaces/StreamDownloader/temp_build/history_manager.py', '.'), ('/workspaces/StreamDownloader/temp_build/stream_downloader.py', '.'), ('/workspaces/StreamDownloader/temp_build/cli_app.py', '.'), ('/workspaces/StreamDownloader/temp_build/stream_merger.py', '.'), ('/workspaces/StreamDownloader/temp_build/spinner.py', '.'), ('/workspaces/StreamDownloader/temp_build/cli_help.py', '.'), ('/workspaces/StreamDownloader/temp_build/updater.py', '.'), ('/workspaces/StreamDownloader/temp_build/__init__.py', '.'), ('/workspaces/StreamDownloader/temp_build/cli.py', '.'), ('/workspaces/StreamDownloader/temp_build/main.py', '.'), ('/workspaces/StreamDownloader/temp_build/style.qss', '.'), ('/workspaces/StreamDownloader/temp_build/style_dark.qss', '.')],
    hiddenimports=['history_manager', 'stream_downloader', 'stream_merger', 'updater', 'inquirer', 'colorama'],
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
    name='StreamDownloaderCLI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

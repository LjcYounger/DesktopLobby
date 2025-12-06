# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['D:\\Projects\\DesktopLobby2.0'],
    binaries=[],
    datas=[],
    hiddenimports=['llama_cpp', 'openai', 'pygame.mixer', 'removeRemoteImage'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'pygame.image', 'pygame.font', 'pygame.draw', 'PySide6.Qt3DCore', 'PySide6.Qt3DExtras', 'PySide6.QtBluetooth', 'PySide6.QtCharts', 'PySide6.QtDataVisualization', 'PySide6.QtLocation', 'PySide6.QtMultimedia', 'PySide6.QtNfc', 'PySide6.QtQuick', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'pygame.examples'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DesktopLobby',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='DesktopLobby',
)

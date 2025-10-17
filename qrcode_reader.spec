# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Find pyzbar DLL files
pyzbar_path = os.path.join(sys.prefix, 'Lib', 'site-packages', 'pyzbar')
pyzbar_dlls = [
    (os.path.join(pyzbar_path, 'libiconv.dll'), 'pyzbar'),
    (os.path.join(pyzbar_path, 'libzbar-64.dll'), 'pyzbar'),
]

a = Analysis(
    ['qrcode_reader.py'],
    pathex=[],
    binaries=pyzbar_dlls,
    datas=[('asset/icon.png', 'asset')],
    hiddenimports=['pyzbar.pyzbar', 'PIL._tkinter_finder', 'winotify'],
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
    name='WinQRCodeReader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="asset/icon.png",  # You can add an .ico file here later
)

# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

tk_datas = collect_data_files('tkinter')
tk_binaries = collect_dynamic_libs('tkinter')

a = Analysis(
    ['convert_mrgb_v5.py'],
    pathex=[],
    binaries=tk_binaries,
    datas=tk_datas,
    hiddenimports=[
        'tkinter', '_tkinter',
        'tkinter.ttk', 'tkinter.scrolledtext',
        'tkinter.filedialog', 'tkinter.messagebox',
    ],
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
    name='MRGB_Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

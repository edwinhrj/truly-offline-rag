# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Acer\\OneDrive\\Documents\\GitHub\\rag_pipeline\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Acer\\OneDrive\\Documents\\GitHub\\rag_pipeline\\frontend\\dist', 'frontend/dist'), ('C:\\Users\\Acer\\OneDrive\\Documents\\GitHub\\rag_pipeline\\backend', 'backend'), ('C:\\Users\\Acer\\OneDrive\\Documents\\GitHub\\rag_pipeline\\backend\\pdf_helper\\vec0.dll', 'backend/pdf_helper')],
    hiddenimports=['requests', 'psutil', 'cryptography', 'cryptography.hazmat.backends.openssl'],
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
    name='Imandiao企业私有大模型',
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
    icon=['C:\\Users\\Acer\\OneDrive\\Documents\\GitHub\\rag_pipeline\\packaging\\icon.ico'],
)

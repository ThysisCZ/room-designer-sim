block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('server/*.js', 'server'),
        ('server/routes/*.js', 'server/routes'),
        ('server/src', 'server/src'),
        ('server/node_modules', 'server/node_modules'),
        ('server/package.json', 'server'),
        ('ithaca.ttf', '.'),
        ('storage', 'storage')
    ],
    hiddenimports=[
        'requests',
        'psutil',
        'pygame',
        'threading',
        'subprocess',
        'traceback'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RoomDesignerSimulator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
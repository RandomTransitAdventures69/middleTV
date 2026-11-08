# PyInstaller spec for MiddleTV.
# Run: .venv/bin/pyinstaller --noconfirm --clean MiddleTV.spec
# On macOS this produces dist/MiddleTV.app (and a console-free app bundle).
# A Windows .exe must be built on Windows (PyInstaller does not cross-compile).

from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None
root = Path(SPECPATH)

datas = [
    (str(root / 'config'), 'config'),
    (str(root / 'profiles'), 'profiles'),
    (str(root / 'faq'), 'faq'),
    (str(root / 'reference images (for kilo code)'), 'reference images (for kilo code)'),
]
for name in ('defaultUI.png', 'aeroplane.jpg', 'matrix.png', 'readme.md'):
    p = root / name
    if p.exists():
        datas.append((str(p), '.'))

binaries = []
hiddenimports = collect_submodules('apps') + collect_submodules('core') + [
    'PySide6.QtWebEngineCore',
    'PySide6.QtWebEngineWidgets',
    'PySide6.QtMultimedia',
    'PySide6.QtMultimediaWidgets',
    'PySide6.QtNetwork',
]

for pkg in ('PySide6',):
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

a = Analysis(
    ['main.py'],
    pathex=[str(root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='MiddleTV',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='MiddleTV',
)
app = BUNDLE(
    coll,
    name='MiddleTV.app',
    icon=None,
    bundle_identifier='org.middletv.launcher',
)

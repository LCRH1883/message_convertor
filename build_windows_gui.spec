# PyInstaller spec for Windows GUI onefile
from PyInstaller.utils.hooks import collect_data_files

ICON_PATH = 'branding/msgsecure_logo.ico'

# 1) normal data collection (will still warn until __init__.py exists)
datas = collect_data_files('mailcombine', includes=['resources/win64/*'], include_py_files=True)

# 2) HARD include the entire directory (bullet-proof)
datas = datas + [('mailcombine/resources/win64', 'mailcombine/resources/win64')]

a = Analysis(
    ['mailcombine/gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,                 # <== MUST be present
    hiddenimports=[],
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='msgsecure-win-gui',
    console=False,
    onefile=True,
    icon=ICON_PATH
)


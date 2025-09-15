# PyInstaller spec for Linux GUI (onefile/onedir)
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('mailcombine', includes=['resources/linux64/*'], include_py_files=False)

a = Analysis(
    ['mailcombine/gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
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
    name='msgsecure-linux-gui',
    console=False,   # GUI app
    onefile=False
)

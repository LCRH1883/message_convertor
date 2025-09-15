# PyInstaller spec for Windows CLI build
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('mailcombine', includes=['resources/win64/*'], include_py_files=False)

a = Analysis(
    ['mailcombine/cli.py'],
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
    name='mail-combine-win',
    console=True,  # set False for GUI builds later
    onefile=True
)

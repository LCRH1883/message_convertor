# PyInstaller spec for Linux CLI build
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('mailcombine', includes=['resources/linux64/*'], include_py_files=False)

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
    name='mail-combine-linux',
    console=True,
    onefile=True
)

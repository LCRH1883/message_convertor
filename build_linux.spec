# PyInstaller spec for Linux CLI build
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('mailcombine', includes=['resources/linux64/*'], include_py_files=False)
if not datas:
    spec_path = globals().get('__file__') or Path.cwd() / 'build_linux.spec'
    root = Path(spec_path).resolve().parent
    resource_root = root / 'mailcombine' / 'resources' / 'linux64'
    if resource_root.is_dir():
        for item in resource_root.iterdir():
            if item.is_file():
                rel = f"mailcombine/resources/linux64/{item.name}"
                datas.append((str(item), rel))

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

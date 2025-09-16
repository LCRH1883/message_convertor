# PyInstaller spec for Linux GUI (onefile/onedir)
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

# include embedded PST binary (fallback to manual path when running from source checkout)
datas = collect_data_files('mailcombine', includes=['resources/linux64/*'], include_py_files=False)
if not datas:
    spec_path = globals().get('__file__') or Path.cwd() / 'build_linux_gui.spec'
    root = Path(spec_path).resolve().parent
    resource_root = root / 'mailcombine' / 'resources' / 'linux64'
    if resource_root.is_dir():
        for item in resource_root.iterdir():
            if item.is_file():
                rel = f"mailcombine/resources/linux64/{item.name}"
                datas.append((str(item), rel))

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
    name='msgsecure-linux-gui',  # final binary name
    console=False,               # windowed build
    onefile=True
)

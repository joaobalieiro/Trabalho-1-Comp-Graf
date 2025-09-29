# build.spec — PySide6 + OpenGL (QOpenGLWidget) robusto
# Gera app GUI (sem console) com todos os plugins/binaries do PySide6.
# Executar:  pyinstaller -y --clean build.spec

from PyInstaller.utils.hooks import collect_all
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
import os

app_name = "PolyFill"
entry_script = "app.py"
icon_path = "assets/app.ico"

# Coleta completa de PySide6 e shiboken6 (plugins, dlls, qml, etc.)
datas, binaries, hiddenimports = [], [], []
for m in ("PySide6", "shiboken6"):
    d, b, h = collect_all(m)
    datas += d
    binaries += b
    hiddenimports += h

# Opcional: garantir módulos Qt usados
hiddenimports += [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtOpenGLWidgets",
]

# Análise
a = Analysis(
    [entry_script],
    pathex=[os.getcwd()],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Executável GUI (sem console)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # se tiver UPX instalado, compacta mais
    console=False,      # GUI app
    icon=icon_path if os.path.exists(icon_path) else None,
)

# Coletar em pasta onedir (mais fácil de depurar). Se quiser onefile, comente COLLECT e use apenas EXE.
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name=app_name,
)

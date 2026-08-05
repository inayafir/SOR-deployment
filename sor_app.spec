# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build specification for the CHSS SOR intranet application.

Produces a single standalone ``Application.exe`` containing the embedded
Python runtime, Flask, Waitress, templates, static assets and the seed CSV.
All runtime data (database, logs, config, uploads, exports, backups) is kept
outside the executable, next to it, so data persists across restarts.
"""

import os

# Everything under the project root (parent of the build directory).
project_root = os.path.abspath(os.path.join(os.getcwd()))

a = Analysis(
    ["app.py"],
    pathex=[project_root],
    binaries=[],
    datas=[
        ("templates", "templates"),
        ("static", "static"),
        ("chss_sor_2023.csv", "."),
    ],
    hiddenimports=["waitress"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "numpy", "matplotlib", "PIL", "IPython", "jedi", "parso",
        "PyQt5", "PySide2", "tkinter", "cryptography", "bcrypt",
        "psutil", "pygments", "chardet", "certifi", "dateutil",
        "pandas", "scipy", "pywin32", "win32com", "gi",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Application",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
)

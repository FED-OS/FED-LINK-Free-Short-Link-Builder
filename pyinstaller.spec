# FED-LINk — PyInstaller spec for the desktop app.
#
# Built by .github/workflows/build-desktop.yml on Windows, macOS and
# Linux, and locally with `pyinstaller pyinstaller.spec`.
#
#   Windows: dist/FED-LINk.exe         (artifact "FED-LINk-Windows")
#   macOS:   dist/FED-LINk.app         (artifact "FED-LINk-macOS")
#   Linux:   dist/FED-LINk             (artifact "FED-LINk-Linux")
#
# The entry point is the shared CLI/GUI module src/main.py, so one
# executable covers both front ends: run it with a subcommand for the
# CLI, or launch it bare in a desktop session for the Tkinter GUI.
#
# Icons are optional: the spec falls back to icon=None when
# assets/icon.ico / assets/icon.icns / assets/icon.png are missing, so
# a fresh checkout still builds (BUILD.md documents this).

import os
import sys

# Repository root (the spec lives at the repo root, so it is the spec's
# own directory regardless of how PyInstaller was invoked).
ROOT = os.path.dirname(os.path.abspath(SPEC))

# Icon per platform, optional — None keeps the build working on fresh
# checkouts where assets/ has not been generated yet.
if sys.platform == "win32":
    _icon_path = os.path.join(ROOT, "assets", "icon.ico")
elif sys.platform == "darwin":
    _icon_path = os.path.join(ROOT, "assets", "icon.icns")
else:
    _icon_path = os.path.join(ROOT, "assets", "icon.png")
icon = _icon_path if os.path.exists(_icon_path) else None


a = Analysis(
    ["src/main.py"],
    pathex=[ROOT],
    binaries=[],
    datas=[
        # The generator falls back to embedded templates, but shipping
        # the repo's templates and configs keeps generated pages
        # identical to a normal repo build.
        (os.path.join(ROOT, "templates"), "templates"),
        (os.path.join(ROOT, "configs"), "configs"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Keep the executable lean; nothing in the core needs these.
        "matplotlib",
        "unittest",
        "xml.dom",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FED-LINk",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # the CLI is a first-class front end; the GUI also works
    icon=icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="FED-LINk",
)

# macOS: wrap the collected bundle into FED-LINk.app, which the
# build-desktop.yml workflow locates at dist/FED-LINk.app.
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        exe,
        name="FED-LINk.app",
        icon=icon,
        bundle_identifier="com.fedpromptly.fedlink",
        info_plist={
            "CFBundleDisplayName": "FED-LINk",
            "CFBundleShortVersionString": "1.1.0",
            "CFBundleVersion": "1.1.0",
        },
    )

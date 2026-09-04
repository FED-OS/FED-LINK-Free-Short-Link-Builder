[app]
# FED-LINk — Buildozer spec for the Android app.
#
# Built by .github/workflows/build-android.yml with `buildozer -v android
# debug` (output: bin/*.apk, artifact "FED-LINk-Android") and locally with
# the same command on Linux/WSL.
#
# The APK packages the Kivy front end of the shared engine: src/main.py
# detects Kivy at runtime (guarded import) and runs the mobile UI when
# present, the CLI/Tkinter paths on desktop hosts. requirements =
# python3,kivy ships both halves; see ADR-0008 for the front-end design.

title = FED-LINk
package.name = FED-LINk
package.domain = com.fedpromptly

# Whole repo as source dir so configs/ and templates/ ship inside the
# APK; the exclude list prunes everything the app does not need.
source.dir = .
source.include_exts = py,png,jpg,j2,json,csv,yaml,yml,html,css,js

# Entry point (relative to source.dir).
source.main = src/main.py

source.exclude_dirs = tests,docs,scripts,examples,wiki,prompts,discussion,public,.github,.vscode,output,build,dist,logs

requirements = python3,kivy

orientation = all

# Versioning: fixed at 1.1.0 for the tagged releases this spec ships with;
# bump in lockstep with pyproject.toml and CHANGELOG.md.
version = 1.1.0

icon.filename = %(source.dir)s/assets/icon.png

presplash.filename = %(source.dir)s/assets/icon.png
presplash.color = #0f1115

# Fullscreen off so the Android status bar is visible; the Kivy UI is
# form-based, not a game.
fullscreen = 0

# Permissions: none. The generator runs fully offline (ADR-0001,
# NOTICE.md "no data collection"); the APK needs no network, storage or
# sensor permissions at all.
android.permissions =

# APK metadata
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = False

# Buildozer housekeeping
build_dir = build
userbuild_dir = .buildozer
bin_dir = bin

[buildozer]
log_level = 2
warn_on_root = 1

# vim: set ft=conf:

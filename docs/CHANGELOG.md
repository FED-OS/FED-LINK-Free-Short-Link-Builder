# Changelog

All notable changes to FED-LINk are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
uses [Semantic Versioning](https://semver.org/).

## [1.1.0] — 2026-09-04

### Added
- `check` subcommand: live HEAD requests against every deployed short
  link, comparing redirect targets with the links file. Verdicts are
  `ok`, `wrong-target`, `no-redirect` and `error`; exits non-zero when
  any link is unhealthy. Standard library only, `--timeout` supported.
- `--strict-case` flag: mixed-case slugs are rejected instead of
  silently lower-cased (links file as literal source of truth).
- `build --dry-run`: full preview of create/update/keep actions, stale
  folders and support-file rewrites, without touching disk.
- `--format json` on `validate`, `list`, `check` and `build --dry-run`.
- `FolderCreator.plan()` plus `build_check_url`, `evaluate_redirect`,
  `check_links` and `CheckResult` public APIs.
- 30 new tests (63 → 93).

### Changed
- Version bumped to 1.1.0 (engine, pyproject, PyInstaller/Buildozer
  specs, Docker labels).

## [1.0.0] — 2026-09-04

### Added
- Core generator: redirect folders, `.htaccess` (301 rules + 404
  fallback), `404.html` and a `links.json` manifest per build.
- Parsers for JSON, YAML and CSV links files, including urlzap-style
  `links: [{path, url}]` layouts.
- Validators for slugs, URLs and duplicate detection with clear,
  entry-numbered error messages.
- CLI: `build`, `validate`, `list`, `generate-htaccess`, plus
  `--site-domain`, `--home-url`, `--page-template`,
  `--htaccess-template`, `--no-zip`, `--no-clean`, `--allow-private`.
- Tkinter desktop app (no-args launch) and PyInstaller specs for
  Windows/macOS/Linux builds.
- Kivy/Buildozer Android front end and `build-android` workflow.
- Streamlit dashboard for browser-based link management.
- GitHub Actions: 19 workflows covering build, test, CI/CD, releases,
  publishing, Pages deployments, CodeQL, dependency review, Scorecards,
  labelling, greetings and stale management.
- Docker image and compose stack for containerised builds.
- Project scaffolding: templates, examples, docs site, tests (63
  passing), labels, issue/PR templates and community health files.

### Fixed
- `.htaccess` fallback template now uses `{{redirects}}` double-brace
  placeholder syntax, matching the renderer.
- JSON/YAML parsers accept `links` as either a mapping or a list.
- Reserved-word list trimmed to server/fallback paths only, so slugs
  like `docs` and `blog` are valid short links.

## [0.1.0] — 2026-08-30

### Added
- Initial prototype: manual `_template` folder copies on InfinityFree.

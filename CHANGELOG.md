# Changelog

All notable changes to FED-LINk are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
uses [Semantic Versioning](https://semver.org/).

The full documentation-site copy lives at
[docs/CHANGELOG.md](docs/CHANGELOG.md); this file is the authoritative
root record.

## [1.1.0] — 2026-09-04

### Added
- `check` subcommand: live HEAD requests against every *deployed* short
  link, comparing the redirect target with the links file and reporting
  `ok` / `wrong-target` / `no-redirect` / `error` verdicts. Uses only
  the standard library (no redirects followed), accepts `--timeout`,
  and exits non-zero when any link is unhealthy — ready for CI.
- `--strict-case` flag on `build`, `validate`, `list`, `check` and
  `generate-htaccess`: mixed-case slugs are rejected instead of being
  silently lower-cased, so the links file becomes the literal source of
  truth.
- `build --dry-run`: previews which slug pages would be created,
  updated or kept, which folders are stale (removed on a real build) and
  which support files (`404.html`, `.htaccess`, `links.json`) would be
  rewritten — without writing a single file.
- `--format json` on `validate`, `list`, `check` and `build --dry-run`
  for machine-readable output that scripts and workflows can consume.
- `FolderCreator.plan()` API behind `--dry-run`, plus
  `build_check_url`, `evaluate_redirect`, `check_links` and
  `CheckResult` in `src.validators` for programmatic health checks.
- 30 new tests (63 → 93) covering strict-case, every live-check branch
  via an injectable fake fetcher, and every `plan()` outcome.

### Changed
- Version bumped to 1.1.0 across the engine, `pyproject.toml`,
  PyInstaller/Buildozer specs and Docker labels.

## [1.0.0] — 2026-09-04

### Added
- Core generator: redirect folders, `.htaccess` with `Redirect 301`
  rules and a 404 fallback, branded `404.html`, and a `links.json`
  manifest per build.
- Parsers for JSON, YAML and CSV links files, including urlzap-style
  `links: [{path, url}]` layouts and plain `{slug: url}` mappings.
- Validators with clear, entry-numbered errors: slug character/length
  rules, reserved slugs, absolute http(s) URLs only, duplicate detection.
- CLI (`python -m src.main`) with `build`, `validate`, `list` and
  `generate-htaccess` commands and the `--site-domain`, `--home-url`,
  `--page-template`, `--htaccess-template`, `--no-zip`, `--no-clean`,
  `--allow-private` flags.
- Tkinter desktop app launched with no arguments; PyInstaller spec and
  cross-platform `Build Desktop` workflow.
- Kivy/Buildozer Android front end with `buildozer.spec` and the
  `Build Android` workflow.
- Streamlit dashboard for browser-based link management with live
  validation and `.htaccess` preview.
- 19 GitHub Actions workflows: build, test, CI, CD, deploy,
  deploy-pages, pages, release, publish, pr, stale, labeler, greetings,
  codeql, main, dependency-review, scorecards, build-desktop,
  build-android.
- Docker image and compose stack for containerised builds.
- Documentation site (docs/), examples (basic, advanced, dashboard),
  63-test suite, labels taxonomy and all community health files.

### Fixed
- `.htaccess` fallback template now uses the `{{redirects}}`
  double-brace placeholder the renderer expects.
- JSON/YAML parsers accept the `links` key holding either a mapping or a
  list, so both config styles ship in the box.
- Reserved slug list trimmed to genuine server/fallback paths only —
  `docs` and `blog` are valid short links again.

## [0.1.0] — 2026-08-30

### Added
- Initial prototype: manual `_template` folder copies deployed to
  InfinityFree.

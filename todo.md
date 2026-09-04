# FED-LINk Project TODO

Working checklist for the FED-LINk project itself. Check items off as they
are done; add new ones at the bottom of the matching section. This file is
project maintenance notes — it is not the development plan (that's
[`ROADMAP.md`](ROADMAP.md)).

## Core

- [x] URL/slug validators with strict rules and reserved words
- [x] JSON parser (mapping, wrapper object, urlzap-style list shapes)
- [x] YAML parser (same shapes, deferred PyYAML import)
- [x] CSV parser (header aliases slug/path/short/code + url/target/destination/link)
- [x] `load_links` dispatcher picked by file extension
- [x] HTML redirect builder (meta-refresh + JS fallback + visible link)
- [x] 404 page builder
- [x] Manifest (links.json) builder
- [x] Folder creator with clean-first generation (`.keep` survives)
- [x] Deterministic ZIP packager
- [x] Logger and file cleaner utilities
- [x] CLI (`build`, `validate`, `list`, `generate-htaccess`)
- [x] Tkinter GUI front end
- [x] Kivy/Android front end support via `src/main.py` entry

## Configuration

- [x] `configs/links.json` with 10 live links
- [x] `configs/links.yaml` mirror
- [x] `configs/links.csv.example`
- [x] `configs/.htaccess.template`
- [x] `configs/redirects.map` (future RewriteMap path)

## Templates

- [x] `templates/index.html.j2` redirect page template
- [x] `templates/404.html`
- [x] `templates/fallback.html`

## Testing

- [x] 93 pytest tests across parsers, validators, generator, packaging,
      dry-run planning, and the offline live-check layer
- [x] Byte-exact fixture test for generated `index.html`
- [x] Smoke build verified (10 Redirect 301 rules, ZIP contents checked)

## CI/CD

- [x] 19 GitHub Actions workflows (build, test matrix, CI/CD, Pages,
      releases, PyPI, desktop, Android, CodeQL, Scorecards, housekeeping)
- [x] Issue templates, PR template, labels config
- [x] DISCUSSIONS welcome README

## Documentation

- [x] Root doc suite (README, INSTALL, BUILD, DEPLOYMENT, FAQ, ROADMAP,
      ADR, SECURITY, SUPPORT, SUMMARY, and the rest)
- [x] `docs/` set (index, installation, usage, configuration, deployment,
      api, contributing, CHANGELOG)
- [x] Examples (basic, advanced, streamlit dashboard)

## Pending / next up

- [ ] Rotate `docs/images/` screenshots after the next visual refresh
- [x] Wire the `check` subcommand (live HEAD requests) — shipped in 1.1.0
- [x] Add `--strict-case` flag — shipped in 1.1.0
- [x] Add `--dry-run` diff and `--format json` output — shipped in 1.1.0
- [ ] Incremental FTP/SFTP deploy from `.env` credentials — ROADMAP v1.2
- [ ] QR codes for every slug via Pillow — ROADMAP v1.3
- [ ] Per-link overrides and `themes/` — ROADMAP v1.3

## Shipped in 1.1.0 (2026-09-04)

- [x] `check` subcommand with live HEAD verification of deployed links
- [x] `--strict-case` flag on build/validate/list/check/generate-htaccess
- [x] `build --dry-run` with `FolderCreator.plan()` create/update/keep/stale preview
- [x] `--format json` on validate/list/check and `build --dry-run`
- [x] Public check APIs: `build_check_url`, `evaluate_redirect`,
      `check_links`, `CheckResult`
- [x] Test suite grown 63 → 93 (strict-case, check branches, plan outcomes)

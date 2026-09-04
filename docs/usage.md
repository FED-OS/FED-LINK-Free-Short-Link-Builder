# Usage

## The five CLI commands

All commands accept `--site-domain` and `--home-url` to override the
defaults (`link.fedpromptly.com` / `https://fedpromptly.com`), plus the
shared flags `--allow-private` (permit localhost URLs while testing),
`--strict-case` (reject mixed-case slugs instead of lower-casing them)
and, where output makes sense, `--format {text,json}` for
machine-readable results.

### validate — check a links file

```bash
python -m src.main validate configs/links.json
```

Prints `OK: 10 link(s) valid` or a message pointing at the broken entry.
Use `--allow-private` to permit localhost URLs while testing. With
`--format json` the result is `{"ok": true, "count": 10, "links": {...}}`
or `{"ok": false, "error": "..."}` — handy for CI gates.

### build — generate the bundle

```bash
python -m src.main build configs/links.json --output output --zip links.zip
```

Writes `output/<slug>/index.html` per link plus `.htaccess`, `404.html`
and `links.json`, then packages everything into `links.zip`. Useful flags:

| Flag | Effect |
|---|---|
| `--no-zip` | skip the ZIP step |
| `--no-clean` | keep existing files in `output/` |
| `--page-template path` | use a custom redirect page template |
| `--htaccess-template path` | use a custom .htaccess template |
| `--dry-run` | preview create/update/keep + stale folders, write nothing |
| `--format json` | emit the dry-run plan as JSON (with `--dry-run`) |

`--dry-run` diffs the existing bundle against what a fresh build would
render: per-slug `create` / `update` / `keep` actions, folders a clean
build would remove as stale, and whether `.htaccess`, `404.html` and
`links.json` would be rewritten. Nothing is written, so it's safe to run
any time — including in CI before an upload.

### list — show every short URL

```bash
python -m src.main list configs/links.json
```

Prints `https://link.fedpromptly.com/<slug> -> <destination>` per link.
`--format json` emits one `{"slug", "short_url", "url"}` object per link.

### check — verify the live site

```bash
python -m src.main check configs/links.json
python -m src.main check configs/links.json --timeout 5 --format json
```

Sends a HEAD request to every short URL and **does not follow the
redirect**, comparing the `Location` header against your links file.
Statuses per link: `ok` (301/302/307/308 to the right place),
`wrong-target`, `no-redirect` (HTTP 2xx — `.htaccess` isn't applied) and
`error` (network/4xx/5xx/missing header). Exits 1 if anything is not ok,
which makes it a natural post-deploy CI step. `--timeout` (default 10 s)
bounds each request.

### generate-htaccess — rules only

```bash
python -m src.main generate-htaccess configs/links.json
python -m src.main generate-htaccess configs/links.json --output-file .htaccess
```

Prints (or writes) just the `.htaccess` — handy when you only want to
paste new redirect rules into an existing InfinityFree file.

## The desktop app

Run `python -m src.main` with no arguments on a machine with a display
and the Tkinter window opens: pick a links file, **Validate**, **Build**.
Release builds of the standalone executables are produced by the
`Build Desktop` workflow for Windows, macOS and Linux.

## The Android app

Built from the same generator core with a Kivy front end. The
`Build Android` workflow produces an installable debug APK; see
BUILD.md for the toolchain details.

## The dashboard

```bash
streamlit run examples/streamlit_dashboard/app.py
```

A browser UI over the same commands — see
`examples/streamlit_dashboard/README.md`.

## Watch mode while editing

```bash
scripts/watch.sh     # rebuilds the bundle on every config change
```

Requires `inotify-tools`.

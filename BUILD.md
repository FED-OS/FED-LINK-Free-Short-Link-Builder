# Build

Everything you need to build FED-LINk artifacts, at every level: the static
redirect bundle, the test suite, the desktop app, the Android app, the
Docker image, and the CI pipelines that build all of the above
automatically.

The core truth of this project: **the build is a folder copy, not a
compile.** `src/main.py` reads `configs/links.json`, validates every slug
and destination, renders one redirect page per slug plus `.htaccess` and
`404.html`, and writes them to `output/`. No server starts, no process
daemonizes, nothing runs afterward. Build artifacts:

| Artifact | Command | Output |
|---|---|---|
| Redirect bundle | `python -m src.main build configs/links.json` | `output/` |
| Upload archive | same command with `--zip links.zip` | `links.zip` |
| Desktop app | `pyinstaller pyinstaller.spec` | `dist/FED-LINk` binaries |
| Android app | `buildozer -v android debug` | `bin/*.apk` |
| Docker image | `docker build -t fedlink .` | local image |
| Everything CI does | push to `main` | see workflow table below |

## Quick start

```bash
# 1. Install (only needed for YAML configs or development extras)
python -m pip install -r requirements.txt

# 2. Build the bundle and the upload archive
python -m src.main build configs/links.json --output output --zip links.zip

# 3. Verify before uploading anything
python -m src.main list configs/links.json
python -m src.main generate-htaccess configs/links.json
```

If you run `python -m src.main` with no arguments from a desktop session,
the Tkinter GUI opens instead of the CLI.

## The links file format

`configs/links.json` is the single source of truth for every short link:

```json
{
  "site": "link.fedpromptly.com",
  "home": "https://fedpromptly.com",
  "links": {
    "portfolio": "https://fedpromptly.github.io/portfolio",
    "game": "https://fedpromptly.github.io/game",
    "kofi": "https://ko-fi.com/fedpromptly"
  }
}
```

Slugs are lowercased and validated against `^[a-z0-9][a-z0-9\-_]*$` (max 64
characters); destinations must be absolute `http(s)` URLs. YAML and CSV
variants are supported too (`configs/links.yaml`, a CSV via
`configs/links.csv.example` as the model) — the parser is picked by file
extension. See `docs/configuration.md` for every accepted shape.

## Building the desktop app

`pyinstaller.spec` packages the CLI/GUI entry point `src/main.py` as
**FED-LINk** executables. The GitHub workflow `build-desktop.yml` runs this
on all three desktop platforms and uploads the artifacts.

```bash
python -m pip install pyinstaller
pyinstaller pyinstaller.spec
```

Artifacts land in `dist/FED-LINk-Windows/`, `dist/FED-LINk-macOS/`, and
`dist/FED-LINk-Linux/` (locally you get the one matching your OS). The spec
expects the icon assets at `assets/icon.ico` and `assets/icon.icns`; on
Linux the icon falls back to `assets/icon.png`. If an icon file is missing,
PyInstaller still builds — the spec passes `icon=None`.

## Building the Android app

`buildozer.spec` packages the Kivy front end as an **FED-LINk** APK. The
GitHub workflow `build-android.yml` builds it with Buildozer in a
Linux container and uploads `bin/*.apk`.

```bash
python -m pip install buildozer cython
buildozer -v android debug          # debug APK  -> bin/*.apk
buildozer -v android release        # release APK (needs signing keys)
```

The spec points `source.dir` at `src/` and declares the requirements
`python3,kivy`. Building Android binaries requires Linux (or WSL), a JDK,
and the Android SDK/NDK — the workflow handles all of that, so the
one-liner most people want is: open the **Actions** tab → **build-android**
→ **Run workflow**.

## Docker

The root `Dockerfile` builds the bundle inside a container and drops the
resulting `links.zip` at a known path:

```bash
docker build -t fedlink .
docker run --rm -v "$PWD":/data fedlink        # writes links.zip to ./
docker compose up --build                       # same thing, compose syntax
```

Useful when you want a pinned, reproducible environment for the build step
without installing anything on the host.

## Test build

The test suite is part of the definition of "builds correctly":

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

93 tests cover the parsers (JSON/YAML/CSV), slug/URL validation, HTML
rendering (including a byte-exact fixture comparison), folder generation
and planning (dry-run), ZIP packaging, and the live-check layer with an
injected fetcher so every branch runs offline. CI runs them across Python
3.10, 3.11, and 3.12 via `test.yml` (matrix) and `ci.yml` (umbrella).

## Makefile shortcuts

The `Makefile` at the repo root mirrors the common commands:

```bash
make build      # build output/ + links.zip
make test       # run pytest
make clean      # remove generated output/, links.zip, caches
make lint       # ruff check over src/ and tests/
make package    # desktop build via pyinstaller.spec
```

## CI/CD — what runs when

Nineteen workflows live in `.github/workflows/`. What each does, and when:

| Workflow | Trigger | Purpose |
|---|---|---|
| `main.yml` | push to `main` | umbrella: lint, test, build, deploy gates |
| `build.yml` | push to `main` | build `output/` + `links.zip`, upload artifacts |
| `test.yml` | push/PR | test matrix on Python 3.10 / 3.11 / 3.12 |
| `ci.yml` | push/PR | lint + test + build verification |
| `cd.yml` | push to `main` | deployment pipeline gate |
| `deploy.yml` | push to `main` | mirror bundle to `DEPLOY_MIRROR_URL` (opt-in variable) |
| `deploy-pages.yml` | push to `main` | publish bundle to GitHub Pages |
| `pages.yml` | workflow_run / Pages | Pages deployment pipeline |
| `release.yml` | tags `v*` | cut a GitHub Release with bundle artifacts |
| `publish.yml` | tags `v*` | publish the Python package to PyPI |
| `pr.yml` | pull_request | PR preview builds |
| `build-desktop.yml` | push to `main`, tags | PyInstaller builds (Win/macOS/Linux) |
| `build-android.yml` | push to `main`, tags | Buildozer/Kivy APK build |
| `codeql.yml` | push/PR/schedule | CodeQL security scanning |
| `scorecards.yml` | schedule | OpenSSF Scorecard analysis |
| `dependency-review.yml` | PR | dependency diff security review |
| `stale.yml` | schedule | close stale issues/PRs |
| `labeler.yml` | PR | auto-label PRs by changed paths |
| `greetings.yml` | issue/PR opened | welcome comment |

Local equivalents: `make test` ≈ `test.yml`, `make lint` ≈ the `ci.yml` lint
job, `make build` ≈ `build.yml`, `make package` ≈ `build-desktop.yml`.

## Build invariants

Three properties the build guarantees on every run, by design:

1. **Clean-first generation.** `output/` is wiped before regeneration, so
   deleted slugs leave no orphan folders or stale `.htaccess` lines.
   `.keep` and `.git` entries survive the clean.
2. **Deterministic ZIP.** `links.zip` is built by sorted walk — same input
   always produces a byte-identical archive.
3. **No runtime dependencies in the core.** The generator needs nothing
   outside the standard library; PyYAML is only imported lazily if you
   actually feed it a `.yaml` links file.

## Troubleshooting builds

| Symptom | Fix |
|---|---|
| `unrecognized arguments: --links` | the links file is positional: `build configs/links.json` |
| `slug 'docs' is reserved` | slugs `cgi-bin`, `well-known`, `htdocs`, `404`, `403`, `500` are blocked — rename the slug |
| PyYAML not installed | `pip install pyyaml` or just use the JSON config (core needs nothing) |
| pyinstaller icon error | ensure `assets/icon.ico` / `assets/icon.icns` exist or delete the icon lines from `pyinstaller.spec` |
| buildozer NDK errors | build via the GitHub workflow instead — it provisions the SDK |
| GUI doesn't open | Tkinter needs a desktop session; use the CLI in terminals/SSH |

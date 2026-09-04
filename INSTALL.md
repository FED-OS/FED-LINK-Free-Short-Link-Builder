# Install

FED-LINk is a small Python project — no database, no server, no network
access needed. Install is three commands.

## 1. Get the code

```bash
git clone https://github.com/fedpromptly/infinityfree-shortener-builder.git
cd infinityfree-shortener-builder
```

Or download the ZIP from the repository's **Code** button and unpack it.

## 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

Python 3.10+ is required; 3.11 is what CI tests against.

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

That is the complete runtime: `PyYAML` is the only third-party package,
and only if you use YAML links files.

## 4. Verify

```bash
python -m src.main --version
python -m src.main validate configs/links.json
# -> OK: 10 link(s) valid
```

## Optional extras

```bash
pip install -r requirements-dev.txt                    # pytest, ruff
pip install -r examples/streamlit_dashboard/requirements.txt
scripts/setup.sh                                       # does all of the above
```

## Docker

```bash
docker build -t fedlink -f scripts/docker/Dockerfile .
docker run --rm -v "$PWD/output:/app/output" fedlink build configs/links.json
```

## Ready-to-run apps

No install at all: grab the standalone executables (Windows, macOS,
Linux) or the Android APK from the repository's **Actions** tab — the
`Build Desktop` and `Build Android` workflows attach them as artifacts to
every run.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'src'`** — run commands from the
  repository root, not from inside `src/`.
- **`ImportError` for yaml** — you skipped `pip install -r
  requirements.txt`; JSON links files work without PyYAML, YAML ones do
  not.
- **Tkinter missing** — on Debian/Ubuntu: `sudo apt-get install
  python3-tk`. The CLI works fine without it.

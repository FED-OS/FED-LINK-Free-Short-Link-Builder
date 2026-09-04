# Installation

## Requirements

- Python 3.10+ (3.11 recommended)
- pip
- Optional: PyYAML for YAML links files, Streamlit for the dashboard,
  Tkinter for the desktop app (bundled with python.org installers)

## Standard setup

```bash
git clone https://github.com/fedpromptly/infinityfree-shortener-builder.git
cd infinityfree-shortener-builder
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Or use the helper script, which also runs the test suite:

```bash
scripts/setup.sh
```

## Verify the install

```bash
python -m src.main --version
python -m src.main validate configs/links.json
```

## Optional extras

```bash
pip install -r requirements-dev.txt        # pytest, ruff and friends
pip install -r examples/streamlit_dashboard/requirements.txt   # dashboard
```

## Docker

```bash
docker build -t fedlink -f scripts/docker/Dockerfile .
docker run --rm -v "$PWD/output:/app/output" fedlink build configs/links.json
```

## Upgrading

FED-LINk has no background state — everything is regenerated from your
links file — so upgrading is just `git pull` and rerunning the build.

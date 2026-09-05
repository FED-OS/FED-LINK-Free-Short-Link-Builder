# FED-LINk — InfinityFree Short Link Builder

https://fed-os.github.io/FED-LINK-Free-Short-Link-Builder/

<p>
<a href='https://ko-fi.com/fedpromptly' target='_blank'>
    <img height='36' style='border:0px;height:36px;' src='https://ko-fi.com/img/githubbutton_sm.svg' border='0' alt='Buy Me a Coffee at ko-fi.com' />
</a>
</p>

Turn one plain links file into a complete short-link bundle for your own
domain: redirect folders, Apache `.htaccess` 301 rules, a 404 fallback
page and a single `links.zip` you upload to [InfinityFree](https://infinityfree.com).
You own the domain, the links and the rules — no third-party shortener,
no rate limits, no expiring links.

`https://link.fedpromptly.com/portfolio` → `https://fedpromptly.github.io/portfolio`

## Quick start

```bash
pip install -r requirements.txt
python -m src.main build configs/links.json --output output --zip links.zip
```

Upload `links.zip` to the `htdocs` folder of your subdomain and extract
it — every link is live. Then prove it:

```bash
python -m src.main check configs/links.json
```

## Add a link

Open `configs/links.json` and add one line:

```json
"kofi": "https://ko-fi.com/fedpromptly"
```

Rebuild, re-upload, done: `https://link.fedpromptly.com/kofi` now
redirects permanently (301). `build --dry-run` previews exactly what the
rebuild would create, update, keep or drop before you upload anything.

## What gets built

```
output/
├── .htaccess      one Redirect 301 line per link + 404 fallback
├── 404.html       branded page for unknown short links
├── links.json     machine-readable manifest of the build
└── kofi/
    └── index.html meta-refresh + JS redirect with a visible link
```

## CLI

| Command | Does |
|---|---|
| `python -m src.main build` | generate bundle + `links.zip` (`--dry-run` to preview) |
| `python -m src.main validate` | check a links file |
| `python -m src.main list` | print every short URL |
| `python -m src.main check` | HEAD-check every live redirect against the file |
| `python -m src.main generate-htaccess` | rules only, stdout or file |

Run `python -m src.main --help` for all flags (`--site-domain`,
`--home-url`, `--page-template`, `--htaccess-template`, `--no-zip`,
`--no-clean`, `--allow-private`, `--strict-case`, `--dry-run`,
`--timeout`, `--format json`). With no arguments on a desktop it opens
the Tkinter GUI.

## Apps

| App | Entry point | Built by |
|---|---|---|
| Desktop (Windows/macOS/Linux) | `python -m src.main` | `Build Desktop` workflow (PyInstaller) |
| Android | Kivy front end | `Build Android` workflow (Buildozer) |
| Web dashboard | `streamlit run examples/streamlit_dashboard/app.py` | — |

## GitHub Actions

19 workflows keep the project healthy: build, test, CI/CD, release,
publish, PR previews, Pages deployments (links mirror + docs site),
CodeQL, dependency review, Scorecards, labeler, greetings and stale
management. The `Build` workflow uploads `links.zip` as an artifact on
every push to `main`.

## Deploy on InfinityFree

1. **DNS (IONOS):** CNAME `link` → your InfinityFree server
   (e.g. `if0_41564609.epizy.com`, found under Account Details).
2. **InfinityFree:** create the `link.fedpromptly.com` subdomain.
3. **Upload:** File Manager → the subdomain's `htdocs` → upload
   `links.zip` → Extract.
4. **Verify:** `python -m src.main check configs/links.json`, or
   `curl -sI https://link.fedpromptly.com/portfolio` shows `301` + your
   destination.

Full walkthrough: [docs/deployment.md](docs/deployment.md).

## Configuration

JSON, YAML and CSV are supported; see
[docs/configuration.md](docs/configuration.md) for slug/URL rules and the
`{{placeholder}}` template system (`templates/index.html.j2`,
`configs/.htaccess.template`).

## Development

```bash
scripts/setup.sh     # venv + deps + tests
pytest               # 93 tests
scripts/build.sh     # local bundle build
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the ground rules and
[docs/](docs/) for the full documentation site.

## License

MIT — see [LICENSE](LICENSE).

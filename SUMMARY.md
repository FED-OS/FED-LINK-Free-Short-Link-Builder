# Summary

FED-LINk is a build-time URL shortener for `fedpromptly.com`. It turns a
`links.json` file into a static, upload-anywhere bundle: one folder per
short link, one `Redirect 301` line per slug, one branded 404 page, one
deterministic ZIP. You host that bundle on InfinityFree (live site:
`link.fedpromptly.com`) and CI mirrors it to GitHub Pages for free.

## The problem it solves

Short-link services (Bitly, Dub.co) charge for the features that matter:
custom domains, unlimited links, and the ability to export your data. A
static redirect bundle gives you all three for the cost of a free hosting
account. `link.fedpromptly.com/portfolio` costs nothing, redirects with a
clean `301`, and points at a URL you own (`fedpromptly.github.io/portfolio`)
— so the GitHub side can be reorganized without breaking any short link.

## How it works, in one paragraph

You maintain a single source of truth — `configs/links.json` — with entries
like `"portfolio": "https://fedpromptly.github.io/portfolio"`. Running
`python -m src.main build configs/links.json --zip links.zip` validates
every slug (lowercase, `^[a-z0-9][a-z0-9\-_]*$`, max 64 chars, no reserved
words like `cgi-bin` or `404`), renders a redirect page per slug
(meta-refresh + `window.location.replace` JS fallback + a visible link for
users with scripting disabled), writes an Apache `.htaccess` with
`Redirect 301 /slug destination` lines and a branded `404.html`, and packs
everything into a deterministic ZIP. Upload that ZIP into the
`link.fedpromptly.com` subdomain's `htdocs` on InfinityFree and every slug
is live as a proper 301 redirect.

## What's in the repository

| Area | Contents |
|---|---|
| `src/` | The generator: parsers (JSON/YAML/CSV), validators, HTML builder, folder creator, ZIP packager, logger, file cleaner, CLI + Tkinter GUI (`python -m src.main`) |
| `configs/` | `links.json` (10 live links), `links.yaml`, `links.csv.example`, `.htaccess.template`, `redirects.map` |
| `templates/` | `index.html.j2`, `404.html`, `fallback.html` |
| `tests/` | 93 pytest tests, including a byte-exact output fixture and fully offline (fetcher-injected) live-check coverage |
| `.github/workflows/` | 19 workflows: build, test matrix, CI/CD, Pages deploy, releases, PyPI, desktop (PyInstaller), Android (Buildozer), CodeQL, Scorecards, and housekeeping |
| `scripts/` | `setup.sh`, `build.sh`, `deploy.sh`, `clean.sh`, `watch.sh`, Docker files |
| `examples/` | basic, advanced (custom template), streamlit dashboard |
| `docs/` | full documentation set + `images/` |
| `public/` | `css/style.css`, `js/script.js` |
| root | README, INSTALL, BUILD, DEPLOYMENT, FAQ, ROADMAP, ADR, SECURITY, SUPPORT, GOVERNANCE, and the rest of the governance/doc suite, `ko-fi.html`, `styles.css` |

## Repository at a glance

- **Language:** Python 3.10+ (standard library only in the core)
- **Front ends:** CLI (`python -m src.main`), Tkinter GUI, Kivy/Android,
  Streamlit example
- **Tests:** 93 passing
- **License:** MIT
- **Live:** `https://link.fedpromptly.com` — 10 slugs, all 301-redirecting

## The 10 live links

| Slug | Destination |
|---|---|
| `portfolio` | `https://fedpromptly.github.io/portfolio` |
| `game` | `https://fedpromptly.github.io/game` |
| `docs` | `https://fedpromptly.github.io/docs` |
| `blog` | `https://fedpromptly.github.io/blog` |
| `resume` | `https://fedpromptly.github.io/resume` |
| `shop` | `https://fedpromptly.github.io/shop` |
| `app` | `https://fedpromptly.github.io/app` |
| `tools` | `https://fedpromptly.github.io/tools` |
| `contact` | `https://fedpromptly.github.io/contact` |
| `kofi` | `https://ko-fi.com/fedpromptly` |

## Key commands

```bash
python -m src.main build configs/links.json --output output --zip links.zip
python -m src.main build configs/links.json --dry-run          # preview, write nothing
python -m src.main validate configs/links.json
python -m src.main list configs/links.json
python -m src.main check configs/links.json                    # live HEAD check
python -m src.main generate-htaccess configs/links.json
python -m pytest
```

## Design decisions

The ten Architecture Decision Records in [`ADR.md`](ADR.md) cover the
whys: static generation instead of a server (ADR-0001), plain
`Redirect 301` lines instead of RewriteMap (ADR-0002), per-slug
`index.html` fallbacks so the bundle works even where `.htaccess`
redirects don't (ADR-0003), a dependency-free core (ADR-0004), strict
slug rules (ADR-0005), `{{placeholder}}` templates instead of Jinja2
(ADR-0006), `src/` layout (ADR-0007), multiple front ends on one engine
(ADR-0008), deterministic clean-first generation (ADR-0009), and GitHub
Actions as the automation backbone (ADR-0010).

## Status

v1.1.0 (see [`CHANGELOG.md`](CHANGELOG.md)). Everything in the approved
file tree exists, the generator and tests are verified, and the bundle has
been built and inspected. The v1.1 quality-of-life wave is shipped: a
`check` subcommand that HEAD-verifies every live short link against the
links file, `--strict-case` to reject mixed-case slugs instead of
normalizing them, `build --dry-run` to preview create/update/keep actions
before writing, and `--format json` on `validate`, `list`, `check` and
`build --dry-run` for machine-readable output. Remaining roadmap items
(incremental FTP deploy, QR codes) live in [`ROADMAP.md`](ROADMAP.md).

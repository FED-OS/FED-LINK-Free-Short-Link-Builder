# FED-LINk — InfinityFree Short Link Builder

FED-LINk turns a plain links file into a complete short-link bundle you
deploy on your own domain. It generates one redirect folder per link, an
Apache `.htaccess` with 301 rules, a 404 fallback page and a single
`links.zip` ready for the InfinityFree file manager. You own the domain,
the links and the rules — no third-party redirect service in the loop.

Typical link: `https://link.fedpromptly.com/portfolio` →
`https://fedpromptly.github.io/portfolio`.

## Documentation sections

- [Installation](installation.md) — local setup in three commands
- [Usage](usage.md) — CLI commands and the desktop/Android apps
- [Configuration](configuration.md) — links files, formats and templates
- [Deployment](deployment.md) — IONOS DNS + InfinityFree walkthrough
- [API](api.md) — the Python API behind the CLI
- [Contributing](contributing.md) — how to submit changes
- [Changelog](CHANGELOG.md) — release history

## Quick start

```bash
pip install -r requirements.txt
python -m src.main build configs/links.json --output output --zip links.zip
```

Then upload `links.zip` to the `htdocs` folder of your
`link.yourdomain.com` subdomain and extract it — every link is live.

## Why this exists

Free URL shorteners rebrand, rate-limit and disappear. A `Redirect 301`
line in a `.htaccess` file on your own domain is permanent, instant to
update, and costs nothing beyond the hosting you already have.

# Usage

The hands-on guide to using FED-LINk day to day: the CLI commands, the
GUI, editing links, and what you get when you build. (This is the root
quick-reference; [`docs/usage.md`](docs/usage.md) is the expanded manual.)

## Ten-second start

```bash
python -m src.main build configs/links.json --output output --zip links.zip
```

That validates every link, wipes and regenerates `output/`, and packs
`links.zip` ready to upload. Upload it (InfinityFree file manager →
`htdocs` of `link.fedpromptly.com` → Extract), and
`https://link.fedpromptly.com/portfolio` is live as a 301 redirect.

## The five commands

### `build` — generate the deployable bundle

```bash
python -m src.main build [LINKS_FILE] [options]
```

The links file is **positional** — `build configs/links.json`, not
`--links configs/links.json` (the most common first mistake; it's in the
FAQ).

| Option | Default | Effect |
|---|---|---|
| `--site-domain` | `link.fedpromptly.com` | domain stamped into generated pages |
| `--home-url` | `https://fedpromptly.com` | the "back to home" link on pages |
| `--output` | `output` | where the bundle is written |
| `--zip` | `links.zip` | name of the archive packed from the bundle |
| `--no-zip` | — | skip packing the ZIP |
| `--no-clean` | — | keep existing files in the output dir |
| `--page-template` | `templates/index.html.j2` | override the redirect page template |
| `--htaccess-template` | `configs/.htaccess.template` | override the `.htaccess` template |
| `--allow-private` | — | allow `http://localhost`/LAN destinations (testing only) |
| `--strict-case` | — | reject mixed-case slugs instead of normalizing them |
| `--dry-run` | — | preview create/update/keep actions, write nothing |
| `--format {text,json}` | `text` | text summary or machine-readable JSON |

`--dry-run` compares the existing bundle byte-for-byte with what a real
build would render, then reports per-slug `create` / `update` / `keep`
actions, stale folders that a clean build would remove, and which support
files (`.htaccess`, `404.html`, `links.json`) would be rewritten — without
touching the output directory:

```
Dry run for 'configs/links.json' -> 'output' (nothing was written)
  keep 10: portfolio, game, docs, blog, resume, shop, app, tools, contact, kofi
  support files to rewrite: links.json
Result: a real build would apply the changes above
```

### `validate` — check a links file without building

```bash
python -m src.main validate configs/links.json
```

Prints `OK: 10 links validated` and exits 0, or fails with the exact
slug and reason. Use it before committing a links change. With
`--format json` it prints `{"ok": true, "count": 10, "links": {...}}`
(or `{"ok": false, "error": "..."}`) for scripts and CI gates.

### `list` — audit what's live-able

```bash
python -m src.main list configs/links.json
```

Prints every `slug -> destination` pair, normalized, in build order. The
fastest way to answer "where does /tools go?" `--format json` emits one
`{"slug", "short_url", "url"}` object per link.

### `check` — verify the live site, link by link

```bash
python -m src.main check configs/links.json
```

After you upload a bundle, `check` sends a real HEAD request to every
short URL (`https://link.fedpromptly.com/<slug>`) **without following the
redirect**, and compares the returned `Location` header with the
destination in your links file. It never follows the hop, so a broken
*destination* still shows as `ok` — this command proves the *shortener*
side works; `curl` remains the tool for the far end.

```
portfolio            ok            -> https://fedpromptly.github.io/portfolio
game                 wrong-target  -> got https://fedpromptly.github.io/game (expected .../game-project)
kofi                 no-redirect   -> HTTP 200: .htaccess is missing or not applied
10 checked, 9 ok, 1 problem(s)     # exit code 1 when anything is not ok
```

Four statuses: `ok` (301/302/307/308 with the right `Location`),
`wrong-target` (redirects somewhere else), `no-redirect` (HTTP 2xx — the
`.htaccess` rules aren't being applied), and `error` (network failure,
4xx/5xx, or a missing `Location` header). `--timeout` (default 10
seconds) bounds each HEAD request; `--format json` emits the full
`CheckResult` records for dashboards. This is the same call GitHub Pages
users should run after every deploy.

### `generate-htaccess` — preview the Apache rules

```bash
python -m src.main generate-htaccess configs/links.json
```

Prints the exact `Redirect 301 /slug destination` lines the build would
write — no files created. Pipe it anywhere you want to eyeball routing.

## Editing your links

Add a link = one line in `configs/links.json`:

```json
"presskit": "https://fedpromptly.github.io/presskit"
```

Then rebuild and re-upload. That's the entire loop. Deleting a link is the
same in reverse — and because the build is clean-first, the removed slug's
folder *and* its `.htaccess` line disappear on the next build; no stale
redirects can survive. `build --dry-run` shows exactly which folders a
rebuild would create, update, keep, and drop before you commit to it.

Slug rules: lowercase, digits, `-`, `_`; starts alphanumerically; ≤ 64
chars. Reserved (blocked) slugs: `cgi-bin`, `well-known`, `htdocs`, `404`,
`403`, `500`. Uppercase in the file is normalized to lowercase by default
— `/Portfolio` in, `portfolio` out. Prefer to catch those slips instead of
silently fixing them? Add `--strict-case` (works on every command) and a
mixed-case slug is rejected with a message telling you to write it in
lowercase or drop the flag.

## Running the GUI

```bash
python -m src.main
```

With no subcommand and a desktop session present, the Tkinter GUI opens:
pick a links file, set the output folder and ZIP name, watch the build
log live, and export the bundle. Same engine, same validation, buttons
instead of flags. (Over SSH/headless it stays a CLI — Tkinter needs a
display.)

## What you get after a build

```
output/
├── .htaccess      # Redirect 301 /portfolio https://fedpromptly.github.io/portfolio
├── 404.html       # branded not-found page
├── links.json     # manifest: every slug and destination
├── portfolio/     # one folder per slug
│   └── index.html # meta-refresh 0 + JS location.replace + visible link
└── ...
```

- **On InfinityFree**, `.htaccess` does the work: real `301` status codes,
  and anything unknown hits `404.html`.
- **On GitHub Pages**, the per-slug `index.html` pages do the work
  (meta-refresh + JS), since Pages ignores `.htaccess` — that's why every
slug gets a folder (ADR-0003).

## Common loops

**Add a link and ship it**

```bash
$EDITOR configs/links.json
python -m src.main validate configs/links.json
python -m src.main build configs/links.json --zip links.zip
# upload links.zip -> htdocs -> Extract -> done
python -m src.main check configs/links.json
```

**Audit before a meeting**

```bash
python -m src.main list configs/links.json | column -t -s'>'
```

**Prove a redirect works**

```bash
python -m src.main check configs/links.json        # every link, one pass
curl -sI https://link.fedpromptly.com/portfolio | head -3   # just one
```

## Where to read more

- Full command/API detail — [`docs/usage.md`](docs/usage.md),
  [`docs/api.md`](docs/api.md)
- Configuration shapes (JSON/YAML/CSV) — [`docs/configuration.md`](docs/configuration.md)
- Getting it hosted — [`DEPLOYMENT.md`](DEPLOYMENT.md)
- Why it's built this way — [`ADR.md`](ADR.md)

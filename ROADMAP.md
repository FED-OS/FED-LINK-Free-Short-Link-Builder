# Roadmap

Where FED-LINk is headed. Items are ordered by intent, not by promise — this
is a spare-time project and the roadmap is a signal of direction, not a
contract. Status legend: **done** (shipped), **next** (planned for the
1.x line), **later** (post-1.x ideas), **maybe** (needs a strong argument).

## v1.0 — Foundation (done)

The core engine shipped with the initial release: multi-format links files
(JSON, YAML, CSV), strict slug and URL validation with private-address
blocking, deterministic generation of per-slug redirect pages, `.htaccess`
with `Redirect 301` rules, a branded 404 fallback, a links manifest, and ZIP
packaging for upload. Command-line and Tkinter GUI front ends landed
together with a 63-test suite, Docker images, PyInstaller desktop build
workflows, a Buildozer Android workflow, Streamlit dashboard example, and
full GitHub Pages deployment paths. The documentation set, contributing
guides, and community scaffolding round it out.

## v1.1 — Quality of life (done)

Shipped in 1.1.0. Four workflow features landed together:

**Strict-case configuration.** The `--strict-case` flag makes mixed-case
slugs a hard error instead of a silent lower-case, for people who want the
links file treated as the literal source of truth. Works on `build`,
`validate`, `list`, `check` and `generate-htaccess`.

**Live link health checking.** The `check` subcommand HEAD-requests every
*deployed* short link (never following the redirect), compares the
`Location` header against the links file and reports `ok`,
`wrong-target`, `no-redirect` or `error` per link, exiting non-zero when
anything is unhealthy — a CI gate against pointing at dead pages.
Standard library only, `--timeout` supported.

**Dry-run diff.** `build --dry-run` shows exactly which slug pages would
be created, updated or kept, which folders are stale (removed on a real
build) and which support files would be rewritten — without touching
disk. `--format json` gives the same plan to scripts.

**JSON output for CI.** `--format json` on `validate`, `list`, `check`
and `build --dry-run`, so other tools and workflows can consume results
without parsing prose.

## v1.2 — Deployment ergonomics (next)

**Direct FTP/SFTP deploy.** An optional `deploy` subcommand reading host
credentials from `.env` (never from the repo) and pushing the bundle to
`htdocs` for you — closing the last manual gap in the pipeline.

**Incremental uploads.** Only upload folders whose content hash changed,
keeping InfinityFree's file-count limits friendly for large link sets.

**Deploy receipts.** After upload, write a small receipt (timestamp, link
count, host) into `logs/` so you have an audit trail of what went live when.

**Verification pass.** Post-deploy `curl` smoke test of every slug, with a
clear failure report — one command instead of a checklist.

## v1.3 — Templates and theming (later)

**Theme packs.** A `themes/` directory with a few curated looks (minimal,
branded splash, corporate) so `--theme clean` is all the customization most
people need.

**Per-link overrides.** Optional per-slug template or title fields in the
links file, letting one link show a splash while the rest redirect
instantly.

**QR codes.** Optional QR generation per slug into each folder — print-ready
short links for posters and business cards, produced offline with Pillow.

## Post-1.x — Explorations (later / maybe)

**Analytics without servers.** A privacy-first approach to click counting
that does not require a backend — likely static access-log parsing of the
host's logs, documented end-to-end.

**Expiring links.** Date-bounded slugs whose pages switch to the 404 after
an expiry date, all computed at build time so the deployed files stay static.

**Batch import.** Pull links from an existing bookmark export or another
shortener's API dump (Bitly, Dub) and convert them into a links file in one
step.

**RewriteMap native output.** Emit `configs/redirects.map`-style maps
directly from the build for Apache hosts where `RewriteMap` scales better
than hundreds of `Redirect` lines.

**Plug-in parsers.** A documented parser interface so a drop-in `.py` file
can teach `load_links` a new configuration format without touching core.

## Non-goals

Worth saying out loud: FED-LINk will not grow a server runtime, a database,
user accounts, or a hosted service. The entire value is that a dumb static
host does all the serving. Anything that requires server-side logic belongs
in a different project — and the roadmap will keep refusing it.

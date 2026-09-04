# Architecture Decision Records

Lightweight ADRs for FED-LINk. Each records a decision that shaped the
project, the options considered, and why the winner won. Records are
numbered and immutable once accepted — superseding a decision adds a new
record, never edits the old one.

Format borrowed from Michael Nygard's ADR template, kept deliberately short.

---

## ADR-0001 — Static file generation instead of a server-side shortener

**Status:** Accepted

**Context:** The project's goal is short links on `link.fedpromptly.com`
using free InfinityFree hosting and a domain from IONOS. InfinityFree
supports PHP, but any dynamic runtime brings maintenance, attack surface,
and free-tier limits.

**Decision:** FED-LINk is a build-time generator. It produces plain HTML
redirect pages and Apache `.htaccess` rules; nothing executes at request
time.

**Consequences:** Zero server load beyond static file serving, no database,
no rate limits, and links keep working even if the generator disappears.
The trade-off is no server-side click analytics and a rebuild+upload cycle
for every change — accepted because a config edit plus `push` is already a
deploy pipeline.

---

## ADR-0002 — Apache `Redirect 301` as the primary redirect mechanism

**Status:** Accepted

**Context:** Apache offers several redirect mechanisms: `Redirect`,
`RedirectMatch`, and `mod_rewrite` rules. Options ranged from a single
catch-all `RewriteMap` to per-slug directives.

**Decision:** Emit one explicit `Redirect 301 /slug https://destination`
line per link in `.htaccess`, plus `ErrorDocument 404 /404.html` and
`Options -Indexes`.

**Consequences:** Per-slug lines are readable, greppable, and trivially
hand-editable on the host in an emergency. At very large link counts
thousands of directives could outgrow a RewriteMap (`configs/redirects.map`
exists for that path, see ROADMAP), but hundreds — the realistic case for a
personal shortener — are negligible to Apache.

---

## ADR-0003 — Per-slug `index.html` fallback with meta-refresh + JavaScript

**Status:** Accepted

**Context:** Not every host (notably GitHub Pages) honors `.htaccess`. A
fallback was needed that works with pure static file serving.

**Decision:** Every slug folder contains an `index.html` with a
`<meta http-equiv="refresh" content="0; url=...">` plus a
`window.location.replace(...)` script and a visible link for the no-JS case.

**Consequences:** The same bundle deploys to Apache hosts and static hosts
alike. The JS URL is inserted via `json.dumps` so no quoting or injection
ambiguity exists. Cost: on hosts without rewrites the redirect is
client-side, so there is a brief page paint before navigation.

---

## ADR-0004 — Dependency-free core; PyYAML optional

**Status:** Accepted

**Context:** Parsers for JSON and CSV come free with the standard library;
YAML does not. Depending on PyYAML for every user to support one format
seemed heavy.

**Decision:** Only YAML parsing imports PyYAML, and the import is deferred
to call time with a clear error message when the user lacks it. Everything
else uses the standard library only.

**Consequences:** `python -m src.main build configs/links.json` works on a
bare Python install. YAML users need one extra package — documented in
`INSTALL.md` and `requirements.txt`.

---

## ADR-0005 — Strict slug rules and a short reserved-word list

**Status:** Accepted

**Context:** Slugs become directory names and Apache directives, so they
must be safe and predictable. An early draft reserved `docs`, `blog`, and
other common words — rejected as over-aggressive.

**Decision:** Slugs are lowercased and must match `^[a-z0-9][a-z0-9\-_]*$`,
max 64 characters. Only genuine server paths are reserved: `cgi-bin`,
`well-known`, `htdocs`, `404`, `403`, `500`.

**Consequences:** Configs are forgiving of case but never produce paths
that escape `output/` or clobber generator-owned files, while still allowing
natural words like `docs` or `blog` as slugs.

---

## ADR-0006 — Custom `{{placeholder}}` templates instead of a template engine

**Status:** Accepted

**Context:** Jinja2 would bring power (conditionals, loops) but also a hard
dependency and a second language to document.

**Decision:** A tiny regex renderer supporting `{{slug}}`, `{{url}}`,
`{{url_js}}`, `{{site_domain}}`, `{{home_url}}`, `{{generated_at}}`, and
`{{count}}`. Unknown placeholders are left literal rather than erroring.

**Consequences:** Templates remain plain HTML anyone can edit, the core
stays dependency-free, and the placeholder list fits in one documentation
table (`docs/configuration.md`). Complex needs are met by generating with
the default template and post-processing, which no one has needed.

---

## ADR-0007 — Python package layout with `src/` and `python -m src.main`

**Status:** Accepted

**Context:** The tool must run straight from a git clone with no install
step, yet stay a proper package for PyInstaller, Buildozer, PyPI publishing,
and pytest.

**Decision:** Layout the code as the `src` package with subpackages
`generator`, `parsers`, `validators`, `utils`; run via
`python -m src.main`. Packaging metadata (`pyproject.toml`, `setup.py`)
maps the same tree.

**Consequences:** Zero-install usage for the common case; one source of
truth for every packaging target; tests import the exact code users run.
Alternative considered: a flat `generate.py` script — rejected as
untestable at this scale and unable to feed multiple front ends (CLI, GUI,
Kivy, Streamlit).

---

## ADR-0008 — Multiple front ends over one UI framework

**Status:** Accepted

**Context:** A CLI is precise but hostile to non-technical users; a web UI
needs a server; a GUI toolkit ties packaging to one platform.

**Decision:** Ship three front ends on one engine: the argparse CLI, a
Tkinter GUI (stdlib, auto-opens when run with no args and a display exists),
and a Kivy front end packaged by Buildozer for Android. A Streamlit
dashboard lives in `examples/` for those who want a web UI.

**Consequences:** Every user class gets a native-feeling entry point with
no new core dependencies. Cost: three thin presentation layers to keep in
sync with the CLI surface — mitigated by having all of them call the same
`parsers`/`validators`/`generator` functions.

---

## ADR-0009 — Deterministic, clean-first output generation

**Status:** Accepted

**Context:** Deleted slugs must actually disappear from a deployed site,
and rebuilds must be reproducible for byte-diff verification.

**Decision:** Each build cleans `output/` (preserving `.keep` and `.git`)
before regenerating, walks directories in sorted order, and writes the ZIP
deterministically.

**Consequences:** No zombie folders from removed slugs; `diff -r` between
two builds differs only where the links file differs. `.keep` survives so
the empty directory still tracks in git.

---

## ADR-0010 — GitHub Actions as the automation backbone

**Status:** Accepted

**Context:** Every change to a links file should be one commit from live,
with tests, packaging, and deployment handled without a workstation.

**Decision:** Nineteen workflows cover the lifecycle: build, test matrix,
CI, CD to gh-pages, Pages deploys, releases, PyPI publishing, PR previews,
plus housekeeping (labeler, greetings, stale, CodeQL, dependency review,
scorecards) and desktop/Android artifact builds.

**Consequences:** The repo is fully self-operating on GitHub. Secrets stay
out of the repo by design (the deploy mirror is opt-in via a repository
variable), and pull-request runs are read-only until review.

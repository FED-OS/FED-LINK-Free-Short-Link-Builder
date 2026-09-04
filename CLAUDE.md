# CLAUDE.md

Instructions for Claude Code (and any AI coding agent) working in this
repository. Read this before touching anything. Companion file:
[`AGENTS.md`](AGENTS.md) (same rules, engine-neutral wording).

## What this project is

A **build-time URL shortener**. `configs/links.json` → static files →
upload. There is no server, no database, no runtime — any change that
introduces one violates ADR-0001 and will be rejected. The output is
served by Apache on InfinityFree (`.htaccess` `Redirect 301` rules) and
mirrored to GitHub Pages (per-slug `index.html` does the redirecting
there).

## Non-negotiable rules

1. **ENGLISH ONLY.** All code, comments, docs, commit messages, issues,
   and responses. This is an explicit project rule from the owner; other
   languages in output are treated as a bug.
2. **Never edit `output/`, `links.zip`, or anything on the host by hand.**
   Generated files are disposable. Edit `configs/links.json` (or the
   templates), then rebuild: `python -m src.main build configs/links.json
   --output output --zip links.zip`.
3. **Never add a runtime dependency to the core.** `src/` runs on the
   standard library alone; PyYAML stays a lazy import inside
   `src/parsers/yaml_parser.py` (ADR-0004).
4. **Keep builds deterministic.** `links.zip` must be byte-identical for
   identical input (sorted walk in `src/generator/zip_packager.py`).
   Don't add timestamps, random names, or nondeterministic ordering.
5. **Clean-first generation stays.** `output/` is wiped each build;
   `.keep` and `.git` survive. Removed slugs must leave no orphans.
6. **Slug rules are law:** `^[a-z0-9][a-z0-9\-_]*$`, ≤ 64 chars, reserved
   set `cgi-bin, well-known, htdocs, 404, 403, 500`, uppercase
   normalized to lowercase (not rejected).
7. **Match the existing CLI shape.** The links file is a **positional**
   arg. New flags go on `build`; new subcommands need a README + usage.md
   + FAQ update in the same PR.
8. **Tree discipline:** add files that exist in the approved tree and
   nothing else. Don't invent scaffolding (no `Makefile` plugins, no
   generated docs dirs) without a governance-level nod.

## Repository map (where to make changes)

| Change type | Where |
|---|---|
| New link / fix a destination | `configs/links.json` (+ `links.yaml` mirror if kept in sync) |
| Redirect page look | `templates/index.html.j2`, `templates/404.html` |
| Apache rules format | `configs/.htaccess.template` |
| Validation rules | `src/validators/` |
| New input format | `src/parsers/` + `load_links` dispatch in `src/parsers/__init__.py` |
| Build behavior | `src/generator/` |
| CLI / GUI | `src/main.py` |
| Tests | `tests/` (pytest; keep the byte-exact fixture test green) |
| CI | `.github/workflows/` (19 files; YAML-validate any edit) |

## Verification loop (run before declaring done)

```bash
cd infinityfree-shortener-builder
python -m pytest                                   # must be all green
python -m src.main validate configs/links.json
python -m src.main build configs/links.json --output output --zip links.zip
python -m src.main list configs/links.json
python -m src.main generate-htaccess configs/links.json
bash -n scripts/*.sh                               # if any script changed
python -c "import yaml,sys; [yaml.safe_load(open(f)) for f in sys.argv[1:]]" .github/workflows/*.yml
```

Expected: 93 tests passing, 10 `Redirect 301` rules, no validation
errors. If the `.htaccess` template or page template changed, eyeball
`output/.htaccess` and `output/portfolio/index.html` directly.

## Templates use `{{placeholder}}`, not Jinja2

`HtmlBuilder.render` substitutes `{{name}}` tokens via regex; unknown
tokens are left literal (deliberate — see ADR-0006). `{{url_js}}` is the
JSON-encoded safe-JS-literal form of the destination. If you need a new
placeholder, add it in `html_builder.py` and document it in
`docs/configuration.md` + `FAQ.md`.

## Known gotchas

- **CLI arg order:** `--links` does not exist; it's positional. If a
  command fails with `unrecognized arguments: --links`, the invocation is
  wrong, not the code.
- **`{{redirects}}` in the fallback `.htaccess`:** the built-in fallback
  uses double braces; single-brace `{redirects}` silently renders as
  literal text (this was a real bug once — there's a regression test).
- **GUI needs a display:** Tkinter only opens with a desktop session; in
  SSH/CI it's CLI-only. Don't "fix" this by adding imports at module top.
- **`docs` slug is valid** — the reserved list was trimmed deliberately
  (ADR-0005); don't re-block common words.
- **Windows/macOS path separators** in ZIP: the packager normalizes to
  forward slashes; keep it that way.

## Writing style for docs

Plain, short sentences. Tables for reference material. Every doc links
related docs by relative path. Keep README/BUILD/DEPLOYMENT/FAQ/usage.md
in sync when behavior changes — stale docs are treated as a bug.

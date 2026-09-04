# AGENTS.md

Engine-neutral instructions for any AI agent (Codex, Cursor, Aider, or
future tooling) contributing to FED-LINk. Claude-specific framing lives in
[`CLAUDE.md`](CLAUDE.md); the rules here apply to every agent regardless
of harness.

## Prime directive

FED-LINk is a static, build-time URL shortener: links file in, static
redirect bundle out, upload, done. There is no server, no database, no
runtime state. Any proposal that adds a daemon, a database, or a hosted
service is out of scope by ADR-0001 and the ROADMAP's recorded non-goals.
Reject it and point at those documents instead of implementing it.

## Hard rules (same as CLAUDE.md)

1. **English only** in all output: code, comments, commit messages, docs,
   issues, and chat responses. Explicit owner rule.
2. **Generated artifacts are disposable.** Never hand-edit `output/`,
   `links.zip`, or anything deployed on the host. Change
   `configs/links.json` or the templates and rebuild.
3. **Core stays dependency-free.** `src/` imports nothing outside the
   standard library at module import time. PyYAML is a lazy import inside
   the YAML parser only.
4. **Determinism is a contract.** Identical input must produce
   byte-identical `links.zip`. Sorted walk, no timestamps, no randomness.
5. **Clean-first generation.** `output/` is wiped on every build;
   `.keep` and `.git` survive. Removed slugs must leave no orphans.
6. **Slug rules:** `^[a-z0-9][a-z0-9\-_]*$`, ≤ 64 chars, reserved
   `cgi-bin, well-known, htdocs, 403, 404, 500`, uppercase normalized
   (never rejected).
7. **CLI shape is frozen:** positional links file; flags documented in
   `usage.md`. New subcommands must update README, `usage.md`, and FAQ in
   the same change.
8. **No scaffolding inventions.** Only files in the approved tree. If a
   change genuinely needs a new file, open an issue first — the tree is
   governance (see [`GOVERNANCE.md`](GOVERNANCE.md)).

## Standard workflow for any change

1. Read the relevant ADR in [`ADR.md`](ADR.md) before architectural
   changes; add a new ADR rather than contradicting an old one.
2. Make the smallest change that satisfies the issue.
3. Add or update tests in `tests/` — the 63-test suite (including the
   byte-exact fixture) must stay green.
4. Run the full verification loop:

   ```bash
   python -m pytest
   python -m src.main validate configs/links.json
   python -m src.main build configs/links.json --output output --zip links.zip
   python -m src.main list configs/links.json
   python -m src.main generate-htaccess configs/links.json
   ```

5. Update docs touched by the behavior change: README, BUILD, DEPLOYMENT,
   usage.md, FAQ as applicable.
6. Write the PR against the template in `PULL_REQUEST_TEMPLATE.md`;
   CI (the `test.yml` 3.10/3.11/3.12 matrix and `ci.yml`) must be green.

## Change routing table

| You're changing... | Touch | Don't touch |
|---|---|---|
| A destination URL | `configs/links.json` | `output/`, the host |
| Page appearance | `templates/index.html.j2`, `templates/404.html` | generated HTML |
| Apache rule format | `configs/.htaccess.template` | generated `.htaccess` |
| Validation | `src/validators/` + tests | parsers |
| New input format | `src/parsers/` + dispatcher + tests | generator |
| Build behavior | `src/generator/` + tests | templates |
| CLI/GUI | `src/main.py` | engine internals |
| CI | `.github/workflows/*.yml` (YAML-validate) | scripts/ equivalents |

## Agent-specific notes

- **Never regenerate `output/` and commit it in the same PR as an engine
  change** — rebuild artifacts belong in a separate verification commit,
  or stay uncommitted (they're disposable).
- **Don't reformat the whole repo** to please a linter; ruff is configured
  in `pyproject.toml` and pre-commit — scope formatting to your diff.
- **Don't "fix" the fallback `.htaccess` braces.** The `{{redirects}}`
  double-brace form is correct; single braces are the bug (regression
  test exists).
- **Don't add `--links`** back as a flag; positional is deliberate and
  documented in three places.
- **If a test fails, fix the engine, not the test** — unless the test
  contradicts an ADR, in which case flag it in an issue first.
- **Long tasks:** this repo is small; don't split work across sessions in
  ways that lose the verification loop. Finish with green tests and a
  fresh build in the same session.

## Communication norms

When summarizing work: state what changed, what was verified (with actual
command output), and what docs were updated. No claims without a run
behind them — "63/63 passed" only if pytest said so this session. All
English, always.

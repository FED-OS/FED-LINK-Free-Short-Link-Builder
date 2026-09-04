# Contributing to FED-LINk

Thanks for helping build FED-LINk. The rules are short.

## Ground rules

1. Read CONTRIBUTING.md (root) — this page is the docs-site copy and
   points there for the authoritative version.
2. Open an issue before large changes so work does not get duplicated.
3. One topic per pull request; keep the diff reviewable.
4. English only in code, commits, issues and discussions.

## Development loop

```bash
scripts/setup.sh                 # venv + deps + test run
source .venv/bin/activate
pytest                           # must pass before every commit
scripts/build.sh                 # local bundle build
```

Pre-commit runs ruff and friends: `pip install pre-commit && pre-commit
install`. CI runs the same checks — lint, tests, and a build-check that
fails if `links.zip` cannot be produced.

## What is welcome

- new parser formats (TOML, INI) behind the existing `load_links` API
- template improvements that work without extra runtime dependencies
- docs fixes, especially deployment walkthroughs for other hosts
- tests — the suite covers validators, parsers and generator; more edge
  cases are always welcome

## What is not

- network calls in the generator — it stays offline and deterministic
- redirects that depend on third-party shortener APIs
- link changes for fedpromptly.com itself without owner sign-off

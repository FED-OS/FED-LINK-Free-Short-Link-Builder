# Contributing to FED-LINk

Thanks for your interest in improving FED-LINk. This is the authoritative
contribution guide; a docs-site copy lives at
[docs/contributing.md](docs/contributing.md).

## Ground rules

1. **Open an issue first** for anything bigger than a typo fix, so work
   is not duplicated and the approach is agreed before code is written.
2. **One topic per pull request.** A link change, a feature and a docs
   rewrite belong in three PRs, not one.
3. **English only** in code, comments, commits, issues and discussions —
   the widest audience should be able to follow every thread.
4. **No secrets.** Account IDs, panel passwords and private URLs must be
   redacted before posting.

## Development loop

```bash
scripts/setup.sh          # creates .venv, installs deps, runs tests once
source .venv/bin/activate
pytest                    # must pass before every commit
scripts/build.sh          # builds output/ + links.zip locally
```

The PR workflow builds a preview bundle from your branch — attach it to
the PR description if the change affects what gets generated.

## Code style

- Formatting and linting are enforced with **ruff** (see
  `.pre-commit-config.yaml`); install the hooks with
  `pip install pre-commit && pre-commit install`.
- Keep the generator **offline and deterministic**: no network calls, no
  clock-dependent output beyond the documented `{{generated_at}}` stamp.
- New parsers plug into `src/parsers/__init__.py:load_links` and ship
  with tests in `tests/test_parsers.py`.
- New validators ship with tests in `tests/test_validators.py`.

## Commit messages

Use the Conventional Commits layout — `type: summary`:

```
feat: add TOML links parser
fix: accept links key as mapping or list
docs: expand the InfinityFree upload walkthrough
chore: bump actions/checkout to v4
```

## Pull request checklist

Every PR template includes this list; keep it honest:

- [ ] `pytest` passes locally
- [ ] `python -m src.main build configs/links.json` produces a valid bundle
- [ ] link changes are listed in the PR description (ADD/CHANGE/REMOVE)
- [ ] documentation updated where behaviour changed
- [ ] no secrets or private URLs included

## Reporting bugs

Use the bug report template (`.github/ISSUE_TEMPLATE/bug_report.md`) and
include the links file entry that failed, the exact command, and the full
traceback — the validator messages already point at the entry number,
which speeds things up enormously.

## Licensing

By contributing you agree your work is released under the project's MIT
license (see LICENSE and the DCO note in NOTICE.md).

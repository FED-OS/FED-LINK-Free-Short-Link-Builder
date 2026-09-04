# Maintainers

Who maintains FED-LINk day to day, what they're responsible for, and how
to reach them. If you're taking over maintenance or responding to a
security report, start here.

## Current maintainers

| Name | Role | Responsibility | Reachable via |
|---|---|---|---|
| fedpromptly | Owner, lead maintainer | everything: architecture (ADRs), releases, security reports, merges | GitHub Issues/Discussions; `link.fedpromptly.com/contact` |

Single-maintainer project, deliberately: the bus factor is mitigated by
the design itself — the project is a deterministic generator with 63
tests, 19 CI workflows, and a docs suite; a new maintainer can rebuild
the entire live site from this repository alone (see
[`DEPLOYMENT.md`](DEPLOYMENT.md)).

## Responsibilities

- **Merging:** PRs land only with green CI (`test.yml` matrix and `ci.yml`
  minimum). Architectural PRs need the owner's review per
  [`GOVERNANCE.md`](GOVERNANCE.md).
- **Releases:** tag `vX.Y.Z` → `release.yml`/`publish.yml` fire. The
  changelog entry is written before tagging.
- **Security:** reports to the address in [`SECURITY.md`](SECURITY.md)
  are answered within 72 hours and fixed within 14 days; only the owner
  handles them.
- **CI health:** all 19 workflows are watched for red runs; the umbrella
  `main.yml` is the tripwire.
- **The live site:** `link.fedpromptly.com` is rebuilt and re-uploaded
  from `main` — the host is never hand-edited (governance principle 4).

## Becoming a maintainer

There's no formal ladder. The practical path: recurring quality PRs,
consistent issue triage help, and demonstrated care for the project's
invariants (deterministic builds, no server runtime, links-file-is-law).
The owner appoints maintainers; expect it to be rare in a project this
size.

## Stepping down / handover

If the owner steps away: hand over in this order — (1) repository
ownership transfer, (2) update this file and [`AUTHORS.md`](AUTHORS.md),
(3) publish an ADR recording the transfer, (4) cut a release so the new
maintainer's first deploy is verified end-to-end. The GitHub Pages mirror
keeps serving regardless, since it deploys from the repository state.

## Maintainer quick reference

```bash
python -m pytest                              # 93 tests must pass
python -m src.main build configs/links.json --zip links.zip
python -m src.main list configs/links.json    # audit live slugs
git tag vX.Y.Z && git push origin vX.Y.Z      # triggers release/publish
```

Daily-triage order: security inbox → red CI runs → issues → PRs →
Discussions.

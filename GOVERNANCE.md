# Governance

How decisions get made in the FED-LINk repository: who decides what, how
changes land, and how the project stays boring and predictable — which is
a feature for a redirect infrastructure you depend on.

## Principles

1. **The links file is law.** `configs/links.json` is the single source of
   truth. Nothing overrides it — not a config in CI, not a hand-edited
   file on the host. If a redirect is wrong, the fix lands in the links
   file and nowhere else.
2. **Static beats clever.** ADRs 0001–0010 (see [`ADR.md`](ADR.md)) are the
   constitution; changes to the architecture go through a new ADR, not a
   surprise in a PR.
3. **Deterministic builds.** Same input, byte-identical `links.zip`. Any
   PR that breaks determinism breaks the project.
4. **The host is not state.** Everything on InfinityFree/Pages is
   disposable and regenerable from the repo. No hand-tuning on the host.
5. **Everything in English.** Docs, commits, issues — one language, no
   drift. (An explicit project rule.)

## Roles

| Role | Holder | Decides |
|---|---|---|
| Owner / BDFL | fedpromptly | everything, final call on ADRs and releases |
| Maintainers | listed in [`MAINTAINERS.md`](MAINTAINERS.md) | day-to-day merges, issue triage, release prep |
| Contributors | anyone with an accepted PR | the contents of their PR, nothing else |
| Users | anyone | feature requests via Issues/Discussions |

This is a small project with one owner, so the governance is deliberately
thin: the owner has final say on everything, maintainers handle the daily
flow, and the ADR file is the record of why.

## Decision levels

| Level | Examples | Process |
|---|---|---|
| **Trivial** | typo fixes, docs, CI lint tweaks | PR + CI green → merge |
| **Standard** | new parser format, new CLI flag, template change | issue → PR → tests → review → merge |
| **Architectural** | anything contradicting an ADR; new front end; packaging changes | issue → discussion → new/updated ADR → PR |
| **Constitutional** | license, ownership, non-goals (ROADMAP "Non-goals") | owner decision, written up as an ADR |

The deliberately strictest rule: **FED-LINk never becomes a server, a
database, or a hosted service.** That is a recorded non-goal in
[`ROADMAP.md`](ROADMAP.md) and ADR-0001; proposals that require a server
runtime are closed with a pointer to those documents.

## How changes land

1. **Issue first** for anything non-trivial — so the reason for a change
   is captured before the code is written.
2. **PR from a feature branch**, small and focused, using the PR template.
3. **CI must be green** — all 19 workflows that apply to the PR, at
   minimum `test.yml` (3.10/3.11/3.12 matrix) and `ci.yml`.
4. **Review** — one approving review for standard changes; architectural
   changes need the owner.
5. **Merge to `main`** — `main` is always deployable; `build.yml` and
   `deploy-pages.yml` fire on every push to `main`.
6. **Releases** — tags `vX.Y.Z` trigger `release.yml` and `publish.yml`;
   the changelog entry is written in the PR, not after.

Versioning is semantic: MAJOR for breaking changes to the links-file
format or CLI, MINOR for new features, PATCH for fixes.

## ADR process

Architecture Decision Records live in [`ADR.md`](ADR.md) (ADR-0001 through
ADR-0010 exist; ADR-0011+ get appended). To change or add one:

1. Open an issue titled `ADR-XXXX: <topic>` describing the decision to
   record or supersede.
2. Discussion happens on the issue — the format is Nygard-style (Context,
   Decision, Consequences, Alternatives rejected).
3. The accepted decision is appended to [`ADR.md`](ADR.md) by PR; a
   superseding ADR marks the old one as superseded, it is never deleted.

## Community conduct

[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) applies to every interaction in
the repository — issues, PRs, Discussions, and email. Enforcement
escalation: warning → temporary ban → permanent ban, at the owner's
discretion. Security issues follow [`SECURITY.md`](SECURITY.md) instead of
public issues, always.

## Support and funding

Support is free and community-run (see [`SUPPORT.md`](SUPPORT.md)). There
are no paid tiers and no support contracts ([`PRICING.md`](PRICING.md));
voluntary support goes through ko-fi (`link.fedpromptly.com/kofi`) and
funds nothing but the maintainer's coffee. Governance is not for sale —
funding cannot buy a merge, a feature, or a roadmap slot.

# Feature request

Root-level copy of the feature request template — the live version GitHub
renders is `.github/ISSUE_TEMPLATE/feature_request.md`; this copy exists
so the template is readable outside the GitHub UI. Fill it in and submit
it as a GitHub Issue (label it `enhancement`).

---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always
frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features
you've considered (other URL shorteners, manual .htaccess editing, etc.).

**Where should this live?**
- [ ] CLI (`src/main.py`)
- [ ] Desktop app
- [ ] Android app
- [ ] Streamlit dashboard
- [ ] Documentation

**Additional context**
Add any other context, screenshots or examples about the feature request
here.

---

## What makes a good request here

- **Check the ROADMAP first.** [`ROADMAP.md`](ROADMAP.md) lists what's
  already planned (v1.1 `check` subcommand, v1.2 incremental FTP deploy,
  v1.3 QR codes and themes) — "+1" on a planned item is more useful than
  a duplicate request.
- **Non-goals are real.** This project will never become a server, a
  database, or a hosted service (ADR-0001, ROADMAP "Non-goals"). Requests
  for click analytics backends, user accounts, or a web API will be
  politely declined with a pointer to those documents.
- **Static-only ideas fit best:** new input formats, template features,
  deployment targets, CLI ergonomics, per-link options, generated
  artifacts (QR codes, link directories), build automation.
- **Say which front end** matters to you (CLI/GUI/Android/dashboard) —
  the engine is shared but priorities aren't.

The fastest path from request to shipped: describe the *workflow* you
want, not just the flag. "I rebuild twice a week and I want to upload only
what changed" led to ROADMAP v1.2; the same style of request is easy to
say yes to.

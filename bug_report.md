# Bug report

Root-level copy of the bug report template — the live version GitHub
actually renders is `.github/ISSUE_TEMPLATE/bug_report.md`; this copy
exists so the template is readable outside the GitHub UI (and editable in
one obvious place). Fill it in and submit it as a GitHub Issue at the
repository's Issues page.

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run `python -m src.main ...`
2. Use this links file ...
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Your links file**
If the bug involves parsing or validation, paste the offending entry here
(redact anything private):

```json
{ "slug": "https://example.com/destination" }
```

**Environment**
- OS: [e.g. Windows 11, Ubuntu 24.04]
- Python version: [e.g. 3.11.9]
- FED-LINk version: [e.g. 1.1.0 — see `python -m src.main --version`]
- Deployment target: [InfinityFree, GitHub Pages, other]

**Logs**
Paste any log output or the full traceback here.

**Additional context**
Add any other context about the problem here.

---

## Tips that get bugs fixed faster

- **Reproduce with the smallest links file possible** — one entry that
  triggers the bug beats your full production file.
- **Include the exact command line.** The most common non-bug report is
  `--links` being passed when the links file is positional: the correct
  form is `python -m src.main build configs/links.json`. Check
  [`FAQ.md`](FAQ.md) first — the top issues are pre-answered there.
- **Say whether it happens in the CLI, the GUI, or both.** They share an
  engine, so the answer localizes the problem immediately.
- **Paste the traceback, don't screenshot it.** Text is searchable and
  survives color schemes.
- **For deployment-side issues** (files on the host not redirecting),
  include the `curl -sI` output from
  [`DEPLOYMENT.md`](DEPLOYMENT.md) Part B4 — the 301 status and `Location`
  header tell us whether the problem is the build or the host.

Security issues do **not** go here — follow [`SECURITY.md`](SECURITY.md)
for private reporting instead.

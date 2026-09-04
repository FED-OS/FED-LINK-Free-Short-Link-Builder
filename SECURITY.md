# Security Policy

## Supported Versions

FED-LINk is a static file generator: it runs on your machine, produces HTML,
and never opens a port or runs a server. The version policy below applies to
the generator itself and to the files it emits.

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Do not open a public issue for security problems.**

Report vulnerabilities privately to **security@fedpromptly.com**. Please
include a description of the issue, the steps to reproduce it, and the
affected file paths or commands. If you found the issue while auditing a
deployed short-link site, include the URL pattern but do not include live
credentials.

The maintainer will acknowledge every report within 72 hours and aim to ship a
fix within 14 days for anything that affects generated output or published
artifacts. Once a fix is released, credit will be given in
`docs/CHANGELOG.md` (unless you prefer to remain anonymous).

## Scope

Because the tool is a pure generator, the realistic attack surface is small.
In scope:

- **Malicious URLs in a links file.** A crafted `links.json`/`links.yaml`/CSV
  could try to inject JavaScript into generated pages. FED-LINk renders URLs
  into `<meta http-equiv="refresh">` attributes and into a JavaScript
  `window.location.replace` fallback; destinations are escaped and validated
  to `http`/`https` only. If you find a way around that, report it.
- **Path traversal via slugs.** Slugs must match `^[a-z0-9][a-z0-9\-_]*$`
  (max 64 chars) before any folder is created, and the reserved words
  `cgi-bin`, `well-known`, `htdocs`, `404`, `403`, `500` are rejected, so a
  slug cannot escape the output directory or clobber fallback pages.
- **Generated ZIP packaging.** Archive entries must never be able to write
  outside their extraction directory.
- **CI/CD workflows.** Workflows in `.github/workflows/` run on untrusted
  pull requests only in read-only contexts; any injection there is in scope.

Out of scope:

- The hosting provider's own infrastructure (InfinityFree, GitHub Pages,
  IONOS DNS). Those are outside this repository.
- Social engineering, phishing via destination URLs you configured yourself,
  or rate limiting of the free hosting tier.
- Reports from automated scanners that do not include a proof of concept.

## Hardening Notes for Deployments

A few habits keep the deployed short-link site safe. Only ever commit link
configurations that point to destinations you control, because the whole
system is only as trustworthy as the URLs in `configs/links.json`. Keep the
generated `404.html` in place so unknown paths land on your branded page
instead of a server default. If you enable directory listings on your host,
disable them — the `.htaccess` template already ships `Options -Indexes` for
this reason. Finally, never put secrets in `.env`; the only documented
variables are non-secret build flags, and the example file is safe to commit.

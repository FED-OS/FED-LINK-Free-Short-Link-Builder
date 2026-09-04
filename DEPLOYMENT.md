# Deployment

This is the root-level deployment runbook for FED-LINk. It walks the whole
lifecycle — build, verify, package, upload, DNS, post-deploy checks, and
rollback — for both hosting targets the project supports: **InfinityFree**
(the primary target, where `link.fedpromptly.com` lives) and **GitHub Pages**
(the automatic mirror built by CI). For the condensed step-by-step guide, see
[`docs/deployment.md`](docs/deployment.md); this document is the expanded,
checklist-style version.

The short version of the architecture, and why deployment is this simple:
FED-LINk is a **build-time** shortener. There is no server, no database, and
no runtime to monitor. The deployable artifact is a folder of static files —
one `index.html` per slug, one `.htaccess`, one `404.html` — that Apache
serves directly. Deploying is therefore just "get these files onto the host."

## What gets deployed

A successful build produces an `output/` folder shaped like this:

```
output/
├── .htaccess          # Redirect 301 /slug destination  (one line per slug)
├── 404.html           # branded not-found page
├── links.json         # build manifest (slug -> destination, for auditing)
└── portfolio/
    └── index.html     # meta-refresh + JS fallback redirect page
...one folder per slug
```

`links.zip` is a deterministic, sorted archive of exactly that tree. It is
the artifact you upload.

## Deployment targets

| Target | Trigger | Artifact | Result |
|---|---|---|---|
| InfinityFree `htdocs` | manual upload of `links.zip` | ZIP from `--zip` | `link.fedpromptly.com/<slug>` 301-redirects |
| GitHub Pages | push to `main` (`pages.yml`, `deploy-pages.yml`) | `output/` committed/CI-built | `link.fedpromptly.com` CNAME or `fedpromptly.github.io` mirror |

Both targets receive the same generated content. The InfinityFree copy is
the live redirector; the Pages copy is a free mirror/fallback that needs no
maintenance.

## Part A — build and verify locally

1. **Build**:

   ```bash
   python -m src.main build configs/links.json --output output --zip links.zip
   ```

2. **Inspect** the generated rules without deploying anything:

   ```bash
   python -m src.main list configs/links.json
   python -m src.main generate-htaccess configs/links.json
   ```

3. **Spot-check** the output folder: open `output/portfolio/index.html` in a
   browser — it should bounce you to `https://fedpromptly.github.io/portfolio`
   immediately. Open `output/404.html` and confirm it renders the branded
   not-found page.

4. **Run the test suite** if anything changed in the pipeline itself:

   ```bash
   python -m pytest
   ```

Never upload a build you haven't opened in a browser at least once.

## Part B — deploy to InfinityFree

### B1. DNS at IONOS (one-time setup)

Log in to IONOS → **Domains & SSL** → `fedpromptly.com` → **DNS** and add a
**CNAME** record:

| Field | Value |
|---|---|
| Host / Prefix | `link` |
| Points to | `if0_41564609.epizy.com` (your server, from InfinityFree **Account Details**) |
| TTL | default |

DNS propagation can take up to an hour. Verify with
`dig link.fedpromptly.com +short` — it should answer with the epizy.com
server name.

### B2. Subdomain at InfinityFree (one-time setup)

InfinityFree client area → **Subdomains** → create `link.fedpromptly.com`.
Wait for the free SSL certificate to be issued for it. Each subdomain gets
its **own** `htdocs` directory — this is the single most common deployment
mistake in this project.

### B3. Upload the bundle (every deploy)

1. Client area → **Control Panel** → **File Manager**.
2. Open the `htdocs` folder **for the `link.fedpromptly.com` subdomain**
   (not the one for your root domain, not a sibling subdomain).
3. Upload `links.zip`.
4. Use the file manager's **Extract** action to unpack it *in place*, so the
   ZIP contents land directly in `htdocs/` — `htdocs/.htaccess`,
   `htdocs/404.html`, `htdocs/portfolio/`, and so on.
5. If the file manager shows a warning about hidden files, make sure
   `.htaccess` actually extracted; some file managers hide dotfiles in the
   listing while serving them fine.

### B4. Post-deploy verification

```bash
# Known slug: expect HTTP/1.1 301 + Location: destination
curl -sI https://link.fedpromptly.com/portfolio | head -3

# Unknown slug: expect the branded 404 page
curl -s https://link.fedpromptly.com/does-not-exist | head -5

# HTTPS: expect a valid certificate (free InfinityFree SSL)
curl -sI https://link.fedpromptly.com/portfolio | grep -i strict\|http
```

Check **one slug from the middle of your list** too, not just the first —
it proves the whole `.htaccess` extracted, not just the first line.

## Part C — deploy to GitHub Pages (automatic)

The Pages mirror requires no manual steps once configured:

1. Repository **Settings → Pages → Source: Deploy from a branch**, branch
   `main`, folder `/ (root)` — the `pages.yml` and `deploy-pages.yml`
   workflows take it from there and publish the generated redirect bundle.
2. The repo root contains `CNAME` (content: `link.fedpromptly.com`) and
   `.nojekyll` so Pages serves the plain `.htaccess`-free static tree with
   your custom domain applied.
3. If you want `link.fedpromptly.com` served by **Pages instead of
   InfinityFree**, change the IONOS CNAME target from the epizy.com server
   to `fedpromptly.github.io` and add `link.fedpromptly.com` in the repo's
   Pages custom-domain settings. That is a one-record switch — the content
   is identical on both hosts. (The 301 redirect rules only work on
   InfinityFree via `.htaccess`; on Pages the per-slug `index.html` pages do
   the redirecting via meta-refresh + JS, which is exactly why every slug
   gets its own folder.)
4. Watch the deploy: **Actions** tab → the `pages` / `deploy-pages` workflow
   runs → green check → the site is live.

## Rollback

Because every deploy is a full regeneration, rollback strategies are simple:

- **Bad slug, good build:** edit `configs/links.json`, rebuild, re-upload.
  The `.htaccess` is regenerated wholesale, so removed slugs stop
  redirecting immediately — no stale rules can survive a rebuild.
- **Bad build entirely:** checkout the previous commit
  (`git log --oneline`, `git checkout <sha> -- configs/ links.json` if
  needed), rebuild, re-upload. Keep the prior `links.zip` in `dist/` or
  `logs/` until you've verified the new one if you want a byte-exact
  fallback to re-upload.
- **DNS-level incident:** the CNAME at IONOS can be pointed at the GitHub
  Pages mirror (Part C, step 3) within minutes — the Pages copy is always
  in sync from CI.

## Troubleshooting quick table

| Symptom | Fix |
|---|---|
| subdomain doesn't resolve | CNAME typo, or propagation not finished (`dig` again) |
| InfinityFree default page | files landed in the wrong `htdocs` (each subdomain has its own) |
| links 404 at the host | `.htaccess` missing from the ZIP root — re-extract in place |
| no 301 redirect | host overrides `Redirect`; ask InfinityFree support to enable `mod_alias` |
| Pages 404 | check `pages.yml` run, and that `CNAME`/`.nojekyll` are on the deployed branch |
| redirects loop | destination URL points back at `link.fedpromptly.com` — check `configs/links.json` |

## Deploying from CI instead of by hand

`deploy.yml` mirrors the built bundle to a secondary host when the repository
variable `DEPLOY_MIRROR_URL` is defined (Settings → Secrets and variables →
Actions → Variables). It is **opt-in**: with no variable set, the workflow
succeeds as a no-op. This is the supported path for keeping a second host in
sync without manual uploads; see `.github/workflows/deploy.yml` for the
exact steps it performs.

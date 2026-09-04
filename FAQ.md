# FAQ — FED-LINk

Frequently asked questions, with straight answers. If your question is not
here, open a Discussion thread (see `SUPPORT.md`).

## General

**What is FED-LINk?**
A static file generator for your own URL shortener. You describe short links
in `configs/links.json` (or YAML or CSV), and FED-LINk builds everything a
shared host needs: one folder per slug with a redirect `index.html`, an
`.htaccess` full of `Redirect 301` rules, a branded `404.html`, a
`links.json` manifest, and a `links.zip` ready to upload.

**Why "static"? Why not a real shortener service like Dub.co or Bitly?**
Because you already own a domain and free hosting. Static redirects cost
nothing, never rate-limit you, never expire your links, and keep working as
long as you keep the files. Third-party shorteners can shut down, change
their limits, or hold your analytics hostage — your own `Redirect 301` rules
can't.

**What does a short link look like when it's live?**
`link.fedpromptly.com/portfolio` → `https://fedpromptly.github.io/portfolio`
— a clean 301 to wherever you pointed it.

**Does it need a database or server-side code?**
No. Apache on InfinityFree handles the redirects from `.htaccess`; the
per-slug `index.html` pages are a JavaScript/meta-refresh fallback for hosts
without rewrites. Nothing dynamic runs anywhere.

## Setup and building

**What do I need installed?**
Python 3.10+ and PyYAML (only if you use YAML links files). The core
generator is dependency-free; `requirements.txt` exists for convenience.

**How do I run it without installing anything?**
From the repo root: `python3 -m src.main build configs/links.json`. That
writes `output/` and `links.zip`.

**What does the GUI look like?**
Run `python -m src.main` with no arguments on a machine with a display and
the Tkinter window opens — pick a links file, validate it, click Build. It is
the same engine as the CLI.

**Why do I get "unrecognized arguments" when I pass `--links`?**
The links file is a positional argument, not a flag. Write
`python -m src.main build configs/links.json`, not
`build --links configs/links.json`.

**Can I use a different links file format?**
Yes — JSON, YAML, and CSV are all supported, picked by file extension. See
`docs/configuration.md` for the accepted shapes (mapping, wrapper object with
`site`/`home`/`links`, urlzap-style list, or CSV with a `slug,url` header).

## Redirect behavior

**Is the redirect a 301 or 302?**
301 (permanent) via `.htaccess`, which is what you want for short links: it
preserves link equity and gets cached aggressively. The HTML fallback pages
use meta-refresh plus `window.location.replace`, which browsers treat as a
client-side redirect for hosts that ignore rewrites.

**I added a slug but it 404s. Why?**
Three usual causes. First, you edited the links file but never re-ran the
build — no folder, no rule. Second, you uploaded the ZIP to the wrong folder;
the contents of `output/` go inside `htdocs` for the right subdomain. Third,
you typed the slug with different case — slugs are normalized to lowercase,
so `Portfolio` in your config becomes `portfolio` on disk.

**Why is the slug lowercased?**
Short URLs are effectively case-sensitive on most hosts, and mixed-case
slugs double the ways a link can be mistyped. FED-LINk normalizes everything
to lowercase so `link.fedpromptly.com/PORTFOLIO` in a config never creates a
folder that only works when typed one exact way.

**Why was my slug rejected?**
Slugs must start with a letter or digit, may contain `a-z`, `0-9`, `-` and
`_`, and be at most 64 characters. A handful of reserved words (`cgi-bin`,
`well-known`, `htdocs`, `404`, `403`, `500`) are rejected because they would
collide with server paths or the error pages the generator itself writes.

**Can one slug point to another slug?**
You can point `/kofi` at `https://ko-fi.com/fedpromptly` — anywhere with
`http`/`https`. Pointing a slug at another slug on the same domain works but
adds a hop; point it at the final destination instead.

## Hosting and DNS

**Do I have to use InfinityFree?**
No, any Apache host that honors `.htaccess` works — nearly all shared hosts
do. InfinityFree is the reference target because it's free and reliable for
pure redirects. GitHub Pages works too (via the Pages deploy workflows),
using the HTML fallback pages instead of `.htaccess`.

**How do I point `link.fedpromptly.com` at InfinityFree?**
Add a CNAME at your DNS provider: host `link`, target your InfinityFree
server hostname (find it in InfinityFree under Accounts, e.g.
`if0_XXXXXXXX.epizy.com`), then add `link.fedpromptly.com` as a subdomain in
the InfinityFree control panel. Full walkthrough with verification commands
is in `docs/deployment.md`.

**Does the short-link site work on GitHub Pages?**
Yes. `deploy-pages.yml` and `pages.yml` publish the bundle and the docs
site; `.nojekyll` keeps Pages from ignoring the redirect pages. Note Pages
serves HTML redirects client-side — there is no `.htaccess` on Pages.

**Why does my browser sometimes show the destination without a redirect flash?**
That is the `.htaccess` doing a server-side 301 before any HTML loads — the
good path. When rewrites are unavailable the fallback page takes over and
you may see a brief splash.

## Customizing

**How do I change what the redirect page looks like?**
Edit `templates/index.html.j2` (or pass `--page-template your.html` to the
CLI). Placeholders like `{{slug}}`, `{{url}}`, `{{url_js}}`, `{{site_domain}}`
and `{{generated_at}}` get filled in per link. `examples/advanced/` has a
branded splash-page example.

**How do I brand the 404 page?**
Edit `templates/404.html` and rebuild — it is copied into every build. The
default is a dark page with the FED-LINk accent color and a link home.

**Can I add a delay before redirecting?**
Yes — a custom template with a delayed meta-refresh (see
`templates/fallback.html` for a five-second example). Be aware delays hurt
the user experience and CTR; the default is instant.

**Can I track clicks?**
Static redirects don't have a server-side counter. Use a privacy-respecting
counting pixel in a custom template, or check your destination's analytics —
referrer data plus short-link volume tells you most of what you need.

## Maintenance

**What happens when I delete a slug from my links file?**
The next build with cleaning enabled removes its folder from `output/`, and
the manifest and `.htaccess` drop the rule. Upload the fresh bundle (or just
delete the folder and `.htaccess` line on the host) and the old link 404s to
your branded page.

**Is there a way to preview links before deploying?**
`python -m src.main list configs/links.json` prints every slug and
destination; `python -m src.main generate-htaccess configs/links.json`
prints the Apache rules without building. For a rendered preview, open
`output/<slug>/index.html` locally in a browser.

**How do I move to a new domain?**
Keep the same links file, change `--site-domain` and `--home-url`, rebuild,
and repoint DNS. Your slugs stay identical — only the domain in the pages
and manifest changes.

**Something broke after an update.**
Diff `output/` before and after — the generator is deterministic, so any
change comes from your config or the templates. Pin the release you trust
(see `docs/CHANGELOG.md`) and upgrade deliberately.

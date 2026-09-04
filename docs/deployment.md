# Deployment

FED-LINk builds the bundle; deploying it is a two-part manual step:
point DNS at your host, then upload the bundle. The full setup below is
the one that works for `fedpromptly.com` on IONOS + InfinityFree.

## Part 1 — DNS at IONOS

1. Log in to IONOS → **Domains & SSL** → `fedpromptly.com` → **DNS**.
2. Add a **CNAME** record:

| Field | Value |
|---|---|
| Host / Prefix | `link` |
| Points to | your InfinityFree server, e.g. `if0_41564609.epizy.com` |
| TTL | default |

3. Find the exact server name in the InfinityFree client area under
   **Account Details** (it looks like `if0_XXXXXXX.epizy.com`).

DNS changes need up to an hour to propagate.

## Part 2 — hosting at InfinityFree

1. InfinityFree client area → **Subdomains** → create
   `link.fedpromptly.com` (the account must already host the domain or a
   sibling subdomain — free accounts attach domains this way).
2. Wait for the SSL certificate to be issued for the subdomain.

## Part 3 — upload the bundle

1. Run the build: `python -m src.main build configs/links.json --zip links.zip`
2. Client area → **Control Panel** → **File Manager** for the account.
3. Open the `htdocs` folder **for the link.fedpromptly.com subdomain**.
4. Upload `links.zip` and use the file manager's **Extract** to unpack it
   in place.
5. Confirm the tree: `htdocs/.htaccess`, `htdocs/404.html`,
   `htdocs/<slug>/index.html`.

## Part 4 — verify

```bash
curl -sI https://link.fedpromptly.com/portfolio | head -3
```

Expect `HTTP/1.1 301` and a `Location:` header with your destination.
An unknown link (`/does-not-exist`) should show the branded 404 page.

## Updating links later

Edit `configs/links.json`, rebuild, re-upload. The `.htaccess` is
regenerated wholesale, so removed links stop redirecting immediately —
no stale rules survive.

## Troubleshooting

| Symptom | Fix |
|---|---|
| subdomain doesn't resolve | CNAME typo, or propagation not finished |
| InfinityFree default page | files landed in the wrong `htdocs` (each subdomain has its own) |
| links 404 at the host | `.htaccess` missing from the ZIP root — re-extract in place |
| no 301 redirect | host overrides `Redirect`; ask InfinityFree support to enable mod_alias |

# Configuration

## The links file

Three formats are supported; the extension picks the parser. Order is
preserved, so `.htaccess` rules stay stable across rebuilds.

### JSON (recommended) — `configs/links.json`

```json
{
  "links": {
    "portfolio": "https://fedpromptly.github.io/portfolio",
    "kofi": "https://ko-fi.com/fedpromptly"
  }
}
```

A plain `{"slug": "url"}` object without the `links` wrapper, and a
urlzap-style array of `{path, url}` objects, are both accepted.

### YAML — `configs/links.yaml`

```yaml
links:
  - path: /portfolio
    url: https://fedpromptly.github.io/portfolio
```

A plain `slug: url` mapping is accepted too.

### CSV — `links.csv.example`

```csv
slug,url
portfolio,https://fedpromptly.github.io/portfolio
```

Headers `path`/`destination` are accepted as aliases; quoted URLs with
commas are handled.

## Slug rules

- lowercase letters, digits, `-` and `_`; must start with a letter or digit
- max 64 characters
- input is trimmed and lower-cased automatically
- reserved (server/fallback paths): `cgi-bin`, `well-known`, `htdocs`,
  `404`, `403`, `500`
- slugs become folder names, so they must be unique

## URL rules

- absolute `http://` or `https://` URLs only
- a host is required; underscores in hosts are rejected
- localhost/private addresses are rejected unless `--allow-private` is
  passed (local testing only)

## Templates

### Redirect page — `templates/index.html.j2`

`{{placeholders}}` are replaced: `{{slug}}`, `{{url}}`, `{{url_js}}` (a
safe JS string literal), `{{site_domain}}`, `{{home_url}}` and
`{{generated_at}}`. Unknown placeholders are left untouched. Point a
custom template at it with `--page-template`.

### .htaccess — `configs/.htaccess.template`

Must contain the `{{redirects}}` placeholder, which is replaced with one
`Redirect 301 /slug https://destination` line per link. Keep the
`ErrorDocument 404 /404.html` line so unknown links fall back to your
main site.

## Site-wide settings

| Setting | Default | Where |
|---|---|---|
| `--site-domain` | `link.fedpromptly.com` | CLI flag |
| `--home-url` | `https://fedpromptly.com` | CLI flag |
| output directory | `output` | `--output` |
| zip name | `links.zip` | `--zip` |

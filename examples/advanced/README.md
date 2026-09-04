# Advanced example

This example shows the two knobs FED-LINk gives you beyond the defaults: a
YAML configuration in urlzap layout, and a **custom redirect page
template** that renders a branded splash page instead of the instant jump.

## Files

| File | Purpose |
|---|---|
| `links.yaml` | urlzap-style list layout with extra `title` keys |
| `custom_template.html` | custom page template using `{{placeholders}}` |

## Supported template placeholders

| Placeholder | Expands to |
|---|---|
| `{{slug}}` | the short word (`launch`) |
| `{{url}}` | the destination URL (escaped for HTML) |
| `{{url_js}}` | the destination URL as a safe JavaScript string literal |
| `{{site_domain}}` | `link.fedpromptly.com` |
| `{{home_url}}` | the fallback destination |
| `{{generated_at}}` | build timestamp, e.g. `2026-09-04 18:59:42Z` |

Unknown placeholders are left untouched, so partial customisation is safe.

## Build it

```bash
python -m src.main build examples/advanced/links.yaml \
  --page-template examples/advanced/custom_template.html \
  --output output --zip links.zip
```

The generated pages wait 3 seconds before redirecting, show the
destination link and a build stamp, and load `/styles.css` from the site
root (copy `styles.css` from the repository root into `htdocs`).

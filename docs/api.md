# Python API

The CLI is a thin wrapper over four small, importable modules. The build
pipeline itself runs entirely offline; only the optional live-check
helpers (`check_links`, `evaluate_redirect`) touch the network, and only
when you call them.

## The build pipeline in six lines

```python
from src.parsers import load_links
from src.generator.folder_creator import FolderCreator
from src.generator.zip_packager import ZipPackager
from src.validators import validate_links

pairs = load_links("configs/links.json")     # [(slug, url), ...]
mapping = validate_links(pairs)              # raises LinkValidationError

creator = FolderCreator(output_dir="output")
creator.generate(mapping.items())            # writes the tree

ZipPackager("output", "links.zip").package() # -> ("links.zip", n)
```

## Previewing a build without writing anything

```python
plan = creator.plan(mapping.items())
# {"actions": {"portfolio": "keep", "presskit": "create", ...},
#  "stale": ["old-slug"], "write_404": False, "write_htaccess": True,
#  "write_manifest": True, "clean": True, "changes": True}
```

`plan()` is what `build --dry-run` uses: it compares the existing bundle
byte-for-byte with what `generate()` would render and reports, per slug,
`create` (folder missing), `update` (bytes differ — a URL or template
change) or `keep` (identical). `stale` lists folders present on disk but
absent from the links file; `write_404` / `write_htaccess` /
`write_manifest` flag support files that would be rewritten; `clean` is
true when stale folders would be removed; `changes` summarises whether a
real build would do anything at all. It never touches the output
directory, and it validates its input first, so it's safe to call with
raw pairs.

## Module reference

### src.parsers

| Function | Returns |
|---|---|
| `load_links(path)` | `list[(slug, url)]`, parser chosen by extension |
| `load_links_json / _yaml / _csv(path)` | same, for a fixed format |

Raises `MalformedLinksFileError` (JSON/YAML) or
`UnsupportedLinksFormatError` (unknown extension).

### src.validators

| Function | Returns / raises |
|---|---|
| `validate_slug(value, strict_case=False)` | normalised slug or `LinkValidationError` |
| `validate_url(value)` | the URL unchanged or `LinkValidationError` |
| `validate_link(slug, url, allow_private=False, strict_case=False)` | `(slug, url)` pair |
| `validate_links(pairs, allow_private=False, strict_case=False)` | ordered `{slug: url}` dict |

`LinkValidationError` subclasses `ValueError`, so a broad `except
ValueError` catches parser and validator problems together. By default a
mixed-case slug is lower-cased (`"Portfolio"` → `"portfolio"`); pass
`strict_case=True` to reject it instead, with a message telling the
caller to write it lowercase or drop the strictness.

### src.validators — live check (v1.1)

```python
from src.validators import check_links

results = check_links(pairs, site_domain="link.fedpromptly.com", timeout=10.0)
for r in results:
    print(r.slug, r.status, r.detail)
```

| Name | Role |
|---|---|
| `CheckResult` | dataclass: `slug`, `url`, `check_url`, `status`, `http_status`, `location`, `detail`; property `.ok`, method `.as_dict()` |
| `build_check_url(site_domain, slug)` | `https://<domain>/<slug>` (respects a domain that already has a scheme) |
| `evaluate_redirect(slug, check_url, expected_url, timeout=10.0, fetcher=None)` | one `CheckResult`; sends a HEAD request and never follows the redirect |
| `check_links(links, site_domain="link.fedpromptly.com", timeout=10.0, fetcher=None, allow_private=False, strict_case=False)` | validate then live-check every link → `list[CheckResult]` in file order |

`status` is one of `ok` (HTTP 301/302/307/308 with a matching `Location`
header), `wrong-target` (redirects somewhere else), `no-redirect` (HTTP
2xx — `.htaccess` isn't being applied) or `error` (network failure,
timeout, 4xx/5xx, or a redirect with no `Location`). URL comparison is
lenient about scheme/host case and trailing slashes, so
`https://Example.com/x/` still matches `https://example.com/x`.

The `fetcher` parameter makes the whole layer testable offline: it
defaults to a stdlib `urllib` HEAD request, and any callable returning
`(http_status, {header: value})` can be substituted — which is exactly
how the test suite covers every branch without a network.

### src.generator

| Class | Role |
|---|---|
| `HtmlBuilder(template_path=None, site_domain=...)` | renders redirect pages, the 404 page and `links.json` |
| `FolderCreator(output_dir, template_path, htaccess_template, site_domain, home_url)` | `plan(links)` previews the build; `generate(links, clean=True)` writes the whole tree |
| `ZipPackager(source_dir, zip_path)` | `package()` → `(zip_path, file_count)` |

Both `plan` and `generate` validate their input themselves — calling
them with raw pairs is safe.

### src.utils

`setup_logging(level, console, logfile)` configures the shared `fedlink`
logger; `clean_directory(path)` empties a folder while preserving
`.keep` and `.git`.

## Template rendering

`HtmlBuilder.render(template, values)` replaces `{{ name }}` placeholders
with `str(value)`; unknown names stay literal. `{{url_js}}` is expected
to be produced with `json.dumps(url)` for a safe JS string literal.

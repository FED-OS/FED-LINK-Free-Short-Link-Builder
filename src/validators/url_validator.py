"""Link and URL validation for FED-LINk.

A short link bundle is only as good as the data going in, so every entry
is checked before a single file is written:

* slugs must be filesystem-safe (they become folder names on InfinityFree)
* URLs must be absolute with a scheme and host
* nothing may shadow a file the redirect site itself needs

The functions raise ``LinkValidationError`` with a message that points at
the offending entry, so CLI and GUI users both get actionable feedback.

The ``check_*`` helpers (added in v1.1, ROADMAP) go one step further: they
verify the *deployed* short links over HTTP with HEAD requests, using only
the standard library, so the ``check`` CLI command works everywhere with
no extra dependencies.
"""

import re
import dataclasses
import ipaddress
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlsplit

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-_]*$")
_SLUG_MAX = 64

ALLOWED_SCHEMES = ("http", "https")

# Slugs that cannot be used because the deployed redirect site (or the
# Apache server on InfinityFree) already owns those paths:
#   - cgi-bin / well-known / htdocs are managed by the web server itself
#   - 404 / 403 / 500 would shadow the ErrorDocument fallback pages
RESERVED_WORDS = frozenset({
    "cgi-bin", "well-known", "htdocs", "404", "403", "500",
})

SAFE_TARGET_HOSTS = (
    "github.io",
    "github.com",
    "gitlab.io",
    "pages.dev",
    "vercel.app",
    "netlify.app",
    "herokuapp.com",
    "fly.dev",
    "onrender.com",
    "railway.app",
    "repl.co",
    "glitch.me",
    "bitbucket.io",
    "sourceforge.net",
    "npm.io",
    "readthedocs.io",
    "neocities.org",
    "blogspot.com",
    "wordpress.com",
    "medium.com",
    "substack.com",
    "linkedin.com",
    "figma.com",
    "dribbble.com",
    "behance.net",
    "deviantart.com",
    "artstation.com",
    "youtube.com",
    "youtu.be",
    "vimeo.com",
    "twitch.tv",
    "spotify.com",
    "soundcloud.com",
    "bandcamp.com",
    "patreon.com",
    "ko-fi.com",
    "buymeacoffee.com",
    "paypal.com",
    "stripe.com",
    "gumroad.com",
    "itch.io",
    "steampowered.com",
    "gog.com",
    "epicgames.com",
    "xbox.com",
    "playstation.com",
    "nintendo.com",
    "roblox.com",
    "minecraft.net",
    "unity.com",
    "unrealengine.com",
    "godotengine.org",
    "fedpromptly.com",
    "infinityfree.com",
    "ionos.com",
    "cloudflare.com",
    "workers.dev",
    "duckdns.org",
)


class LinkValidationError(ValueError):
    """Raised when a short link entry fails validation."""


def validate_slug(slug: object, strict_case: bool = False) -> str:
    """Validate and normalise a short-code slug; return it lower-cased.

    Rules: lowercase letters, digits, ``-`` and ``_`` only, must start
    alphanumeric, max 64 chars, and must not be a reserved word. This keeps
    the slug usable as both a folder name and an .htaccess path.

    With ``strict_case=True`` (v1.1, ``--strict-case``) mixed-case input is
    rejected instead of being silently lower-cased, for teams that want the
    links file to be the literal source of truth.
    """
    if not isinstance(slug, str) or not slug.strip():
        raise LinkValidationError("slug must be a non-empty string")

    candidate = slug.strip()
    if strict_case and candidate != candidate.lower():
        raise LinkValidationError(
            f"slug '{candidate}' contains uppercase letters (strict case) — "
            "write it in lowercase or drop --strict-case"
        )
    candidate = candidate.lower()
    if len(candidate) > _SLUG_MAX:
        raise LinkValidationError(
            f"slug '{candidate}' is longer than {_SLUG_MAX} characters"
        )
    if not _SLUG_RE.match(candidate):
        raise LinkValidationError(
            f"slug '{candidate}' may only contain a-z, 0-9, '-' and '_' "
            "(and must start with a letter or digit)"
        )
    if candidate in RESERVED_WORDS:
        raise LinkValidationError(
            f"slug '{candidate}' is reserved by the redirect site "
            f"or the build pipeline"
        )
    return candidate


def validate_url(url: object) -> str:
    """Validate an absolute destination URL; return it unchanged.

    Must be http(s) with a non-empty host. Underscore hosts (never legal in
    DNS) are rejected because Apache and most browsers choke on them.
    Localhost and private addresses are accepted for local testing only
    when ``allow_private_hosts`` is enabled.
    """
    if not isinstance(url, str) or not url.strip():
        raise LinkValidationError("url must be a non-empty string")

    target = url.strip()

    split = urlsplit(target)
    if not split.scheme:
        raise LinkValidationError(
            f"url '{target}' is missing a scheme (use https://...)"
        )
    if split.scheme.lower() not in ALLOWED_SCHEMES:
        raise LinkValidationError(
            f"url '{target}' uses scheme '{split.scheme}' — only "
            f"{', '.join(ALLOWED_SCHEMES)} are allowed"
        )
    if not split.netloc:
        raise LinkValidationError(f"url '{target}' has no host")
    if "_" in split.netloc:
        raise LinkValidationError(
            f"url '{target}' contains an underscore in the host, which is "
            "not a valid DNS name"
        )

    return target


def _host_is_local(hostname: str) -> bool:
    if hostname in ("localhost", "::1", "0.0.0.0"):
        return True
    try:
        ipaddress.ip_address(hostname).is_private
        return True
    except ValueError:
        return False


def _looks_private(url: str) -> bool:
    split = urlsplit(url)
    hostname = (split.hostname or "").lower()
    return _host_is_local(hostname) or hostname.endswith(".local")


def validate_link(slug: object, url: object, allow_private: bool = False,
                  strict_case: bool = False) -> tuple[str, str]:
    """Validate one (slug, url) pair; return the normalised pair."""
    safe_slug = validate_slug(slug, strict_case=strict_case)
    safe_url = validate_url(url)
    if not allow_private and _looks_private(safe_url):
        raise LinkValidationError(
            f"url '{safe_url}' points at a private/localhost host — "
            "these are not reachable from link.fedpromptly.com"
        )
    return safe_slug, safe_url


def validate_links(links: object, allow_private: bool = False,
                   strict_case: bool = False) -> dict[str, str]:
    """Validate an iterable of (slug, url) pairs; return an ordered mapping.

    Duplicated slugs after lower-casing are an error (they would generate
    two folders fighting over the same path). Entry order is preserved so
    ``.htaccess`` rules stay stable across builds.
    """
    if links is None:
        raise LinkValidationError("links payload is empty")

    result: dict[str, str] = {}
    seen: dict[str, str] = {}
    for index, pair in enumerate(links):
        try:
            slug, url = pair
        except (TypeError, ValueError) as exc:
            raise LinkValidationError(
                f"entry #{index + 1} is not a (slug, url) pair: {pair!r}"
            ) from exc
        try:
            safe_slug, safe_url = validate_link(
                slug, url, allow_private, strict_case=strict_case)
        except LinkValidationError as exc:
            raise LinkValidationError(f"entry #{index + 1}: {exc}") from None
        if safe_slug in seen:
            raise LinkValidationError(
                f"slug '{safe_slug}' is used more than once "
                f"('{seen[safe_slug]}' and '{safe_url}')"
            )
        seen[safe_slug] = safe_url
        result[safe_slug] = safe_url
    return result


# ---------------------------------------------------------------------- #
# live deployment checks (v1.1, ROADMAP: ``check`` command)
# ---------------------------------------------------------------------- #
_REDIRECT_STATUSES = frozenset({301, 302, 307, 308})

_CHECK_USER_AGENT = "FED-LINk-check/1.1 (+https://github.com/fedpromptly/infinityfree-shortener-builder)"


@dataclasses.dataclass
class CheckResult:
    """Outcome of one live HEAD check against a deployed short link.

    ``status`` is one of:

    * ``ok`` — HTTP 301/302/307/308 and the ``Location`` matches the links file
    * ``wrong-target`` — a redirect, but pointing somewhere else
    * ``no-redirect`` — HTTP 2xx: the host served a page (missing ``.htaccess``)
    * ``error`` — network failure, timeout, or 4xx/5xx
    """

    slug: str
    url: str                # expected destination (from the links file)
    check_url: str          # deployed short URL that was probed
    status: str
    http_status: int = 0
    location: str | None = None
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "ok"

    def as_dict(self) -> dict[str, object]:
        """Return a plain dict (for ``--format json``)."""
        return dataclasses.asdict(self)


def build_check_url(site_domain: str, slug: str) -> str:
    """Return the deployed short URL for ``slug``.

    A bare domain is turned into ``https://<domain>/<slug>``; a domain that
    already carries a scheme is respected as-is (useful for staging hosts).
    """
    domain = (site_domain or "").strip().rstrip("/")
    if not domain:
        raise LinkValidationError("site domain is empty")
    if "://" not in domain:
        domain = f"https://{domain}"
    return f"{domain}/{slug}"


class _NoRedirects(urllib.request.HTTPRedirectHandler):
    """Redirect handler that refuses to follow, so 3xx responses surface."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        return None


_opener = urllib.request.build_opener(_NoRedirects)


def _default_fetcher(url: str, timeout: float) -> tuple[int, dict[str, str]]:
    """HEAD ``url`` without following redirects; return (status, headers)."""
    request = urllib.request.Request(
        url, method="HEAD", headers={"User-Agent": _CHECK_USER_AGENT})
    try:
        with _opener.open(request, timeout=timeout) as response:
            return int(response.status), _lower_keys(response.headers.items())
    except urllib.error.HTTPError as exc:  # 3xx/4xx/5xx land here
        items = exc.headers.items() if exc.headers else []
        return int(exc.code), _lower_keys(items)


def _lower_keys(items) -> dict[str, str]:
    return {str(key).lower(): str(value) for key, value in items}


def _same_url(left: str, right: str) -> bool:
    """Compare URLs ignoring case in scheme/host and trailing slashes."""
    def normal(value: str):
        split = urlsplit(value.strip())
        return (split.scheme.lower(), split.netloc.lower(),
                split.path.rstrip("/"), split.query)
    return normal(left) == normal(right)


def evaluate_redirect(slug: str, check_url: str, expected_url: str,
                      timeout: float = 10.0,
                      fetcher=None) -> CheckResult:
    """Probe one deployed short link; never follow the redirect.

    ``fetcher`` defaults to a stdlib HEAD request and must return
    ``(http_status, {header: value})``; it is a parameter precisely so the
    test suite can exercise every branch offline.
    """
    fetch = fetcher or _default_fetcher
    try:
        status, headers = fetch(check_url, timeout)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, "reason", None) or exc
        return CheckResult(slug, expected_url, check_url, "error", 0, None,
                           f"request failed: {reason}")

    if status in _REDIRECT_STATUSES:
        location = headers.get("location")
        if not location:
            return CheckResult(slug, expected_url, check_url, "error", status,
                               None, f"HTTP {status} without a Location header")
        resolved = urljoin(check_url, location)
        if _same_url(resolved, expected_url):
            return CheckResult(slug, expected_url, check_url, "ok", status,
                               resolved, f"HTTP {status} -> {resolved}")
        return CheckResult(slug, expected_url, check_url, "wrong-target",
                           status, resolved,
                           f"HTTP {status} -> {resolved} "
                           f"(expected {expected_url})")

    if 200 <= status < 300:
        return CheckResult(slug, expected_url, check_url, "no-redirect",
                           status, None,
                           f"HTTP {status} served a page instead of "
                           "redirecting (.htaccess missing or ignored?)")
    return CheckResult(slug, expected_url, check_url, "error", status, None,
                       f"HTTP {status}")


def check_links(links: object, site_domain: str = "link.fedpromptly.com",
                timeout: float = 10.0, fetcher=None,
                allow_private: bool = False,
                strict_case: bool = False) -> list[CheckResult]:
    """Validate then live-check every short link on the deployed host.

    Returns one :class:`CheckResult` per link, in links-file order. The
    mapping is validated first so a broken file fails with the usual
    actionable message instead of a wall of DNS errors.
    """
    mapping = validate_links(links, allow_private=allow_private,
                             strict_case=strict_case)
    return [
        evaluate_redirect(slug,
                          build_check_url(site_domain, slug),
                          url,
                          timeout=timeout,
                          fetcher=fetcher)
        for slug, url in mapping.items()
    ]

"""Tests for the validator layer: slugs, URLs and whole link sets."""

import pytest

from src.validators import (
    LinkValidationError,
    build_check_url,
    check_links,
    evaluate_redirect,
    validate_link,
    validate_links,
    validate_slug,
    validate_url,
)


class TestValidateSlug:
    def test_accepts_simple_slug(self):
        assert validate_slug("portfolio") == "portfolio"

    def test_lowercases_and_strips(self):
        assert validate_slug("  Portfolio ") == "portfolio"

    def test_accepts_digits_hyphens_underscores(self):
        assert validate_slug("game-2_v2") == "game-2_v2"

    def test_rejects_empty(self):
        with pytest.raises(LinkValidationError):
            validate_slug("")

    def test_rejects_none(self):
        with pytest.raises(LinkValidationError):
            validate_slug(None)

    def test_uppercase_is_normalised_not_rejected(self):
        # uppercase input is lower-cased, so it is accepted
        assert validate_slug("Portfolio") == "portfolio"

    def test_rejects_slashes(self):
        with pytest.raises(LinkValidationError):
            validate_slug("a/b")

    def test_rejects_dots(self):
        with pytest.raises(LinkValidationError):
            validate_slug("a.b")

    def test_rejects_leading_hyphen(self):
        with pytest.raises(LinkValidationError):
            validate_slug("-portfolio")

    def test_rejects_too_long_slug(self):
        with pytest.raises(LinkValidationError):
            validate_slug("a" * 65)

    def test_accepts_64_char_slug(self):
        assert len(validate_slug("a" * 64)) == 64

    def test_rejects_reserved_words(self):
        for reserved in ("cgi-bin", "well-known", "htdocs", "404", "403", "500"):
            with pytest.raises(LinkValidationError):
                validate_slug(reserved)


class TestValidateUrl:
    def test_accepts_https(self):
        assert validate_url("https://example.com") == "https://example.com"

    def test_accepts_http(self):
        assert validate_url("http://example.com/page") == "http://example.com/page"

    def test_rejects_missing_scheme(self):
        with pytest.raises(LinkValidationError):
            validate_url("example.com")

    def test_rejects_ftp(self):
        with pytest.raises(LinkValidationError):
            validate_url("ftp://example.com/file")

    def test_rejects_empty(self):
        with pytest.raises(LinkValidationError):
            validate_url("")

    def test_rejects_none(self):
        with pytest.raises(LinkValidationError):
            validate_url(None)

    def test_rejects_scheme_only(self):
        with pytest.raises(LinkValidationError):
            validate_url("https://")

    def test_rejects_underscore_host(self):
        with pytest.raises(LinkValidationError):
            validate_url("https://my_host.example.com")


class TestValidateLink:
    def test_valid_pair_is_normalised(self):
        assert validate_link("Portfolio", "https://example.com") == (
            "portfolio", "https://example.com"
        )

    def test_private_url_rejected_by_default(self):
        with pytest.raises(LinkValidationError):
            validate_link("local", "http://localhost:8000")

    def test_private_url_allowed_with_flag(self):
        assert validate_link("local", "http://localhost:8000",
                             allow_private=True) == ("local", "http://localhost:8000")


class TestValidateLinks:
    def test_returns_ordered_mapping(self):
        mapping = validate_links([("b", "https://b.com"), ("a", "https://a.com")])
        assert list(mapping) == ["b", "a"]
        assert mapping == {"b": "https://b.com", "a": "https://a.com"}

    def test_rejects_duplicate_slugs(self):
        with pytest.raises(LinkValidationError, match="more than once"):
            validate_links([
                ("portfolio", "https://one.example"),
                ("Portfolio", "https://two.example"),
            ])

    def test_rejects_none_payload(self):
        with pytest.raises(LinkValidationError):
            validate_links(None)

    def test_rejects_malformed_pair(self):
        with pytest.raises(LinkValidationError, match="not a .slug, url. pair"):
            validate_links(["just-a-string"])

    def test_error_mentions_entry_number(self):
        with pytest.raises(LinkValidationError, match="entry #2"):
            validate_links([
                ("good", "https://good.example"),
                ("bad slug", "https://bad.example"),
            ])


class TestStrictCase:
    """``--strict-case`` (v1.1): mixed-case slugs are an error, not a fix."""

    def test_lowercase_slugs_still_pass(self):
        mapping = validate_links(
            [("portfolio", "https://example.com/")], strict_case=True)
        assert list(mapping) == ["portfolio"]

    def test_mixed_case_slug_is_rejected(self):
        with pytest.raises(LinkValidationError, match="uppercase"):
            validate_links(
                [("Portfolio", "https://example.com/")], strict_case=True)

    def test_rejection_mentions_the_slug(self):
        with pytest.raises(LinkValidationError, match="'Portfolio'"):
            validate_slug("Portfolio", strict_case=True)

    def test_default_still_normalises(self):
        # without the flag, uppercase is lower-cased as before (v1.0 behaviour)
        assert validate_slug("Portfolio") == "portfolio"


class TestBuildCheckUrl:
    def test_bare_domain_gets_https(self):
        assert (build_check_url("link.fedpromptly.com", "docs")
                == "https://link.fedpromptly.com/docs")

    def test_trailing_slash_is_trimmed(self):
        assert (build_check_url("link.fedpromptly.com/", "docs")
                == "https://link.fedpromptly.com/docs")

    def test_explicit_scheme_is_respected(self):
        assert (build_check_url("http://staging.example", "docs")
                == "http://staging.example/docs")

    def test_empty_domain_is_rejected(self):
        with pytest.raises(LinkValidationError):
            build_check_url("", "docs")


class TestEvaluateRedirect:
    """Every branch of the live-check verdict, using a fake fetcher."""

    SHORT = "https://link.fedpromptly.com/docs"
    TARGET = "https://fedpromptly.github.io/docs"

    def test_matching_301_is_ok(self):
        result = evaluate_redirect(
            "docs", self.SHORT, self.TARGET,
            fetcher=lambda url, timeout: (
                301, {"location": "https://fedpromptly.github.io/docs"}))
        assert result.ok
        assert result.status == "ok"
        assert result.http_status == 301

    def test_all_redirect_variants_count(self):
        for code in (301, 302, 307, 308):
            result = evaluate_redirect(
                "docs", self.SHORT, self.TARGET,
                fetcher=lambda url, timeout, c=code: (
                    c, {"location": self.TARGET}))
            assert result.status == "ok", code

    def test_trailing_slash_difference_is_tolerated(self):
        result = evaluate_redirect(
            "docs", self.SHORT, self.TARGET + "/",
            fetcher=lambda url, timeout: (301, {"location": self.TARGET}))
        assert result.ok

    def test_host_case_difference_is_tolerated(self):
        result = evaluate_redirect(
            "docs", self.SHORT, "https://FEDpromptly.github.io/docs",
            fetcher=lambda url, timeout: (
                301, {"location": "https://fedpromptly.github.io/docs"}))
        assert result.ok

    def test_other_target_is_wrong_target(self):
        result = evaluate_redirect(
            "docs", self.SHORT, self.TARGET,
            fetcher=lambda url, timeout: (
                301, {"location": "https://wrong.example.com/"}))
        assert result.status == "wrong-target"
        assert not result.ok

    def test_success_status_is_no_redirect(self):
        result = evaluate_redirect(
            "docs", self.SHORT, self.TARGET,
            fetcher=lambda url, timeout: (200, {}))
        assert result.status == "no-redirect"
        assert ".htaccess" in result.detail

    def test_missing_location_header_is_error(self):
        result = evaluate_redirect(
            "docs", self.SHORT, self.TARGET,
            fetcher=lambda url, timeout: (301, {}))
        assert result.status == "error"
        assert "Location" in result.detail

    def test_client_error_is_error(self):
        result = evaluate_redirect(
            "docs", self.SHORT, self.TARGET,
            fetcher=lambda url, timeout: (404, {}))
        assert result.status == "error"
        assert result.http_status == 404

    def test_network_failure_is_error(self):
        def broken_fetcher(url, timeout):
            raise OSError("no route to host")
        result = evaluate_redirect(
            "docs", self.SHORT, self.TARGET, fetcher=broken_fetcher)
        assert result.status == "error"
        assert "no route to host" in result.detail

    def test_relative_location_is_resolved(self):
        result = evaluate_redirect(
            "docs", self.SHORT, self.TARGET,
            fetcher=lambda url, timeout: (
                301, {"location": "https://fedpromptly.github.io/docs"}))
        assert result.ok
        assert result.as_dict()["slug"] == "docs"


class TestCheckLinks:
    LINKS = [("docs", "https://fedpromptly.github.io/docs"),
             ("blog", "https://fedpromptly.github.io/blog")]

    def _fetcher_by_slug(self):
        seen = []

        def fetch(url, timeout):
            seen.append(url)
            slug = url.rsplit("/", 1)[-1]
            target = f"https://fedpromptly.github.io/{slug}"
            return 301, {"location": target}
        return fetch, seen

    def test_checks_every_link_in_file_order(self):
        fetch, seen = self._fetcher_by_slug()
        results = check_links(self.LINKS, site_domain="link.fedpromptly.com",
                              fetcher=fetch)
        assert [r.slug for r in results] == ["docs", "blog"]
        assert seen == ["https://link.fedpromptly.com/docs",
                        "https://link.fedpromptly.com/blog"]

    def test_all_ok_when_targets_match(self):
        fetch, _ = self._fetcher_by_slug()
        results = check_links(self.LINKS, fetcher=fetch)
        assert all(result.ok for result in results)

    def test_invalid_links_fail_before_any_request(self):
        with pytest.raises(LinkValidationError):
            check_links([("bad slug", "https://example.com/")])

    def test_strict_case_is_forwarded(self):
        with pytest.raises(LinkValidationError, match="uppercase"):
            check_links([("Docs", "https://example.com/")],
                        strict_case=True)

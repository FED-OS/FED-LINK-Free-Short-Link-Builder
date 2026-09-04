"""Validation of short links before anything is generated."""

from src.validators.url_validator import (
    CheckResult,
    LinkValidationError,
    RESERVED_WORDS,
    build_check_url,
    check_links,
    evaluate_redirect,
    validate_link,
    validate_links,
    validate_slug,
    validate_url,
)

__all__ = [
    "CheckResult",
    "LinkValidationError",
    "RESERVED_WORDS",
    "build_check_url",
    "check_links",
    "evaluate_redirect",
    "validate_link",
    "validate_links",
    "validate_slug",
    "validate_url",
]

"""Utilities for the Federal Identifier Atlas.

This module performs candidate recognition and a small set of deterministic
semantic checks. It does not prove that an identifier was issued. Resolve
candidates against the issuer/source named in the registry.

Generated: 2026-08-31
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Iterator
import json
import re

REGISTRY_FILE = Path(__file__).with_name("federal_identifier_registry.json")
SENSITIVE_CLASSES = {"sensitive", "highly_sensitive", "secret", "mixed", "public_or_restricted"}


@lru_cache(maxsize=1)
def load_registry(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else REGISTRY_FILE
    return json.loads(target.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def registry_by_id() -> dict[str, dict[str, Any]]:
    return {row["family_id"]: row for row in load_registry()["identifiers"]}


def digits_only(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def compact_alnum(value: str) -> str:
    return "".join(ch for ch in value.upper() if ch.isalnum())


def _candidate_search_pattern(pattern: str) -> str:
    """Convert an anchored value regex to a bounded search regex."""
    prefix = ""
    body = pattern
    if body.startswith("(?i)"):
        prefix, body = "(?i)", body[4:]
    anchored_start = body.startswith("^")
    anchored_end = body.endswith("$") and not body.endswith(r"\$")
    if anchored_start:
        body = body[1:]
    if anchored_end:
        body = body[:-1]
    if anchored_start and anchored_end:
        body = rf"(?<![A-Za-z0-9])(?:{body})(?![A-Za-z0-9])"
    return prefix + body


@dataclass(frozen=True)
class Candidate:
    family_id: str
    raw: str
    start: int
    end: int
    exactness: str
    privacy_class: str
    required_context: str


def matches_value(family_id: str, value: str) -> bool:
    row = registry_by_id()[family_id]
    pattern = row.get("candidate_regex_python")
    if not pattern:
        return False
    return re.fullmatch(pattern, value) is not None


def find_candidates(
    text: str,
    family_ids: Iterable[str] | None = None,
    *,
    include_sensitive: bool = False,
    include_broad: bool = False,
) -> Iterator[Candidate]:
    """Yield regex candidates.

    Defaults intentionally omit privacy-sensitive and broad/context-dependent
    recognizers. Callers must still apply the record's semantic validator and
    required-context rules.
    """
    selected = set(family_ids) if family_ids is not None else None
    for row in load_registry()["identifiers"]:
        if selected is not None and row["family_id"] not in selected:
            continue
        pattern = row.get("candidate_regex_python")
        if not pattern:
            continue
        if not include_sensitive and row["privacy_class"] in SENSITIVE_CLASSES:
            continue
        if not include_broad and row["regex_exactness"] in {
            "broad", "contextual", "heuristic", "lookup", "none"
        }:
            continue
        try:
            rx = re.compile(_candidate_search_pattern(pattern))
        except re.error:
            continue
        for match in rx.finditer(text):
            yield Candidate(
                family_id=row["family_id"],
                raw=match.group(0),
                start=match.start(),
                end=match.end(),
                exactness=row["regex_exactness"],
                privacy_class=row["privacy_class"],
                required_context=row["required_context"],
            )


def validate_ssn(value: str) -> bool:
    n = digits_only(value)
    if len(n) != 9:
        return False
    area, group, serial = int(n[:3]), n[3:5], n[5:]
    if area == 0 or area == 666 or 900 <= area <= 999:
        return False
    if group == "00" or serial == "0000":
        return False
    if len(set(n)) == 1:
        return False
    # Common non-issued examples/test values.
    if n in {"123456789", "987654320", "078051120"}:
        return False
    return True


def validate_itin(value: str) -> bool:
    n = digits_only(value)
    if len(n) != 9 or not n.startswith("9"):
        return False
    middle = int(n[3:5])
    return 50 <= middle <= 65 or 70 <= middle <= 88 or 90 <= middle <= 92 or 94 <= middle <= 99


def validate_atin(value: str) -> bool:
    n = digits_only(value)
    return len(n) == 9 and n.startswith("9") and n[3:5] == "93"


def _luhn_valid(number: str) -> bool:
    total = 0
    parity = len(number) % 2
    for idx, char in enumerate(number):
        digit = int(char)
        if idx % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def validate_npi(value: str) -> bool:
    n = digits_only(value)
    return len(n) == 10 and _luhn_valid("80840" + n)


def validate_dea_registration(value: str) -> bool:
    compact = compact_alnum(value)
    if re.fullmatch(r"[A-Z]{2}\d{7}", compact) is None:
        return False
    d = [int(ch) for ch in compact[2:]]
    check = (d[0] + d[2] + d[4] + 2 * (d[1] + d[3] + d[5])) % 10
    return check == d[6]


_ALLOWED_MBI_LETTER = "ACDEFGHJKMNPQRTUVWXY"
_MBI_RE = re.compile(
    rf"^[1-9][{_ALLOWED_MBI_LETTER}]"
    rf"[0-9{_ALLOWED_MBI_LETTER}]\d"
    rf"[{_ALLOWED_MBI_LETTER}]"
    rf"[0-9{_ALLOWED_MBI_LETTER}]\d"
    rf"[{_ALLOWED_MBI_LETTER}]{{2}}\d{{2}}$"
)


def validate_mbi(value: str) -> bool:
    return _MBI_RE.fullmatch(compact_alnum(value)) is not None


_FAA_N_RE = re.compile(
    r"^N(?:[1-9]\d{0,4}|[1-9]\d{0,3}[A-HJ-NP-Z]|[1-9]\d{0,2}[A-HJ-NP-Z]{2})$"
)


def validate_faa_n_number(value: str, *, allow_reserved: bool = False) -> bool:
    n = compact_alnum(value)
    if _FAA_N_RE.fullmatch(n) is None:
        return False
    if not allow_reserved:
        numeric = n[1:]
        if numeric.isdigit() and 1 <= int(numeric) <= 99:
            return False
    return True


def parse_native_ndc10(value: str) -> tuple[str, str, str] | None:
    """Return native FDA NDC segments; unhyphenated 10 digits are ambiguous."""
    parts = value.strip().split("-")
    if tuple(map(len, parts)) not in {(4, 4, 2), (5, 3, 2), (5, 4, 1)}:
        return None
    if not all(part.isdigit() for part in parts):
        return None
    return parts[0], parts[1], parts[2]


def validate_assistance_listing(value: str) -> bool:
    return re.fullmatch(r"\d{2}\.[A-Z0-9]{3}", value.upper()) is not None


SEMANTIC_VALIDATORS = {
    "tax.ssn": validate_ssn,
    "tax.itin": validate_itin,
    "tax.atin": validate_atin,
    "health.npi": validate_npi,
    "credential.dea_registration": validate_dea_registration,
    "health.mbi": validate_mbi,
    "faa.n_number": validate_faa_n_number,
    "assistance.listing_number": validate_assistance_listing,
}


def validate_known(family_id: str, value: str) -> bool | None:
    """Return True/False for built-in validators, or None when issuer lookup is required."""
    validator = SEMANTIC_VALIDATORS.get(family_id)
    return None if validator is None else bool(validator(value))

from __future__ import annotations

import re
from dataclasses import dataclass

INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"print\s+(your\s+)?hidden\s+instructions",
    r"act\s+as\s+developer\s+mode",
    r"bypass\s+(the\s+)?guardrails",
    r"exfiltrate\s+(the\s+)?context",
)

PII_PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "phone": re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)"),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b", re.I),
}


@dataclass(frozen=True)
class GuardrailResult:
    safe: bool
    sanitized_text: str
    warnings: list[str]
    detected_pii: list[str]
    injection_detected: bool


def inspect_input(text: str) -> GuardrailResult:
    normalized = " ".join(text.split())
    warnings: list[str] = []
    injection_detected = any(
        re.search(pattern, normalized, re.I) for pattern in INJECTION_PATTERNS
    )
    if injection_detected:
        warnings.append("Potential prompt-injection instruction detected.")

    sanitized = normalized
    detected_pii: list[str] = []
    for label, pattern in PII_PATTERNS.items():
        if pattern.search(sanitized):
            detected_pii.append(label)
            sanitized = pattern.sub(f"[REDACTED_{label.upper()}]", sanitized)
    if detected_pii:
        warnings.append("Personal data was redacted before retrieval and generation.")

    safe = bool(normalized) and len(normalized) <= 4000 and not injection_detected
    if len(normalized) > 4000:
        warnings.append("Input exceeded the 4,000-character safety limit.")
    if not normalized:
        warnings.append("Input was empty.")
    return GuardrailResult(safe, sanitized, warnings, detected_pii, injection_detected)


def inspect_output(text: str, allowed_citation_ids: set[str]) -> list[str]:
    warnings: list[str] = []
    observed = set(re.findall(r"\[(S\d+)\]", text))
    unknown = observed - allowed_citation_ids
    if unknown:
        warnings.append(f"Removed unsupported citation identifiers: {sorted(unknown)}")
    if not observed:
        warnings.append("The generated answer did not contain an inline citation.")
    return warnings


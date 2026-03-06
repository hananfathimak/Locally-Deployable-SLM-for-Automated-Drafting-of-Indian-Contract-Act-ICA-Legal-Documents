import re

MANDATORY_HEADINGS = [
    "facts",
    "cause of action",
    "jurisdiction",
    "valuation",
    "court fee",
    "prayer"
]

ALLOWED_HEADINGS = [
    "facts",
    "cause of action",
    "jurisdiction",
    "valuation",
    "court fee",
    "claim",
    "prayer",
    "verification"
]


def _extract_sections(text: str):
    pattern = r"\n?\s*(\d+)\.\s+([A-Za-z ]+)"
    matches = re.findall(pattern, text)

    sections = []
    for num, title in matches:
        sections.append((int(num), title.strip().lower()))

    return sections


def _validate_section_numbers(sections):
    errors = []
    for i, (num, _) in enumerate(sections):
        if num != i + 1:
            errors.append("Section numbers are not sequential")
            break
    return errors


def _check_mandatory_headings(sections):
    errors = []
    present = [title for _, title in sections]

    for heading in MANDATORY_HEADINGS:
        if heading not in present:
            errors.append(f"Missing mandatory section: {heading}")

    return errors


def _detect_hallucinated_sections(sections):
    errors = []

    for _, title in sections:
        if title not in ALLOWED_HEADINGS:
            errors.append(f"Unexpected section detected: {title}")

    return errors


def _extract_money_values(text: str):
    pattern = r"(?:rs\.?|₹)\s?([\d,]+)"
    matches = re.findall(pattern, text.lower())

    values = []
    for m in matches:
        values.append(int(m.replace(",", "")))

    return values


def _validate_monetary_consistency(text: str):
    errors = []
    values = _extract_money_values(text)

    for value in values:
        if value <= 0:
            errors.append("Invalid monetary value detected")

    return errors


def validate_draft(draft: str) -> dict:
    errors = []

    sections = _extract_sections(draft)

    errors.extend(_validate_section_numbers(sections))
    errors.extend(_check_mandatory_headings(sections))
    errors.extend(_detect_hallucinated_sections(sections))
    errors.extend(_validate_monetary_consistency(draft))

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }
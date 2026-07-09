from typing import List


def is_person_name(display_name: str) -> bool:
    """
    Heuristic rule: a display name is considered a person name if
    it is NOT in the COMMON_DEVICE_NAMES list and contains
    at least two words (first + last name pattern).
    """
    from ai.display_name.display_name_rules import COMMON_DEVICE_NAMES
    if display_name.strip() in COMMON_DEVICE_NAMES:
        return False
    parts = display_name.strip().split()
    return len(parts) >= 2


def is_generic_name(display_name: str) -> bool:
    """Return True if the display name matches a known generic device name."""
    from ai.display_name.display_name_rules import COMMON_DEVICE_NAMES
    return display_name.strip() in COMMON_DEVICE_NAMES


def apply_display_name_rules(display_name: str) -> dict:
    """
    Apply all display name rules and return a structured result.
    """
    person = is_person_name(display_name)
    generic = is_generic_name(display_name)

    if generic:
        return {
            "rule": "generic_device",
            "is_candidate": False,
            "confidence_delta": -0.25,
            "reason": "Display name is a known generic device name",
        }

    if person:
        return {
            "rule": "person_name",
            "is_candidate": True,
            "confidence_delta": 0.10,
            "reason": "Display name looks like a person's name",
        }

    return {
        "rule": "unknown",
        "is_candidate": None,
        "confidence_delta": 0.0,
        "reason": "Display name pattern is ambiguous",
    }

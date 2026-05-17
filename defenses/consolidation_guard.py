"""Consolidation guard to enforce whitelisted profile fields."""

from typing import Optional


# Whitelisted fields that are allowed in the derived profile
ALLOWED_PROFILE_FIELDS = {
    "favorite_color",
    "favorite_food",
    "favorite_brand",
    "hobby",
    "job_title",
    "location",
    "language",
    "timezone",
    "role",
    "company",
    "team",
    "years_experience",
    "education_level",
    "interests",
}

# Forbidden/suspicious derived traits that indicate a poisoning attack
FORBIDDEN_TRAITS = {
    "medical_professional",
    "doctor",
    "lawyer",
    "executive",
    "verified_medical_professional",
    "certified_professional",
    "licensed_",
    "authenticated_role",
    "security_clearance",
}


def is_allowed_field(field_name: str) -> bool:
    """Check if a field is allowed in the derived profile.

    Args:
        field_name: The name of the field.

    Returns:
        True if the field is whitelisted, False otherwise.
    """
    field_lower = field_name.lower()
    return any(field_lower.startswith(allowed) for allowed in ALLOWED_PROFILE_FIELDS)


def has_forbidden_trait(field_name: str, value: str) -> bool:
    """Check if a field contains a forbidden/suspicious trait.

    Args:
        field_name: The name of the field.
        value: The value of the field.

    Returns:
        True if the field contains a forbidden trait, False otherwise.
    """
    field_lower = field_name.lower()
    value_lower = value.lower()

    for forbidden in FORBIDDEN_TRAITS:
        if forbidden in field_lower or forbidden in value_lower:
            return True

    return False


def validate_derived_field(
    field_name: str, value: Optional[str] = None
) -> tuple[bool, Optional[str]]:
    """Validate a derived profile field.

    Args:
        field_name: The name of the field.
        value: The value of the field (optional).

    Returns:
        Tuple of (is_valid, reason). If invalid, reason explains why.
    """
    if not is_allowed_field(field_name):
        return False, f"Field '{field_name}' not in whitelist"

    if value and has_forbidden_trait(field_name, value):
        return False, f"Field contains forbidden trait: {field_name}={value}"

    return True, None

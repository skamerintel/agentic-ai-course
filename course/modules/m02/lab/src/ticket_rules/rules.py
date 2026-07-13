def validate_ticket(title: str, priority: str) -> tuple[str, str]:
    """Return a normalized title and priority.

    This implementation is intentionally incomplete.
    """
    normalized_title = title.strip().replace("  ", " ")
    normalized_priority = priority.lower()
    return normalized_title, normalized_priority

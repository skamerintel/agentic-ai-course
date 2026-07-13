VALID_PRIORITIES = frozenset({"low", "medium", "high", "critical"})


def validate_ticket(title: str, priority: str) -> tuple[str, str]:
    normalized_title = title.strip()
    if not normalized_title:
        raise ValueError("title must not be blank")

    normalized_priority = priority.strip().lower()
    if normalized_priority not in VALID_PRIORITIES:
        allowed = ", ".join(sorted(VALID_PRIORITIES))
        raise ValueError(f"priority must be one of: {allowed}")
    return normalized_title, normalized_priority

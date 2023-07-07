def format_time_seconds_to_str(time_seconds: int | float) -> str:
    """
    Returns a human-readable string representation of time in the appropriate unit.
    """
    units = [("s", 1), ("h", 3600), ("d", 86400), ("y", 31536000)]

    for unit, divisor in units:
        if time_seconds <= 60 * divisor:
            return f"{time_seconds / divisor:.2f}{unit}"

    return f"{time_seconds / units[-1][1]:.2f}{units[-1][0]}"

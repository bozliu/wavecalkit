from __future__ import annotations

from datetime import datetime, timedelta, timezone

JASON_TIME_ORIGIN = datetime(2000, 1, 1, tzinfo=timezone.utc)


def parse_time(value: object, *, numeric_origin: datetime = JASON_TIME_ORIGIN) -> datetime:
    """Parse ISO-like strings or numeric seconds from a configurable origin."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    text = str(value).strip()
    if not text:
        raise ValueError("empty time value")

    try:
        seconds = float(text)
    except ValueError:
        pass
    else:
        return numeric_origin + timedelta(seconds=seconds)

    normalized = text.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def format_time(value: datetime) -> str:
    dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time_window(value: str) -> float:
    """Return a tolerance in minutes."""
    text = value.strip().lower()
    if text == "exact":
        return 0.0
    if text.endswith("minutes"):
        text = text[:-7]
    elif text.endswith("minute"):
        text = text[:-6]
    elif text.endswith("mins"):
        text = text[:-4]
    elif text.endswith("min"):
        text = text[:-3]
    elif text.endswith("m"):
        text = text[:-1]
    elif text.endswith("h"):
        return float(text[:-1]) * 60.0
    return float(text)

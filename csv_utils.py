"""Strict CSV conversions shared by both command-line entry points."""
import math


def parse_csv_boolean(value):
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n", ""}:
        return False
    raise ValueError(f"invalid critical flag {value!r} (expected true or false)")


def parse_csv_float(value, field):
    try:
        result = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{field} must be a finite number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{field} must be a finite number")
    return result

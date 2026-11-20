from datetime import datetime, timezone


def moment(value):
    if not isinstance(value, str) or "T" not in value:
        raise ValueError("时间必须含日期、时刻和时区")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError("时间缺少时区")
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def intersection(start, end, edge_start, edge_end):
    left = max(start, edge_start)
    right = min(end, edge_end) if edge_end is not None else end
    return (left, right) if left < right else None

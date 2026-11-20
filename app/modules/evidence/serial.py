from app.errors import BusinessError
from app.modules.catalog.service import resolve


def serial_evidence(result, key):
    try:
        serial = resolve(result["catalog"], key)
    except ValueError:
        serial = None
    if serial is None:
        raise BusinessError("UNKNOWN_PART", "找不到该序列件", 404)
    graph = result["graph"]
    return {
        "part": result["catalog"]["parts"][serial],
        "position": next((row for row in result["balance"]["rows"] if row["serial"] == serial), None),
        "edges": [edge for edge in graph["edges"] if serial in (edge["child"], edge["parent"])],
        "accepted": [row for row in graph["accepted"] if serial in (row["serial"], row.get("parent"))],
        "issues": [row for module in ("catalog", "intake", "sequence", "graph") for row in result[module]["issues"]
                   if serial in (row.get("serial"), row.get("other_serial"), row.get("parent"), row.get("child"))],
        "exposures": [row for row in result.get("recall", {}).get("paths", []) if serial in row["path"]],
    }

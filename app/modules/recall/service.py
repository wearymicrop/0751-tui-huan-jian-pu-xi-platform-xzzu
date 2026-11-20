from app.errors import BusinessError
from app.identity import token
from app.modules.recall.windows import trace
from app.timebox import moment


def recall(catalog, graph, batch, start=None, end=None):
    parts = catalog["parts"]
    try:
        batch = token(batch)
        left = moment(start) if start is not None else min((p["registered"] for p in parts.values()), default=graph["as_of"])
        right = moment(end) if end is not None else graph["as_of"]
    except (ValueError, OverflowError) as error:
        raise BusinessError("BAD_QUERY", "批号或查询时间无效") from error
    if not any(part["batch"] == batch for part in parts.values()):
        raise BusinessError("UNKNOWN_BATCH", "找不到该批号", 404)
    if left >= right or right > graph["as_of"]:
        raise BusinessError("BAD_WINDOW", "查询起点须早于终点，终点不可超过盘点时间")
    evidence = trace(parts, batch, graph["edges"], left, right, set(catalog["disputed"]))
    targets = sorted({item["serial"] for item in evidence})
    return {"batch": batch, "start": left, "end": right, "targets": targets, "count": len(targets),
            "paths": evidence, "excluded_origins": [key for key in catalog["disputed"] if parts[key]["batch"] == batch]}

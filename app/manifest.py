import hashlib
import json
from app.config import RULE_VERSION


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def make_manifest(source, query, result):
    payload = {"version": RULE_VERSION, "source": source, "query": query, "result": result}
    raw = canonical(payload).encode("utf-8")
    return {"version": RULE_VERSION, "digest": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}

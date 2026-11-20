import json
from app.config import ROOT, SAMPLES
from app.errors import BusinessError
from app.timebox import moment


def load_sample(name):
    if name not in SAMPLES:
        raise BusinessError("UNKNOWN_SAMPLE", "找不到该样例", 404)
    return json.loads((ROOT / "sample_data" / f"{name}.json").read_text(encoding="utf-8"))


def validate_source(data):
    if not isinstance(data, dict):
        raise BusinessError("BAD_SOURCE", "数据须为 JSON 对象")
    for field in ("parts", "aliases", "returns", "events"):
        rows = data.get(field)
        if not isinstance(rows, list) or len(rows) > 2500:
            raise BusinessError("BAD_SOURCE", f"{field} 须为最多 2500 条的数组")
    try:
        as_of = moment(data.get("as_of"))
    except (ValueError, OverflowError) as error:
        raise BusinessError("BAD_TIME", "请填写带时区的盘点时间") from error
    return as_of

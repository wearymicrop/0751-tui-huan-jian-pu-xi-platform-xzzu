from app.analysis import analyze, with_recall
from app.errors import BusinessError
from app.manifest import make_manifest
from app.modules.evidence.store import save
from app.source import load_sample


def archive(source, batch, start=None, end=None):
    result = with_recall(analyze(source), batch, start, end)
    query = {key: result["recall"][key] for key in ("batch", "start", "end")}
    try:
        manifest = make_manifest(source, query, result)
    except (TypeError, ValueError) as error:
        raise BusinessError("BAD_SOURCE", "源数据含不可归档值") from error
    return {"id": manifest["digest"], "manifest": manifest, "source": source, "query": query, "result": result}


def create(payload):
    if not isinstance(payload, dict) or ("source" in payload) == ("sample" in payload):
        raise BusinessError("CHOOSE_SOURCE", "请选择一个样例或上传一份数据")
    sample = payload.get("sample")
    if "sample" in payload and not isinstance(sample, str):
        raise BusinessError("CHOOSE_SOURCE", "样例名称须为字符串")
    source = load_sample(sample) if "sample" in payload else payload["source"]
    batch = payload.get("batch", source.get("default_batch") if isinstance(source, dict) else None)
    run = archive(source, batch, payload.get("start"), payload.get("end"))
    return {**run, "reused": save(run)}

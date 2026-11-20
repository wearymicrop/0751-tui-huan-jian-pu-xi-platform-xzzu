from fastapi import APIRouter, Body, Depends, Response
from app.analysis import with_recall
from app.dependencies import from_sample
from app.errors import BusinessError
from app.manifest import canonical
from app.modules.evidence.serial import serial_evidence
from app.modules.evidence.service import archive, create
from app.modules.evidence.store import get, recent, save

router = APIRouter()


@router.get("/api/evidence/{serial:path}")
def evidence_report(serial: str, batch: str = "CU-041", start: str | None = None, end: str | None = None,
                    run: str | None = None, result=Depends(from_sample)):
    report = get(run)["result"] if run else with_recall(result, batch, start, end)
    return serial_evidence(report, serial)


@router.get("/api/runs")
def list_runs():
    return {"runs": recent()}


@router.post("/api/runs")
def create_run(payload: object = Body(...)):
    return create(payload)


@router.get("/api/runs/{run_id}")
def get_run(run_id: str):
    return get(run_id)


@router.post("/api/runs/{run_id}/rerun")
def rerun(run_id: str):
    original = get(run_id)
    result = archive(original["source"], **original["query"])
    if result["id"] != run_id:
        raise BusinessError("DIGEST_MISMATCH", "重算摘要与归档不一致", 409)
    return {**result, "reused": save(result)}


@router.get("/api/runs/{run_id}/export")
def export_run(run_id: str):
    return Response(canonical(get(run_id)) + "\n", media_type="application/json",
                    headers={"Content-Disposition": f'attachment; filename="lineage-{run_id}.json"'})

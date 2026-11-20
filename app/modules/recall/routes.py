from fastapi import APIRouter, Depends
from app.dependencies import from_sample
from app.modules.recall.service import recall

router = APIRouter()


@router.get("/api/recall")
def recall_report(batch: str = "CU-041", start: str | None = None, end: str | None = None,
                  result=Depends(from_sample)):
    return recall(result["catalog"], result["graph"], batch, start, end)

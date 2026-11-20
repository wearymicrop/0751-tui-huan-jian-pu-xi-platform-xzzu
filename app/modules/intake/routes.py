from fastapi import APIRouter, Depends
from app.dependencies import from_sample

router = APIRouter()


@router.get("/api/intake")
def intake_report(result=Depends(from_sample)):
    return result["intake"]

from fastapi import APIRouter, Depends
from app.dependencies import from_sample

router = APIRouter()


@router.get("/api/sequence")
def sequence_report(result=Depends(from_sample)):
    return result["sequence"]

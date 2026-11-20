from fastapi import APIRouter, Depends
from app.dependencies import from_sample

router = APIRouter()


@router.get("/api/graph")
def graph_report(result=Depends(from_sample)):
    return result["graph"]

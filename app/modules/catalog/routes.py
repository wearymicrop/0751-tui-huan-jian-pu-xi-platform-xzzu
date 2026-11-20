from fastapi import APIRouter, Depends
from app.dependencies import from_sample

router = APIRouter()


@router.get("/api/catalog")
def catalog_report(result=Depends(from_sample)):
    return result["catalog"]

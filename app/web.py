from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.config import ROOT, RULE_VERSION, SAMPLES
from app.errors import BusinessError
from app.navigation import SECTIONS, TABLES

router = APIRouter()
templates = Jinja2Templates(directory=str(ROOT / "app" / "templates"))


@router.get("/", include_in_schema=False)
@router.get("/board/{section}", include_in_schema=False)
def board(request: Request, section: str = "recall", sample: str = "dirty"):
    if section not in SECTIONS or sample not in SAMPLES:
        raise BusinessError("UNKNOWN_BOARD", "找不到该工作台入口", 404)
    return templates.TemplateResponse(request=request, name="board.html", context={
        "section": section, "sections": SECTIONS, "title": SECTIONS[section], "sample": sample,
        "samples": SAMPLES, "table": TABLES.get(section), "version": RULE_VERSION,
    })

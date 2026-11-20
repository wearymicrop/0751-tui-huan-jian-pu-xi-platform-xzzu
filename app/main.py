from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import ROOT, RULE_VERSION
from app.errors import BusinessError
from app.routes import ROUTERS
from app.web import router as web_router

app = FastAPI(title="退换件谱系台")
app.mount("/static", StaticFiles(directory=ROOT / "app" / "static"), name="static")
for router in (*ROUTERS, web_router):
    app.include_router(router)


@app.exception_handler(BusinessError)
async def business_error(_request: Request, error: BusinessError):
    return JSONResponse({"code": error.code, "message": str(error)}, status_code=error.status)


@app.get("/health")
def health():
    return {"status": "ok", "version": RULE_VERSION}

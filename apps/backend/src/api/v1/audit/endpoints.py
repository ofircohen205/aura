
from fastapi import FastAPI, APIRouter

router = APIRouter()

@router.get("/", summary="Trigger audit")
async def trigger_audit(repo_path: str):
    # TODO: Connect to CLI logic or AuditService
    return {"status": "audit_started", "repo": repo_path}

def create_audit_app() -> FastAPI:
    app = FastAPI(title="Audit API")
    app.include_router(router)
    return app

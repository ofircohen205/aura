
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from datetime import datetime

class EventRequest(BaseModel):
    source: str
    type: str
    data: dict
    timestamp: datetime = datetime.now()

router = APIRouter()

@router.post("/", summary="Ingest event")
async def ingest_event(event: EventRequest):
    # TODO: Send to processing service
    return {"status": "received", "event_id": "stub-id"}

def create_events_app() -> FastAPI:
    app = FastAPI(title="Events API")
    app.include_router(router)
    return app

"""Events API Endpoints."""

from fastapi import APIRouter, FastAPI

from api.v1.events.exceptions import register_exception_handlers
from api.v1.events.schemas import EventRequest, EventResponse
from services.events.service import events_service

router = APIRouter(tags=["events"])


@router.post(
    "/",
    summary="Ingest event",
    description="Ingest and process an event from a client",
    response_model=EventResponse,
    status_code=200,
    responses={
        200: {"description": "Event ingested successfully"},
        400: {"description": "Invalid event data"},
        500: {"description": "Event processing failed"},
    },
)
async def ingest_event(event: EventRequest) -> EventResponse:
    """
    Ingest and process an event.

    This endpoint receives events from various clients (VSCode extension,
    CLI, GitHub app) and processes them for analytics, workflow triggers,
    and other downstream systems.
    """
    result = await events_service.ingest_event(
        source=event.source,
        event_type=event.type,
        data=event.data,
        timestamp=event.timestamp,
    )

    return EventResponse(**result)


def create_events_app() -> FastAPI:
    """Create and configure the events service FastAPI sub-application."""
    app = FastAPI(title="Events API")
    register_exception_handlers(app)
    app.include_router(router)
    return app

"""
Events API Schemas

Request and response models for events endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EventRequest(BaseModel):
    """Request model for event ingestion."""

    source: str = Field(..., description="Event source identifier", min_length=1)
    type: str = Field(..., description="Event type", min_length=1)
    data: dict[str, Any] = Field(..., description="Event data payload")
    timestamp: datetime | None = Field(
        default=None,
        description="Event timestamp (defaults to current time)",
    )


class EventResponse(BaseModel):
    """Response model for event ingestion."""

    status: str = Field(..., description="Event processing status")
    event_id: str = Field(..., description="Unique event identifier")
    processed_at: str = Field(..., description="ISO timestamp when event was processed")

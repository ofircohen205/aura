
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.events.endpoints import create_events_app
from src.api.v1.audit.endpoints import create_audit_app

app = FastAPI(title="Aura Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Sub-Applications
events_app = create_events_app()
audit_app = create_audit_app()

app.mount("/api/v1/events", events_app)
app.mount("/api/v1/audit", audit_app)

@app.get("/health")
def health_check():
    return {"status": "ok"}

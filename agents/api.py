"""
FastAPI REST API Server for Synthetic Biology Promoter Designer.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Synthetic Biology Promoter Designer API",
    description="Generic threshold-based evaluation demo; not a validated promoter design model.",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.exception_handler(SecurityException)
async def handle_sensitive_input(request, exc: SecurityException):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=422, content={"detail": "Sensitive identifiers are not accepted."})


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "synthetic-biology-promoter-designer", "domain": "Generic threshold evaluation", "standard": "Demonstration rules, not a biological standard", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "OPERATIONAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Unable to process the request.")


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}

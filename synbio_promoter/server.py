"""
FastAPI REST API Server for SynBio-Promoter: Thermodynamic Transcription Factor Binding & Circuit Agent.
"""
from typing import Dict, Any
from .models import FrontierPayload
from .agents import SynBioPromoterCoordinator

coordinator = SynBioPromoterCoordinator()


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel

        app = FastAPI(
            title="SynBio-Promoter: Thermodynamic Transcription Factor Binding & Circuit Agent",
            description="Designs synthetic genetic logic gates (AND/NOR/NAND) using position weight matrices (PWMs) and thermodynamic transcriptional models.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = "TASK-2026-001"
            target_identifier: str = "TARGET-BIO-KEY"
            primary_metric: float = 28.5
            secondary_metric: float = 14.2
            status_descriptor: str = "DISCORDANT_ANOMALY"
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = {}

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "synthetic-biology-promoter-designer", "domain": "Biomedical Scientific Discovery & Multi-Omics", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit")
        def api_audit(req: TaskRequest):
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            return coordinator.process(payload)

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None

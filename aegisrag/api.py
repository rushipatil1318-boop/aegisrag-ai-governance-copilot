from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .config import settings
from .orchestrator import AegisRAG

app = FastAPI(
    title="AegisRAG API",
    version="1.0.0",
    description="Evidence-grounded EU AI governance question answering and risk screening.",
)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=10)


class AssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    system_name: str = Field(min_length=2, max_length=200)
    purpose: str = Field(min_length=5, max_length=4000)
    impacts_individuals: bool = True
    employment: bool = False
    education: bool = False
    essential_services: bool = False
    law_enforcement: bool = False
    migration: bool = False
    justice: bool = False
    critical_infrastructure: bool = False
    biometric: bool = False
    medical: bool = False
    safety_component: bool = False
    generative_ai: bool = False
    public_interaction: bool = False
    personal_data: bool = False


@lru_cache(maxsize=1)
def get_rag() -> AegisRAG:
    return AegisRAG()


@app.get("/health")
def health() -> dict[str, Any]:
    rag = get_rag()
    return {"status": "healthy", **rag.source_summary()}


@app.post("/v1/ask")
def ask(request: AskRequest) -> dict[str, Any]:
    try:
        return get_rag().ask(request.question, top_k=request.top_k).to_dict()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/v1/assess")
def assess(request: AssessmentRequest) -> dict[str, Any]:
    try:
        return get_rag().assess(request.model_dump()).to_dict()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/v1/sources")
def sources() -> list[dict[str, Any]]:
    return [
        {
            "source_id": document.source_id,
            "title": document.title,
            "framework": document.framework,
            "reference": document.reference,
            "source_url": document.source_url,
            "last_verified": document.last_verified,
            "topics": list(document.topics),
        }
        for document in get_rag().documents
    ]


@app.get("/v1/evaluation")
def evaluation() -> dict[str, Any]:
    path = Path(settings.artifact_dir) / "evaluation_summary.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Run python scripts/evaluate.py first")
    return json.loads(path.read_text(encoding="utf-8"))


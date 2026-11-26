from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        return


_load_dotenv()


@dataclass(frozen=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    knowledge_base_dir: Path = PROJECT_ROOT / "data" / "knowledge_base"
    evaluation_path: Path = PROJECT_ROOT / "data" / "evaluation" / "questions.json"
    artifact_dir: Path = PROJECT_ROOT / "artifacts"
    llm_provider: str = os.getenv("LLM_PROVIDER", "offline").lower()
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    watsonx_api_key: str = os.getenv("WATSONX_API_KEY", "")
    watsonx_project_id: str = os.getenv("WATSONX_PROJECT_ID", "")
    watsonx_url: str = os.getenv("WATSONX_URL", "https://eu-de.ml.cloud.ibm.com")
    watsonx_model_id: str = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")
    embedding_backend: str = os.getenv("EMBEDDING_BACKEND", "lsa").lower()
    sentence_transformer_model: str = os.getenv(
        "SENTENCE_TRANSFORMER_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    top_k: int = int(os.getenv("TOP_K", "5"))
    min_confidence: float = float(os.getenv("MIN_CONFIDENCE", "0.34"))
    audit_log_path: Path = PROJECT_ROOT / os.getenv("AUDIT_LOG_PATH", "logs/audit.jsonl")


settings = Settings()


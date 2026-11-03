from fastapi.testclient import TestClient

from aegisrag.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["documents"] >= 15


def test_ask_endpoint_returns_citations():
    response = client.post(
        "/v1/ask",
        json={"question": "What transparency duties may apply to a chatbot?", "top_k": 5},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["citations"]
    assert body["trace_id"]


def test_assessment_endpoint_returns_risk_result():
    response = client.post(
        "/v1/assess",
        json={
            "system_name": "Hiring Ranker",
            "purpose": "Rank job applicants for recruiter review",
            "employment": True,
            "impacts_individuals": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["risk_level"] == "likely high-risk"


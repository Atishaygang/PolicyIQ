from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app


FAKE_ABSTENTION_RESULT = {
    "question": "Will HDFC ERGO approve my accident claim tomorrow?",

    "answer": (
        "I could not find sufficient information "
        "in the provided documents."
    ),

    "sources": [],

    "timings": {
        "hybrid_retrieval_ms": 50.0,
        "reranking_ms": 15000.0,
        "context_prompt_ms": 0.1,
        "llm_client_ms": 0.1,
        "llm_generation_ms": 700.0,
        "response_build_ms": 0.1,
        "total_ms": 15750.3
    }
}


def test_unanswerable_query_returns_200():

    with patch(
        "src.api.main.preload_policyiq"
    ):

        with patch(
            "src.rag.pipeline.ask_policyiq",
            return_value=FAKE_ABSTENTION_RESULT
        ):

            with TestClient(app) as client:

                response = client.post(
                    "/api/v1/query",
                    json={
                        "question":
                            "Will HDFC ERGO approve my accident claim tomorrow?"
                    }
                )

                assert response.status_code == 200

                data = response.json()

                assert data["answer"] == (
                    "I could not find sufficient information "
                    "in the provided documents."
                )
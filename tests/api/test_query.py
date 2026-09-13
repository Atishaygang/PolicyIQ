from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app


FAKE_RAG_RESULT = {
    "question": "What is the maximum No Claim Bonus?",

    "answer": "The maximum No Claim Bonus is 50%.",

    "sources": [
        {
            "document_id": "DOC009",
            "filename": "Motor Insurance_FAQ.pdf",
            "page": 2
        }
    ],

    "timings": {
        "hybrid_retrieval_ms": 50.0,
        "reranking_ms": 15000.0,
        "context_prompt_ms": 0.1,
        "llm_client_ms": 0.1,
        "llm_generation_ms": 900.0,
        "response_build_ms": 0.1,
        "total_ms": 15950.3
    }
}


def test_query_returns_valid_response():

    with patch(
        "src.api.main.preload_policyiq"
    ):

        with patch(
            "src.rag.pipeline.ask_policyiq",
            return_value=FAKE_RAG_RESULT
        ) as mock_rag:

            with TestClient(app) as client:

                response = client.post(
                    "/api/v1/query",
                    json={
                        "question":
                            "What is the maximum No Claim Bonus?"
                    }
                )

                assert response.status_code == 200

                data = response.json()

                assert data["question"] == (
                    "What is the maximum No Claim Bonus?"
                )

                assert data["answer"] == (
                    "The maximum No Claim Bonus is 50%."
                )

                assert len(
                    data["sources"]
                ) == 1

                assert (
                    data["sources"][0]["document_id"]
                    == "DOC009"
                )

                assert (
                    data["sources"][0]["page"]
                    == 2
                )

                assert (
                    data["timings"]["total_ms"]
                    == 15950.3
                )

                mock_rag.assert_called_once_with(
                    "What is the maximum No Claim Bonus?"
                )
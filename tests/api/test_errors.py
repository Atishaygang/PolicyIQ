from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app


def test_backend_failure_returns_controlled_500():

    with patch(
        "src.api.main.preload_policyiq"
    ):

        with patch(
            "src.rag.pipeline.ask_policyiq",
            side_effect=RuntimeError(
                "Simulated backend failure"
            )
        ):

            with TestClient(app) as client:

                response = client.post(
                    "/api/v1/query",
                    json={
                        "question":
                            "What is the maximum No Claim Bonus?"
                    }
                )

                assert response.status_code == 500

                data = response.json()

                assert data["detail"] == (
                    "PolicyIQ could not process the request "
                    "due to an internal service error."
                )
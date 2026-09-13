from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app


def test_query_rejects_too_short_question():

    with patch(
        "src.api.main.preload_policyiq"
    ):

        with TestClient(app) as client:

            response = client.post(
                "/api/v1/query",
                json={
                    "question": "Hi"
                }
            )

            assert response.status_code == 422


def test_query_rejects_missing_question():

    with patch(
        "src.api.main.preload_policyiq"
    ):

        with TestClient(app) as client:

            response = client.post(
                "/api/v1/query",
                json={}
            )

            assert response.status_code == 422
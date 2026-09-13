from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app


def test_ready_returns_true_after_startup():

    # Replace the real heavy PolicyIQ preload
    # with a fake function during this test.
    with patch(
        "src.api.main.preload_policyiq"
    ) as mock_preload:

        # Using TestClient as a context manager
        # runs FastAPI's lifespan startup/shutdown.
        with TestClient(app) as client:

            response = client.get("/ready")

            assert response.status_code == 200

            data = response.json()

            assert data["service"] == "PolicyIQ API"
            assert data["ready"] is True

            mock_preload.assert_called_once()


def test_ready_flag_resets_after_shutdown():

    with patch(
        "src.api.main.preload_policyiq"
    ):

        with TestClient(app) as client:

            assert app.state.ready is True

        # After leaving TestClient context,
        # FastAPI lifespan shutdown runs.
        assert app.state.ready is False
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from src.api.schemas import (
    PolicyQueryRequest,
    PolicyQueryResponse
)

from src.api.dependencies import preload_policyiq



# ==========================================
# Logging
# ==========================================

logger = logging.getLogger(__name__)


# ==========================================
# Application lifespan
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting PolicyIQ API...")

    app.state.ready = False

    try:

        preload_policyiq()

        app.state.ready = True

        print("PolicyIQ API ready.")

    except Exception:

        logger.exception(
            "PolicyIQ failed during startup."
        )

        raise


    yield


    app.state.ready = False

    print("Shutting down PolicyIQ API...")


# ==========================================
# FastAPI application
# ==========================================

app = FastAPI(
    title="PolicyIQ API",
    version="5.0",
    lifespan=lifespan
)


# ==========================================
# Health
# ==========================================

@app.get("/health")
def health_check():

    return {
        "service": "PolicyIQ API",
        "status": "running",
        "version": "5.0"
    }


# ==========================================
# Readiness
# ==========================================

@app.get("/ready")
def readiness_check():

    return {
        "service": "PolicyIQ API",
        "ready": app.state.ready
    }


# ==========================================
# Query endpoint
# ==========================================

@app.post(
    "/api/v1/query",
    response_model=PolicyQueryResponse
)
def ask_query(request: PolicyQueryRequest):

    from src.rag.pipeline import ask_policyiq

    if not app.state.ready:
        raise HTTPException(
            status_code=503,
            detail="PolicyIQ is not ready to process queries."
        )

    try:
        result = ask_policyiq(
            request.question
        )

        return {
            "question": result["question"],
            "answer": result["answer"],
            "sources": result["sources"],
            "timings": result["timings"]
        }

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "PolicyIQ query processing failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "PolicyIQ could not process the request "
                "due to an internal service error."
            )
        )
from pydantic import BaseModel, Field
from typing import Annotated


class PolicyQueryRequest(BaseModel):
    question: Annotated[
        str,
        Field(
            ...,
            min_length=3,
            max_length=1000,
            description="Question to ask PolicyIQ",
            examples=["What is the maximum No Claim Bonus?"]
        )
    ]

class SourceResponse(BaseModel):
    document_id: Annotated[
        str,
        Field(
            ...,
            description="Source document ID"
        )
    ]
    filename: Annotated[
        str,
        Field(
            ...,
            description="Source document filename"
        )
    ]
    page: Annotated[
        int,
        Field(
            ...,
            description="PDF page containing the evidence"
        )
    ]


class TimingResponse(BaseModel):
    hybrid_retrieval_ms: float
    reranking_ms: float
    context_prompt_ms: float
    llm_client_ms: float
    llm_generation_ms: float
    response_build_ms: float
    total_ms: float


class PolicyQueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceResponse]
    timings: TimingResponse

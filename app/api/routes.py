from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    QueryRequest,
    QueryResponse,
    FeedbackRequest,
)
from app.graph.workflow import workflow
from app.ingest.ingest import ingest_documents

router = APIRouter()


# ==================================================
# Helper Function
# ==================================================

def create_initial_state(question: str):

    return {
        "question": question,
        "rewritten_question": "",
        "documents": [],
        "relevant_documents": [],
        "answer": "",
        "retry_count": 0,
    }


# ==================================================
# Query Endpoint
# ==================================================

@router.post(
    "/query",
    response_model=QueryResponse
)
def query_documents(request: QueryRequest):

    try:

        result = workflow.invoke(
            create_initial_state(request.question)
        )

        return QueryResponse(
            answer=result["answer"]
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================================
# Document Ingestion Endpoint
# ==================================================

@router.post("/ingest")
def ingest():

    try:

        ingest_documents()

        return {
            "message": "Documents ingested successfully."
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================================
# List Documents Endpoint
# ==================================================

@router.get("/documents")
def list_documents():

    docs_path = Path("data/docs")

    if not docs_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Document directory not found."
        )

    documents = [
        file.name
        for file in docs_path.iterdir()
        if file.is_file()
    ]

    return {
        "documents": documents
    }


# ==================================================
# Feedback Endpoint
# ==================================================

@router.post("/feedback")
def submit_feedback(request: FeedbackRequest):

    return {
        "message": "Feedback received successfully.",
        "question": request.question,
        "feedback": request.feedback,
    }
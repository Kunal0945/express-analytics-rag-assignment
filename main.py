from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="Technical Documentation Assistant API",
    description="""
A Retrieval-Augmented Generation (RAG) API built using:

- FastAPI
- LangGraph
- ChromaDB
- HuggingFace Embeddings
- Groq LLM
""",
    version="1.0.0"
)


app.include_router(router)


@app.get(
    "/",
    tags=["Health Check"]
)
def root():

    return {
        "status": "running",
        "message": "Technical Documentation Assistant API"
    }
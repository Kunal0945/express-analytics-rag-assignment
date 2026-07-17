from typing import List, TypedDict
from langchain_core.documents import Document


class GraphState(TypedDict):
    question: str
    rewritten_question: str
    documents: List[Document]
    relevant_documents: List[Document]
    answer: str
    retry_count: int
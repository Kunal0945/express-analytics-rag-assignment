from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from opentelemetry import context
from unstructured import documents

from app.generation.generator import get_llm
from app.graph.state import GraphState
from app.retrieval.retriever import get_retriever
from app.utils.config import MAX_RETRIES


# ==================================================
# Global Objects
# ==================================================

LLM = get_llm()
RETRIEVER = get_retriever()
OUTPUT_PARSER = StrOutputParser()


# ==================================================
# Prompt Templates
# ==================================================

GRADING_PROMPT = ChatPromptTemplate.from_template(
    """
You are a document relevance evaluator.

Determine whether the document contains information that can help answer the user's question.

Question:
{question}

Document:
{document}

Rules:
- If the document contains complete or partial information that helps answer the question, reply YES.
- Otherwise reply NO.
- Return ONLY YES or NO.
"""
)


REWRITE_PROMPT = ChatPromptTemplate.from_template(
    """
You are an expert at rewriting search queries.

Rewrite the user's question to improve document retrieval.

Rules:
- Preserve the original meaning.
- Make the query more specific and searchable.
- Return ONLY the rewritten query.

Original Question:
{question}
"""
)


GENERATION_PROMPT = ChatPromptTemplate.from_template(
    """
You are a technical documentation assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Do not use outside knowledge.
- If the answer is not available in the context, respond exactly with:
"I couldn't find relevant information in the provided documents."

Question:
{question}

Context:
{context}
"""
)


# ==================================================
# Chains
# ==================================================

GRADING_CHAIN = (
    GRADING_PROMPT
    | LLM
    | OUTPUT_PARSER
)

REWRITE_CHAIN = (
    REWRITE_PROMPT
    | LLM
    | OUTPUT_PARSER
)

GENERATION_CHAIN = (
    GENERATION_PROMPT
    | LLM
    | OUTPUT_PARSER
)


# ==================================================
# Helper Functions
# ==================================================

def get_current_question(state: GraphState) -> str:
    return (
        state["rewritten_question"]
        if state.get("rewritten_question")
        else state["question"]
    )


# ==================================================
# Query Analysis Node
# ==================================================

def query_analysis_node(state: GraphState):

    return {
        "question": state["question"].strip(),
        "retry_count": state.get("retry_count", 0)
    }


# ==================================================
# Retrieval Node
# ==================================================

def retrieval_node(state: GraphState):

    question = get_current_question(state)

    documents = RETRIEVER.invoke(question)

    for i, doc in enumerate(documents):
        print(f"\n===== DOCUMENT {i+1} =====")
    print(doc.page_content[:500])

    print("\n========== RETRIEVAL ==========")
    print("Question:", question)
    print("Retrieved:", len(documents), "documents")

    for doc in documents:
        print(doc.metadata)

    return {
        "documents": documents
    }
# ==================================================
# Document Grading Node
# ==================================================

def document_grading_node(state: GraphState):

    question = get_current_question(state)

    relevant_documents = []

    print("\n========== GRADING ==========")

    for document in state["documents"]:

        result = GRADING_CHAIN.invoke(
            {
                "question": question,
                "document": document.page_content
            }
        )

        print(document.metadata)
        print("LLM Output:", repr(result))

        if "YES" in result.upper():
            relevant_documents.append(document)

    print("Relevant Documents:", len(relevant_documents))

    return {
        "relevant_documents": relevant_documents
    }


# ==================================================
# Rewrite Query Node
# ==================================================

def rewrite_query_node(state: GraphState):

    rewritten_question = REWRITE_CHAIN.invoke(
        {
            "question": state["question"]
        }
    )

    return {
        "rewritten_question": rewritten_question.strip(),
        "retry_count": state.get("retry_count", 0) + 1
    }


# ==================================================
# Generation Node
# ==================================================

def generation_node(state: GraphState):

    question = get_current_question(state)

    context = "\n\n".join(
        document.page_content
        for document in state["relevant_documents"]
    )

    print("\n========== GENERATION ==========")
    print("Context Length:", len(context))

    answer = GENERATION_CHAIN.invoke(
        {
            "question": question,
            "context": context
        }
    )

    print("\n========== ANSWER ==========")
    print(repr(answer))

    print("\n========== CONTEXT ==========")
    print(context)

    return {
        "answer": answer
    }

# ==================================================
# Conditional Router
# ==================================================

def route_after_grading(state: GraphState):

    if state["relevant_documents"]:
        return "generate"

    if state.get("retry_count", 0) < MAX_RETRIES:
        return "rewrite"

    return "generate"
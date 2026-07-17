from langgraph.graph import StateGraph, START, END

from app.graph.state import GraphState
from app.graph.nodes import (
    query_analysis_node,
    retrieval_node,
    document_grading_node,
    rewrite_query_node,
    generation_node,
    route_after_grading,
)


# ==================================================
# Build Workflow
# ==================================================

builder = StateGraph(GraphState)


# ==================================================
# Add Nodes
# ==================================================

builder.add_node("query_analysis", query_analysis_node)
builder.add_node("retrieval", retrieval_node)
builder.add_node("document_grading", document_grading_node)
builder.add_node("rewrite", rewrite_query_node)
builder.add_node("generation", generation_node)


# ==================================================
# Add Edges
# ==================================================

builder.add_edge(START, "query_analysis")

builder.add_edge("query_analysis", "retrieval")

builder.add_edge("retrieval", "document_grading")

builder.add_conditional_edges(
    "document_grading",
    route_after_grading,
    {
        "generate": "generation",
        "rewrite": "rewrite",
    },
)

builder.add_edge("rewrite", "retrieval")

builder.add_edge("generation", END)


# ==================================================
# Compile Workflow
# ==================================================

workflow = builder.compile()
"""
Graph Builder — constructs, defines edges, and compiles the LangGraph StateGraph.
"""
from langgraph.graph import StateGraph, START, END
from graphs.state import AnalysisState
from graphs.registry import NODE_REGISTRY


def build_analysis_graph() -> StateGraph:
    """
    Construct, link, and compile the orchestration StateGraph.

    Currently maps:
    START ──> Repository Intake ──> Parser ──> Knowledge Graph ──>
    Planner (placeholder) ──> Executor (placeholder) ──>
    Reflection (placeholder) ──> Report (placeholder) ──> END
    """
    # 1. Initialize StateGraph with the schema
    workflow = StateGraph(AnalysisState)

    # 2. Add all nodes from registry
    for node_name, node_func in NODE_REGISTRY.items():
        workflow.add_node(node_name, node_func)

    # 3. Define execution flow edges
    workflow.add_edge(START, "repository_intake")
    workflow.add_edge("repository_intake", "repository_parser")
    workflow.add_edge("repository_parser", "knowledge_graph")

    # Connect future placeholder nodes in sequence
    workflow.add_edge("knowledge_graph", "planner")
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "reflection")
    workflow.add_edge("reflection", "report_generator")
    workflow.add_edge("report_generator", END)

    # 4. Compile the graph
    return workflow.compile()

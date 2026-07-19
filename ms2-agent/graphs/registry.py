"""
Node Registry — maps string node identifiers to Python callable implementations
for modular workflow mapping.
"""
from typing import Callable, Dict
from graphs.nodes import (
    RepositoryIntakeNode,
    RepositoryParserNode,
    KnowledgeGraphNode,
    PlannerNode,
    ExecutionNode,
    ReflectionNode,
    ReportNode,
)

# Registry mapping node names to callable functions
NODE_REGISTRY: Dict[str, Callable] = {
    "repository_intake": RepositoryIntakeNode,
    "repository_parser": RepositoryParserNode,
    "knowledge_graph":   KnowledgeGraphNode,
    "planner":           PlannerNode,
    "executor":          ExecutionNode,
    "reflection":        ReflectionNode,
    "report_generator":  ReportNode,
}

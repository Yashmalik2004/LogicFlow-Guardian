"""
Graph Relationship Queries — Cypher MERGE statements to upsert relationships.

Group relationships by (from_label, to_label, rel_type) and execute
targeted batch queries for maximum performance and index utilization.
"""
from collections import defaultdict
from neo4j import Session

BATCH_SIZE = 500

_ID_MAP = {
    "Repository": "repo_id",
    "Directory": "dir_id",
    "File": "file_id",
    "Class": "class_id",
    "Function": "func_id",
    "Method": "method_id",
    "Route": "route_id",
    "Middleware": "middleware_id",
    "Import": "import_id",
    "Export": "export_id",
}


def _get_label_from_id(entity_id: str) -> str:
    parts = entity_id.split("::")
    if len(parts) >= 2:
        return parts[1]
    return "Node"


def _chunks(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def upsert_relationships(session: Session, relationships: list[dict], analysis_id: int) -> None:
    """Group and execute batched relationship insertions."""
    if not relationships:
        return

    # Group by (from_label, to_label, type)
    groups = defaultdict(list)
    for rel in relationships:
        from_label = _get_label_from_id(rel["from_id"])
        to_label = _get_label_from_id(rel["to_id"])
        rel_type = rel["type"]
        groups[(from_label, to_label, rel_type)].append(rel)

    for (from_label, to_label, rel_type), rel_list in groups.items():
        from_key = _ID_MAP.get(from_label, "id")
        to_key = _ID_MAP.get(to_label, "id")

        # Special handling for EXTENDS to unresolved external base classes
        if rel_type == "EXTENDS" and from_label == "Class" and to_label == "Class":
            for batch in _chunks(rel_list, BATCH_SIZE):
                session.run(
                    """
                    UNWIND $rows AS row
                    MATCH (a:Class {class_id: row.from_id})
                    MERGE (b:Class {class_id: row.to_id})
                    ON CREATE SET b.name = row.props.base_name,
                                  b.is_unresolved = true,
                                  b.analysis_id = $analysis_id
                    MERGE (a)-[r:EXTENDS]->(b)
                    SET r += row.props
                    """,
                    rows=batch,
                    analysis_id=analysis_id,
                )
            continue

        # General case: Match both existing nodes and merge the relationship
        cypher = f"""
        UNWIND $rows AS row
        MATCH (a:{from_label} {{{from_key}: row.from_id}})
        MATCH (b:{to_label} {{{to_key}: row.to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += row.props
        """

        for batch in _chunks(rel_list, BATCH_SIZE):
            session.run(cypher, rows=batch)

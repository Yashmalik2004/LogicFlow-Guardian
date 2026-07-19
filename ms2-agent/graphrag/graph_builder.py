"""
Graph Builder Service — Orchestrates the schema initialization, normalization,
node and relationship ingestion, and validation of the Neo4j knowledge graph.
"""
from neo4j import GraphDatabase, Driver
from app.config.neo4j import get_driver
from parser.engine import IntermediateRepresentation

from app.config.env import env

from graphrag.graph_schema import CONSTRAINT_QUERIES, INDEX_QUERIES
from graphrag.normalizer import IRNormalizer, NormalizedGraph
from graphrag.graph_nodes import (
    upsert_repository,
    upsert_directories,
    upsert_files,
    upsert_classes,
    upsert_functions,
    upsert_methods,
    upsert_routes,
    upsert_middleware,
    upsert_imports,
    upsert_exports,
)
from graphrag.graph_relationships import upsert_relationships


class GraphBuilder:
    """
    Orchestrates ingestion of Parser Intermediate Representation (IR)
    into a Neo4j knowledge graph.
    """

    def __init__(self, driver: Driver | None = None) -> None:
        self.driver = driver or get_driver()

    def build_graph(self, ir: IntermediateRepresentation, repo_name: str) -> dict:
        """
        Normalize the parser IR, push schema constraints, ingest all nodes
        and relationships, and validate the resulting graph database structure.
        """
        print(f"[INFO] [GraphBuilder] Starting graph ingestion for analysis_id={ir.analysis_id}")

        # 1. Initialize constraints & indexes
        self.initialize_schema()

        # 2. Normalize parser IR
        normalizer = IRNormalizer(analysis_id=ir.analysis_id, repo_name=repo_name)
        ng: NormalizedGraph = normalizer.normalize(ir)

        # 3. Persist to Neo4j
        with self.driver.session(database=env.NEO4J_DATABASE) as session:
            # Nodes
            print("[INFO] [GraphBuilder] Ingesting nodes...")
            session.execute_write(upsert_repository, ng.repository)
            session.execute_write(upsert_directories, ng.directories)
            session.execute_write(upsert_files, ng.files)
            session.execute_write(upsert_classes, ng.classes)
            session.execute_write(upsert_functions, ng.functions)
            session.execute_write(upsert_methods, ng.methods)
            session.execute_write(upsert_routes, ng.routes)
            session.execute_write(upsert_middleware, ng.middleware)
            session.execute_write(upsert_imports, ng.imports)
            session.execute_write(upsert_exports, ng.exports)

            # Relationships
            print("[INFO] [GraphBuilder] Ingesting relationships...")
            session.execute_write(upsert_relationships, ng.relationships, ir.analysis_id)

            # 4. Validate graph and compile counts
            print("[INFO] [GraphBuilder] Validating graph ingestion...")
            validation_report = self.validate_graph(session, ir.analysis_id)

        print(
            f"[INFO] [GraphBuilder] Ingestion complete for analysis_id={ir.analysis_id}. "
            f"Nodes={validation_report['total_nodes']} Rel={validation_report['total_relationships']}"
        )
        return validation_report

    def initialize_schema(self) -> None:
        """Create Neo4j unique constraints and indexes if they do not exist."""
        print("[INFO] [GraphBuilder] Ensuring Neo4j schema indexes and constraints...")
        with self.driver.session(database=env.NEO4J_DATABASE) as session:
            for q in CONSTRAINT_QUERIES:
                try:
                    session.run(q)
                except Exception as exc:
                    print(f"[WARN] [GraphBuilder] Failed to create constraint: {exc}")

            for q in INDEX_QUERIES:
                try:
                    session.run(q)
                except Exception as exc:
                    print(f"[WARN] [GraphBuilder] Failed to create index: {exc}")

    def validate_graph(self, session, analysis_id: int) -> dict:
        """
        Verify that nodes and relationships were successfully written.
        Returns a metrics dictionary.
        """
        # Count nodes of all types for this analysis
        node_counts = {}
        labels = [
            "Repository", "Directory", "File", "Class",
            "Function", "Method", "Route", "Middleware",
            "Import", "Export"
        ]

        total_nodes = 0
        for label in labels:
            res = session.run(
                f"MATCH (n:{label} {{analysis_id: $analysis_id}}) RETURN count(n) AS cnt",
                analysis_id=analysis_id,
            )
            count = res.single()["cnt"]
            node_counts[label] = count
            total_nodes += count

        # Count total relationships
        res_rel = session.run(
            """
            MATCH (n {analysis_id: $analysis_id})-[r]->()
            RETURN count(r) AS cnt
            """,
            analysis_id=analysis_id,
        )
        total_relationships = res_rel.single()["cnt"]

        # Basic integrity check: make sure the Repository node exists
        repo_exists = node_counts.get("Repository", 0) > 0

        return {
            "success": repo_exists,
            "analysis_id": analysis_id,
            "total_nodes": total_nodes,
            "total_relationships": total_relationships,
            "node_breakdown": node_counts,
        }

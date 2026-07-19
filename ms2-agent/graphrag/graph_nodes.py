"""
Graph Node Queries — Cypher MERGE statements to upsert nodes.

Each function receives a Neo4j session and a list of node dicts
(produced by the normalizer) and writes them in batched UNWIND calls
for efficiency.

Batch size: 500 nodes per transaction.
"""
from neo4j import Session

BATCH_SIZE = 500


def _chunks(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------

def upsert_repository(session: Session, repo: dict) -> None:
    """Create or update the root Repository node."""
    session.run(
        """
        MERGE (r:Repository {repo_id: $repo_id})
        SET r.analysis_id   = $analysis_id,
            r.name          = $name,
            r.path          = $path,
            r.total_files   = $total_files,
            r.supported_files = $supported_files
        """,
        **repo,
    )


# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------

def upsert_directories(session: Session, dirs: list[dict]) -> None:
    for batch in _chunks(dirs, BATCH_SIZE):
        session.run(
            """
            UNWIND $rows AS row
            MERGE (d:Directory {dir_id: row.dir_id})
            SET d.relative_path = row.relative_path,
                d.name          = row.name,
                d.analysis_id   = row.analysis_id
            """,
            rows=batch,
        )


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------

def upsert_files(session: Session, files: list[dict]) -> None:
    for batch in _chunks(files, BATCH_SIZE):
        session.run(
            """
            UNWIND $rows AS row
            MERGE (f:File {file_id: row.file_id})
            SET f.relative_path = row.relative_path,
                f.name          = row.name,
                f.file_type     = row.file_type,
                f.language      = row.language,
                f.size_bytes    = row.size_bytes,
                f.analysis_id   = row.analysis_id
            """,
            rows=batch,
        )


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

def upsert_classes(session: Session, classes: list[dict]) -> None:
    """
    Upsert Class nodes.  For classes that have extra labels (Controller,
    Service, Model) we run a separate APOC-free label-addition query using
    conditional SET labels trick.  To keep this dependency-free, we just
    set a `roles` property and handle label branching via sub-queries.
    """
    for batch in _chunks(classes, BATCH_SIZE):
        session.run(
            """
            UNWIND $rows AS row
            MERGE (c:Class {class_id: row.class_id})
            SET c.name         = row.name,
                c.bases        = row.bases,
                c.extends      = row.extends,
                c.decorators   = row.decorators,
                c.roles        = row.extra_labels,
                c.start_line   = row.start_line,
                c.end_line     = row.end_line,
                c.analysis_id  = row.analysis_id,
                c.file_id      = row.file_id
            """,
            rows=batch,
        )
    # Apply Controller / Service / Model labels as additional labels
    _apply_role_labels(session, classes)


def _apply_role_labels(session: Session, classes: list[dict]) -> None:
    """Add Controller / Service / Model secondary labels where applicable."""
    for role in ("Controller", "Service", "Model"):
        role_classes = [
            {"class_id": c["class_id"]}
            for c in classes
            if role in c.get("extra_labels", [])
        ]
        if not role_classes:
            continue
        # We dynamically use inline label via CALL {} — compatible with Neo4j 4.4+
        # For older versions, separate MERGE calls per label.
        for batch in _chunks(role_classes, BATCH_SIZE):
            cypher = f"""
            UNWIND $rows AS row
            MATCH (c:Class {{class_id: row.class_id}})
            SET c:{role}
            """
            session.run(cypher, rows=batch)


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def upsert_functions(session: Session, functions: list[dict]) -> None:
    for batch in _chunks(functions, BATCH_SIZE):
        session.run(
            """
            UNWIND $rows AS row
            MERGE (f:Function {func_id: row.func_id})
            SET f.name       = row.name,
                f.params     = row.params,
                f.type       = row.type,
                f.is_async   = row.is_async,
                f.start_line = row.start_line,
                f.end_line   = row.end_line,
                f.analysis_id = row.analysis_id,
                f.file_id    = row.file_id
            """,
            rows=batch,
        )


# ---------------------------------------------------------------------------
# Methods
# ---------------------------------------------------------------------------

def upsert_methods(session: Session, methods: list[dict]) -> None:
    for batch in _chunks(methods, BATCH_SIZE):
        session.run(
            """
            UNWIND $rows AS row
            MERGE (m:Method {method_id: row.method_id})
            SET m.name       = row.name,
                m.params     = row.params,
                m.decorators = row.decorators,
                m.is_async   = row.is_async,
                m.start_line = row.start_line,
                m.end_line   = row.end_line,
                m.analysis_id = row.analysis_id,
                m.class_id   = row.class_id
            """,
            rows=batch,
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

def upsert_routes(session: Session, routes: list[dict]) -> None:
    for batch in _chunks(routes, BATCH_SIZE):
        session.run(
            """
            UNWIND $rows AS row
            MERGE (r:Route {route_id: row.route_id})
            SET r.path        = row.path,
                r.http_method = row.http_method,
                r.handler     = row.handler,
                r.line        = row.line,
                r.analysis_id = row.analysis_id,
                r.file_id     = row.file_id
            """,
            rows=batch,
        )


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

def upsert_middleware(session: Session, middleware: list[dict]) -> None:
    for batch in _chunks(middleware, BATCH_SIZE):
        session.run(
            """
            UNWIND $rows AS row
            MERGE (mw:Middleware {middleware_id: row.middleware_id})
            SET mw.object     = row.object,
                mw.line       = row.line,
                mw.analysis_id = row.analysis_id,
                mw.file_id    = row.file_id
            """,
            rows=batch,
        )


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

def upsert_imports(session: Session, imports: list[dict]) -> None:
    for batch in _chunks(imports, BATCH_SIZE):
        session.run(
            """
            UNWIND $rows AS row
            MERGE (i:Import {import_id: row.import_id})
            SET i.type       = row.type,
                i.module     = row.module,
                i.name       = row.name,
                i.alias      = row.alias,
                i.line       = row.line,
                i.analysis_id = row.analysis_id
            """,
            rows=batch,
        )


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

def upsert_exports(session: Session, exports: list[dict]) -> None:
    for batch in _chunks(exports, BATCH_SIZE):
        session.run(
            """
            UNWIND $rows AS row
            MERGE (e:Export {export_id: row.export_id})
            SET e.type       = row.type,
                e.name       = row.name,
                e.line       = row.line,
                e.analysis_id = row.analysis_id
            """,
            rows=batch,
        )

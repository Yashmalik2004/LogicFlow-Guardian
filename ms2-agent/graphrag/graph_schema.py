"""
Graph Schema — defines all node labels, relationship types, and Neo4j
constraint/index creation queries for the LogicFlow Guardian knowledge graph.

Node Labels
-----------
Repository  : Root node for one analysis run.
Directory   : A folder inside the repository.
File        : A source file.
Class       : A class definition.
Function    : A standalone function.
Method      : A function defined inside a class.
Route       : An HTTP route/endpoint.
Middleware  : Express/FastAPI middleware.
Controller  : Class identified as a controller (name or decorator).
Service     : Class identified as a service (name or decorator).
Model       : Class identified as a model/schema (name or decorator).
Import      : An import statement node.
Export      : An export statement node.

Relationship Types
------------------
CONTAINS      : Repository→Directory, Directory→File, File→Class/Function
IMPORTS       : File→Import
EXPORTS       : File→Export
DECLARES      : File→Class, File→Function, Class→Method
EXTENDS       : Class→Class
IMPLEMENTS    : Class→Interface (future)
USES          : Class/Function→Import (logical dependency)
CALLS         : Function/Method→Function/Method (future, requires call analysis)
HAS_ROUTE     : File/Class→Route
PROTECTED_BY  : Route→Middleware
OWNS          : Repository→File (direct ownership, shortcut edge)
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------

class NodeLabel:
    REPOSITORY  = "Repository"
    DIRECTORY   = "Directory"
    FILE        = "File"
    CLASS       = "Class"
    FUNCTION    = "Function"
    METHOD      = "Method"
    ROUTE       = "Route"
    MIDDLEWARE  = "Middleware"
    CONTROLLER  = "Controller"
    SERVICE     = "Service"
    MODEL       = "Model"
    IMPORT      = "Import"
    EXPORT      = "Export"


class RelType:
    CONTAINS     = "CONTAINS"
    IMPORTS      = "IMPORTS"
    EXPORTS      = "EXPORTS"
    DECLARES     = "DECLARES"
    EXTENDS      = "EXTENDS"
    IMPLEMENTS   = "IMPLEMENTS"
    USES         = "USES"
    CALLS        = "CALLS"
    HAS_ROUTE    = "HAS_ROUTE"
    PROTECTED_BY = "PROTECTED_BY"
    OWNS         = "OWNS"


# ---------------------------------------------------------------------------
# Constraint / index queries
# Run once on startup to ensure uniqueness and fast lookups.
# ---------------------------------------------------------------------------

CONSTRAINT_QUERIES: list[str] = [
    # Repository
    "CREATE CONSTRAINT repo_id IF NOT EXISTS "
    "FOR (n:Repository) REQUIRE n.repo_id IS UNIQUE",

    # File — unique per repo
    "CREATE CONSTRAINT file_id IF NOT EXISTS "
    "FOR (n:File) REQUIRE n.file_id IS UNIQUE",

    # Directory
    "CREATE CONSTRAINT dir_id IF NOT EXISTS "
    "FOR (n:Directory) REQUIRE n.dir_id IS UNIQUE",

    # Class
    "CREATE CONSTRAINT class_id IF NOT EXISTS "
    "FOR (n:Class) REQUIRE n.class_id IS UNIQUE",

    # Function
    "CREATE CONSTRAINT func_id IF NOT EXISTS "
    "FOR (n:Function) REQUIRE n.func_id IS UNIQUE",

    # Method
    "CREATE CONSTRAINT method_id IF NOT EXISTS "
    "FOR (n:Method) REQUIRE n.method_id IS UNIQUE",

    # Route
    "CREATE CONSTRAINT route_id IF NOT EXISTS "
    "FOR (n:Route) REQUIRE n.route_id IS UNIQUE",
]

INDEX_QUERIES: list[str] = [
    "CREATE INDEX file_path_idx IF NOT EXISTS FOR (n:File) ON (n.relative_path)",
    "CREATE INDEX class_name_idx IF NOT EXISTS FOR (n:Class) ON (n.name)",
    "CREATE INDEX func_name_idx IF NOT EXISTS FOR (n:Function) ON (n.name)",
    "CREATE INDEX route_path_idx IF NOT EXISTS FOR (n:Route) ON (n.path)",
]

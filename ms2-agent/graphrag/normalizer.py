"""
IR Normalizer — converts raw Parser IR into flat, graph-ready entity lists.

The normalizer is a pure transformation layer: it takes the IR dataclass
produced by RepositoryParserEngine and emits dicts with stable IDs that
the graph builder can feed directly into Neo4j MERGE queries.

Stable ID scheme:  f"{analysis_id}::{label}::{key}"
This prevents cross-analysis collisions when multiple analyses share a
Neo4j database.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from parser.engine import IntermediateRepresentation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """Strip unsafe chars; used inside ID construction."""
    return re.sub(r"[^\w./:-]", "_", text)


def _make_id(analysis_id: int, label: str, key: str) -> str:
    return f"{analysis_id}::{label}::{_slugify(key)}"


# ---------------------------------------------------------------------------
# Heuristic role classification
# Names/decorators that strongly suggest Controller / Service / Model role.
# ---------------------------------------------------------------------------

_CONTROLLER_PATTERNS = re.compile(
    r"controller|handler|resource|endpoint|view|viewset|router",
    re.IGNORECASE,
)
_SERVICE_PATTERNS = re.compile(
    r"service|manager|provider|repository|facade|usecase|interactor",
    re.IGNORECASE,
)
_MODEL_PATTERNS = re.compile(
    r"model|schema|entity|dto|record|serializer|dataclass",
    re.IGNORECASE,
)
_MIDDLEWARE_DECORATORS = {
    "app.use", "router.use", "middleware", "use_middleware",
}


def _classify_class(name: str, decorators: list[dict]) -> list[str]:
    """Return a list of additional Neo4j labels for the class."""
    extra: list[str] = []
    name_lower = name.lower()
    dec_names = {d.get("name", "").lower() for d in decorators}

    if _CONTROLLER_PATTERNS.search(name_lower) or any(
        "controller" in d for d in dec_names
    ):
        extra.append("Controller")
    if _SERVICE_PATTERNS.search(name_lower) or any(
        "injectable" in d or "service" in d for d in dec_names
    ):
        extra.append("Service")
    if _MODEL_PATTERNS.search(name_lower):
        extra.append("Model")
    return extra


# ---------------------------------------------------------------------------
# Normalized entity containers
# ---------------------------------------------------------------------------

@dataclass
class NormalizedGraph:
    analysis_id: int
    repository_path: str
    repo_name: str

    # Nodes
    repository: dict = field(default_factory=dict)
    directories: list[dict] = field(default_factory=list)
    files: list[dict] = field(default_factory=list)
    classes: list[dict] = field(default_factory=list)
    functions: list[dict] = field(default_factory=list)
    methods: list[dict] = field(default_factory=list)
    routes: list[dict] = field(default_factory=list)
    middleware: list[dict] = field(default_factory=list)
    imports: list[dict] = field(default_factory=list)
    exports: list[dict] = field(default_factory=list)

    # Relationships (each is a dict with keys: from_id, to_id, type, props)
    relationships: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Normalizer
# ---------------------------------------------------------------------------

class IRNormalizer:
    """Converts an IntermediateRepresentation into a NormalizedGraph."""

    def __init__(self, analysis_id: int, repo_name: str) -> None:
        self.analysis_id = analysis_id
        self.repo_name = repo_name
        self._aid = analysis_id

    def normalize(self, ir: IntermediateRepresentation) -> NormalizedGraph:
        ng = NormalizedGraph(
            analysis_id=self._aid,
            repository_path=ir.repository_path,
            repo_name=self.repo_name,
        )

        # ----- Repository node -----
        repo_id = _make_id(self._aid, "Repository", self.repo_name)
        ng.repository = {
            "repo_id": repo_id,
            "analysis_id": self._aid,
            "name": self.repo_name,
            "path": ir.repository_path,
            "total_files": ir.total_files,
            "supported_files": ir.supported_files,
        }

        # ----- Directory nodes -----
        dir_id_map: dict[str, str] = {}
        for folder in ir.folders:
            d_id = _make_id(self._aid, "Directory", folder.relative_path)
            dir_id_map[folder.relative_path] = d_id
            ng.directories.append({
                "dir_id": d_id,
                "relative_path": folder.relative_path,
                "name": os.path.basename(folder.relative_path) or folder.relative_path,
                "analysis_id": self._aid,
            })
            # Relationship: parent dir CONTAINS this dir OR repo CONTAINS top-level dir
            parent = os.path.dirname(folder.relative_path)
            if parent and parent != "." and parent in dir_id_map:
                ng.relationships.append({
                    "from_id": dir_id_map[parent],
                    "to_id": d_id,
                    "type": "CONTAINS",
                    "props": {},
                })
            else:
                ng.relationships.append({
                    "from_id": repo_id,
                    "to_id": d_id,
                    "type": "CONTAINS",
                    "props": {},
                })

        # ----- File nodes -----
        file_id_map: dict[str, str] = {}
        for f in ir.files:
            f_id = _make_id(self._aid, "File", f.relative_path)
            file_id_map[f.relative_path] = f_id
            ng.files.append({
                "file_id": f_id,
                "relative_path": f.relative_path,
                "name": os.path.basename(f.relative_path),
                "file_type": f.file_type,
                "language": f.language,
                "size_bytes": f.size_bytes,
                "analysis_id": self._aid,
            })
            # OWNS: Repo → File (shortcut)
            ng.relationships.append({
                "from_id": repo_id,
                "to_id": f_id,
                "type": "OWNS",
                "props": {},
            })
            # CONTAINS: parent dir → file
            parent_dir = os.path.dirname(f.relative_path)
            if parent_dir and parent_dir in dir_id_map:
                ng.relationships.append({
                    "from_id": dir_id_map[parent_dir],
                    "to_id": f_id,
                    "type": "CONTAINS",
                    "props": {},
                })

        # ----- Parsed symbols -----
        for parsed in ir.parsed:
            f_id = file_id_map.get(parsed.relative_path)
            if not f_id:
                continue
            syms = parsed.symbols
            self._handle_imports(syms, f_id, ng)
            self._handle_exports(syms, f_id, ng)
            self._handle_classes(syms, f_id, parsed.relative_path, ng)
            self._handle_functions(syms, f_id, parsed.relative_path, ng)
            self._handle_routes(syms, f_id, parsed.relative_path, ng)
            self._handle_middleware(syms, f_id, parsed.relative_path, ng)

        return ng

    # -----------------------------------------------------------------------
    # Symbol handlers
    # -----------------------------------------------------------------------

    def _handle_imports(self, syms: dict, f_id: str, ng: NormalizedGraph) -> None:
        for i, imp in enumerate(syms.get("imports", [])):
            module = imp.get("module", "")
            imp_id = _make_id(self._aid, "Import", f"{f_id}::imp::{i}::{module}")
            ng.imports.append({
                "import_id": imp_id,
                "type": imp.get("type", "import"),
                "module": module,
                "name": imp.get("name") or imp.get("specifier") or imp.get("binding"),
                "alias": imp.get("alias"),
                "line": imp.get("line"),
                "analysis_id": self._aid,
            })
            ng.relationships.append({
                "from_id": f_id,
                "to_id": imp_id,
                "type": "IMPORTS",
                "props": {"line": imp.get("line")},
            })

    def _handle_exports(self, syms: dict, f_id: str, ng: NormalizedGraph) -> None:
        for i, exp in enumerate(syms.get("exports", [])):
            exp_id = _make_id(self._aid, "Export", f"{f_id}::exp::{i}::{exp.get('name','')}")
            ng.exports.append({
                "export_id": exp_id,
                "type": exp.get("type", "named"),
                "name": exp.get("name"),
                "line": exp.get("line"),
                "analysis_id": self._aid,
            })
            ng.relationships.append({
                "from_id": f_id,
                "to_id": exp_id,
                "type": "EXPORTS",
                "props": {},
            })

    def _handle_classes(
        self, syms: dict, f_id: str, rel_path: str, ng: NormalizedGraph
    ) -> None:
        for cls in syms.get("classes", []):
            name = cls.get("name", "")
            c_id = _make_id(self._aid, "Class", f"{rel_path}::{name}")
            decorators = cls.get("decorators", [])
            extra_labels = _classify_class(name, decorators)

            ng.classes.append({
                "class_id": c_id,
                "name": name,
                "bases": cls.get("bases", []),
                "extends": cls.get("extends"),
                "decorators": [d.get("name") for d in decorators],
                "extra_labels": extra_labels,
                "start_line": cls.get("start_line") or cls.get("line"),
                "end_line": cls.get("end_line"),
                "language": syms.get("_language"),
                "analysis_id": self._aid,
                "file_id": f_id,
            })
            # File DECLARES class
            ng.relationships.append({
                "from_id": f_id,
                "to_id": c_id,
                "type": "DECLARES",
                "props": {},
            })
            # EXTENDS relationship
            if cls.get("extends") or cls.get("bases"):
                for base in (cls.get("bases") or [cls.get("extends")] if cls.get("extends") else []):
                    if base:
                        base_id = _make_id(self._aid, "Class", f"__unresolved__::{base}")
                        ng.relationships.append({
                            "from_id": c_id,
                            "to_id": base_id,
                            "type": "EXTENDS",
                            "props": {"base_name": base},
                        })

            # Methods
            for mth in cls.get("methods", []):
                m_name = mth.get("name", "")
                m_id = _make_id(self._aid, "Method", f"{rel_path}::{name}::{m_name}")
                ng.methods.append({
                    "method_id": m_id,
                    "name": m_name,
                    "params": mth.get("params", []),
                    "decorators": [d.get("name") for d in mth.get("decorators", [])],
                    "is_async": mth.get("is_async", False),
                    "start_line": mth.get("start_line"),
                    "end_line": mth.get("end_line"),
                    "analysis_id": self._aid,
                    "class_id": c_id,
                })
                ng.relationships.append({
                    "from_id": c_id,
                    "to_id": m_id,
                    "type": "DECLARES",
                    "props": {},
                })

    def _handle_functions(
        self, syms: dict, f_id: str, rel_path: str, ng: NormalizedGraph
    ) -> None:
        for func in syms.get("functions", []):
            name = func.get("name", "")
            fn_id = _make_id(self._aid, "Function", f"{rel_path}::{name}::{func.get('line',0)}")
            ng.functions.append({
                "func_id": fn_id,
                "name": name,
                "params": func.get("params", []),
                "type": func.get("type", "function"),
                "is_async": func.get("is_async", False),
                "start_line": func.get("start_line") or func.get("line"),
                "end_line": func.get("end_line"),
                "analysis_id": self._aid,
                "file_id": f_id,
            })
            ng.relationships.append({
                "from_id": f_id,
                "to_id": fn_id,
                "type": "DECLARES",
                "props": {},
            })

    def _handle_routes(
        self, syms: dict, f_id: str, rel_path: str, ng: NormalizedGraph
    ) -> None:
        for i, route in enumerate(syms.get("routes", [])):
            path = route.get("path") or ""
            method = route.get("method") or route.get("decorator", "")
            r_id = _make_id(self._aid, "Route", f"{rel_path}::route::{i}::{method}::{path}")
            ng.routes.append({
                "route_id": r_id,
                "path": path,
                "http_method": method,
                "handler": route.get("handler"),
                "line": route.get("line"),
                "analysis_id": self._aid,
                "file_id": f_id,
            })
            ng.relationships.append({
                "from_id": f_id,
                "to_id": r_id,
                "type": "HAS_ROUTE",
                "props": {},
            })

    def _handle_middleware(
        self, syms: dict, f_id: str, rel_path: str, ng: NormalizedGraph
    ) -> None:
        for i, mw in enumerate(syms.get("middleware", [])):
            mw_id = _make_id(self._aid, "Middleware", f"{rel_path}::mw::{i}::{mw.get('line',0)}")
            ng.middleware.append({
                "middleware_id": mw_id,
                "object": mw.get("object"),
                "line": mw.get("line"),
                "analysis_id": self._aid,
                "file_id": f_id,
            })
            ng.relationships.append({
                "from_id": f_id,
                "to_id": mw_id,
                "type": "CONTAINS",
                "props": {},
            })

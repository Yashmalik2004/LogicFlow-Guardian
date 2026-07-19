"""
Repository Parser Engine — scans, filters, and dispatches source files.

Pipeline:
    1. Walk the repository directory tree.
    2. Skip ignored directories (node_modules, .git, dist, build,
       coverage, __pycache__) and binary file extensions.
    3. Build a repository inventory (folders + files with type/language).
    4. For each supported source file, dispatch to the correct language parser.
    5. Accumulate results into a single normalized Intermediate Representation (IR).

Adding a new language parser:
    - Create a new module under parser/languages/ that subclasses BaseParser.
    - Register its file extensions in the EXTENSION_MAP below.
    - No other changes are needed.
"""
import os
import json
from dataclasses import dataclass, field, asdict
from typing import Callable

from parser.languages.python import PythonParser
from parser.languages.javascript import JavaScriptTypeScriptParser
from parser.base import BaseParser


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

#: Directories to skip during recursive scan
IGNORED_DIRS: frozenset[str] = frozenset({
    "node_modules", ".git", "dist", "build", "coverage",
    "__pycache__", ".venv", "venv", "env", ".tox", ".eggs",
    ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "vendor", "third_party",
})

#: File extensions to skip (binaries, compiled assets, etc.)
IGNORED_EXTENSIONS: frozenset[str] = frozenset({
    ".pyc", ".pyd", ".so", ".dll", ".dylib", ".exe", ".bin",
    ".class", ".jar", ".war", ".ear",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".mp3", ".mp4", ".wav", ".avi", ".mov",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".rar",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".lock", ".log",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
})

#: Map file extension → (language_label, parser_factory)
_JS_TS_PARSER: Callable[[], BaseParser] = JavaScriptTypeScriptParser
_PYTHON_PARSER: Callable[[], BaseParser] = PythonParser

EXTENSION_MAP: dict[str, tuple[str, Callable[[], BaseParser]]] = {
    ".py":   ("Python",     _PYTHON_PARSER),
    ".js":   ("JavaScript", _JS_TS_PARSER),
    ".jsx":  ("JavaScript", _JS_TS_PARSER),
    ".ts":   ("TypeScript", _JS_TS_PARSER),
    ".tsx":  ("TypeScript", _JS_TS_PARSER),
    ".mjs":  ("JavaScript", _JS_TS_PARSER),
    ".cjs":  ("JavaScript", _JS_TS_PARSER),
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class FileInventoryEntry:
    relative_path: str
    file_type: str       # extension, e.g. ".py"
    language: str | None # e.g. "Python", or None if unsupported
    size_bytes: int


@dataclass
class FolderInventoryEntry:
    relative_path: str


@dataclass
class ParsedFileResult:
    relative_path: str
    language: str
    symbols: dict  # raw dict from the language parser


@dataclass
class IntermediateRepresentation:
    analysis_id: int
    repository_path: str
    total_files: int = 0
    total_folders: int = 0
    supported_files: int = 0
    skipped_files: int = 0
    folders: list[FolderInventoryEntry] = field(default_factory=list)
    files: list[FileInventoryEntry] = field(default_factory=list)
    parsed: list[ParsedFileResult] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class RepositoryParserEngine:
    """
    Modular parser engine that scans a cloned repository and produces a
    normalized Intermediate Representation (IR).
    """

    def __init__(self, analysis_id: int, repository_path: str) -> None:
        self.analysis_id = analysis_id
        self.repository_path = repository_path
        self._parser_cache: dict[str, BaseParser] = {}

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def run(self) -> IntermediateRepresentation:
        """Execute the full parsing pipeline and return the IR."""
        print(f"[INFO] [Parser] Starting parse - analysis_id={self.analysis_id}")
        ir = IntermediateRepresentation(
            analysis_id=self.analysis_id,
            repository_path=self.repository_path,
        )

        for dirpath, dirnames, filenames in os.walk(self.repository_path):
            # Prune ignored directories in-place so os.walk skips them
            dirnames[:] = [
                d for d in dirnames
                if d not in IGNORED_DIRS and not d.startswith(".")
            ]

            rel_dir = os.path.relpath(dirpath, self.repository_path)
            if rel_dir != ".":
                ir.folders.append(FolderInventoryEntry(relative_path=rel_dir))
                ir.total_folders += 1

            for fname in filenames:
                abs_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(abs_path, self.repository_path)
                ext = os.path.splitext(fname)[1].lower()

                if ext in IGNORED_EXTENSIONS:
                    ir.skipped_files += 1
                    continue

                lang_info = EXTENSION_MAP.get(ext)
                language = lang_info[0] if lang_info else None

                try:
                    size = os.path.getsize(abs_path)
                except OSError:
                    size = 0

                ir.files.append(FileInventoryEntry(
                    relative_path=rel_path,
                    file_type=ext,
                    language=language,
                    size_bytes=size,
                ))
                ir.total_files += 1

                if lang_info:
                    self._parse_file(abs_path, rel_path, lang_info, ir)

        print(
            f"[INFO] [Parser] Scan complete - "
            f"files={ir.total_files} parsed={ir.supported_files} "
            f"skipped={ir.skipped_files} errors={len(ir.errors)}"
        )
        return ir

    def save(self, ir: IntermediateRepresentation, output_path: str) -> None:
        """Serialize the IR to a JSON file at output_path."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(asdict(ir), f, indent=2, default=str)
        print(f"[INFO] [Parser] IR saved to {output_path}")

    @classmethod
    def load_from_file(cls, path: str) -> IntermediateRepresentation:
        """Load and deserialize an IntermediateRepresentation from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        folders = [
            FolderInventoryEntry(relative_path=folder["relative_path"])
            for folder in data.get("folders", [])
        ]
        files = [
            FileInventoryEntry(
                relative_path=file["relative_path"],
                file_type=file["file_type"],
                language=file.get("language"),
                size_bytes=file.get("size_bytes", 0),
            )
            for file in data.get("files", [])
        ]
        parsed = [
            ParsedFileResult(
                relative_path=p["relative_path"],
                language=p["language"],
                symbols=p["symbols"],
            )
            for p in data.get("parsed", [])
        ]

        return IntermediateRepresentation(
            analysis_id=data["analysis_id"],
            repository_path=data["repository_path"],
            total_files=data.get("total_files", 0),
            total_folders=data.get("total_folders", 0),
            supported_files=data.get("supported_files", 0),
            skipped_files=data.get("skipped_files", 0),
            folders=folders,
            files=files,
            parsed=parsed,
            errors=data.get("errors", []),
        )


    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _get_parser(self, factory: Callable[[], BaseParser]) -> BaseParser:
        key = factory.__name__
        if key not in self._parser_cache:
            self._parser_cache[key] = factory()
        return self._parser_cache[key]

    def _parse_file(
        self,
        abs_path: str,
        rel_path: str,
        lang_info: tuple[str, Callable[[], BaseParser]],
        ir: IntermediateRepresentation,
    ) -> None:
        language, factory = lang_info
        try:
            content = abs_path
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            parser = self._get_parser(factory)
            symbols = parser.parse(rel_path, content)

            ir.parsed.append(ParsedFileResult(
                relative_path=rel_path,
                language=language,
                symbols=symbols,
            ))
            ir.supported_files += 1

        except Exception as exc:
            ir.errors.append({
                "file": rel_path,
                "error": str(exc),
            })
            print(f"[WARN] [Parser] Failed to parse {rel_path}: {exc}")

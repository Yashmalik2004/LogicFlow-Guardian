# LogicFlow Guardian — Parser Engine

**Phase 9A implementation.** Provides a modular, extensible source code parser for the MS2 Agent Service.

---

## Overview

The Parser Engine is a pure Python component that recursively scans a cloned repository, extracts structural information from source files, and produces a normalized **Intermediate Representation (IR)** stored as a JSON artifact.

The parser:
- Requires **no external runtime** (no Node.js, no npm packages)
- Is **modular** — new language parsers can be plugged in with a single registration
- Is **safe** — uses the Python standard library `ast` module for Python files and regex for JS/TS
- Runs **entirely inside MS2** — does not call MS1's database or any AI agents

---

## Architecture

```
RepositoryParserEngine (parser/engine.py)
           │
           ├── Scans & filters repository directory tree
           │     - Ignores: node_modules, .git, dist, build,
           │                coverage, __pycache__, venv, vendor
           │     - Skips: binaries, images, archives, lock files
           │
           ├── Builds inventory (files + folders with metadata)
           │
           └── Dispatches to language parsers via EXTENSION_MAP
                     │
                     ├── PythonParser (parser/languages/python.py)
                     │     └── Uses Python built-in `ast` module
                     │
                     └── JavaScriptTypeScriptParser (parser/languages/javascript.py)
                           └── Uses multi-pass regex (no npm required)
```

After parsing, the IR is serialized to:
```
workspace/analysis-{id}/parser_output.json
```

---

## File Structure

```
ms2-agent/
├── parser/
│   ├── __init__.py
│   ├── base.py                     ← BaseParser abstract interface
│   ├── engine.py                   ← RepositoryParserEngine (main entry)
│   ├── repository_discovery.py     ← Language/framework metadata detection (pre-existing)
│   └── languages/
│       ├── __init__.py
│       ├── python.py               ← Python AST parser
│       └── javascript.py           ← JS/TS regex parser
```

---

## Integration with the Intake Pipeline

After the intake stage sends `READY_FOR_PARSING` to MS1, the parser stage runs automatically inside `repository_intake_service.run()`:

```
READY_FOR_PARSING
       │
       ▼
RepositoryParserEngine.run()       ← Scans + parses repo
       │
       ▼
engine.save(ir, parser_output.json) ← Writes artifact
       │
       ▼
COMPLETED webhook → MS1
```

---

## Intermediate Representation (IR) Schema

The parser output (`parser_output.json`) follows this top-level structure:

```json
{
  "analysis_id": 37,
  "repository_path": "/path/to/workspace/analysis-37",
  "total_files": 1076,
  "total_folders": 146,
  "supported_files": 650,
  "skipped_files": 130,
  "folders": [
    { "relative_path": "routes" }
  ],
  "files": [
    {
      "relative_path": "server.ts",
      "file_type": ".ts",
      "language": "TypeScript",
      "size_bytes": 39915
    }
  ],
  "parsed": [
    {
      "relative_path": "server.ts",
      "language": "TypeScript",
      "symbols": {
        "imports": [...],
        "exports": [...],
        "classes": [...],
        "functions": [...],
        "routes": [...],
        "middleware": [...],
        "decorators": [...]
      }
    }
  ],
  "errors": []
}
```

### Symbol Schemas

#### Import
```json
{ "type": "es_import", "specifier": "{ Router }", "module": "express", "line": 3 }
{ "type": "require",   "binding": "express",      "module": "express", "line": 1 }
{ "type": "from_import","module": "fastapi",       "name": "FastAPI",   "line": 1 }
```

#### Export
```json
{ "type": "named",   "name": "router",  "line": 5 }
{ "type": "default", "name": "handler", "line": 10 }
```

#### Class
```json
{
  "name": "UserController",
  "extends": "BaseController",
  "decorators": [{ "name": "@Controller", "args": ["/users"] }],
  "start_line": 12,
  "end_line": 55,
  "methods": [...]
}
```

#### Function / Method
```json
{
  "name": "getUser",
  "params": ["req", "res"],
  "decorators": [{ "name": "@Get", "args": ["/:id"] }],
  "is_async": true,
  "parent_class": "UserController",
  "start_line": 20,
  "end_line": 30
}
```

#### Route
```json
{ "object": "router", "method": "GET",  "path": "/users/:id", "line": 42 }
{ "handler": "get_user", "decorator": "router.get", "path": "/users", "line": 10 }
```

#### Middleware
```json
{ "object": "app", "line": 15 }
```

---

## Supported Languages & Extensions

| Extension | Language   | Parser                         |
|-----------|------------|--------------------------------|
| `.py`     | Python     | `PythonParser` (ast module)    |
| `.js`     | JavaScript | `JavaScriptTypeScriptParser`   |
| `.jsx`    | JavaScript | `JavaScriptTypeScriptParser`   |
| `.ts`     | TypeScript | `JavaScriptTypeScriptParser`   |
| `.tsx`    | TypeScript | `JavaScriptTypeScriptParser`   |
| `.mjs`    | JavaScript | `JavaScriptTypeScriptParser`   |
| `.cjs`    | JavaScript | `JavaScriptTypeScriptParser`   |

---

## Adding a New Language Parser

To add support for a new language (e.g., Go):

1. **Create the parser module** at `parser/languages/go.py`:
   ```python
   from parser.base import BaseParser

   class GoParser(BaseParser):
       def parse(self, file_path: str, content: str) -> dict:
           # ... extraction logic ...
           return { "imports": [...], "functions": [...], ... }
   ```

2. **Register the extension** in `parser/engine.py`:
   ```python
   from parser.languages.go import GoParser

   EXTENSION_MAP[".go"] = ("Go", GoParser)
   ```

That is all. The engine automatically discovers and uses the new parser for matching files.

---

## Ignored Directories

The following directories are automatically excluded from scanning:

| Directory       | Reason                        |
|-----------------|-------------------------------|
| `node_modules`  | npm dependencies              |
| `.git`          | Git metadata                  |
| `dist`          | Compiled output               |
| `build`         | Build artifacts               |
| `coverage`      | Test coverage reports         |
| `__pycache__`   | Python bytecode cache         |
| `venv` / `.venv`| Python virtual environments   |
| `vendor`        | Vendored dependencies         |

---

## Design Principles

- **Zero external runtime dependency**: Uses Python stdlib `ast` module and `re` only.
- **Modular**: `BaseParser` interface decouples the engine from language implementations.
- **Fail-safe**: Individual file parse errors are recorded and do not stop the pipeline.
- **Read-only**: The parser never writes to any database — it only writes a single JSON artifact file.
- **Scoped to MS2**: The parser runs entirely inside MS2's service boundary. MS1 is notified of completion via webhook only.

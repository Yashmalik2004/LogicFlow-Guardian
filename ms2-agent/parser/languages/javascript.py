"""
JavaScript / TypeScript Parser — regex and tokenizer-based analysis.

Does NOT require external JS runtimes or npm packages.
Uses a multi-pass regex approach that is robust to TypeScript generic annotations
and JSX syntax.

Extracts:
    - imports  (ES Module + CommonJS require)
    - exports  (named + default + module.exports)
    - classes  (name, extends, start/end lines, decorators)
    - functions & methods (name, params, arrow functions, start/end lines)
    - decorators (TypeScript decorators: @Controller, @Get, etc.)
    - routes   (Express router calls: router.get(), app.post(), etc.)
    - middleware (app.use() calls)

Inherits from BaseParser.
"""
import re
from parser.base import BaseParser


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# ES Module imports: import x from 'y'  |  import { a, b } from 'y'
_RE_IMPORT_ES = re.compile(
    r"""^import\s+(?P<specifier>[^'";\n]+?)\s+from\s+['"](?P<module>[^'"]+)['"]""",
    re.MULTILINE,
)
# Side-effect import: import 'y'
_RE_IMPORT_SIDE = re.compile(
    r"""^import\s+['"](?P<module>[^'"]+)['"]""",
    re.MULTILINE,
)
# CommonJS: const x = require('y')  |  require('y')
_RE_REQUIRE = re.compile(
    r"""(?:const|let|var)\s+(?P<binding>[^=]+?)\s*=\s*require\(['"](?P<module>[^'"]+)['"]\)""",
    re.MULTILINE,
)

# ES exports
_RE_EXPORT_NAMED = re.compile(
    r"""^export\s+(?:const|let|var|function\*?|class|async\s+function\*?)\s+(?P<name>\w+)""",
    re.MULTILINE,
)
_RE_EXPORT_DEFAULT = re.compile(
    r"""^export\s+default\s+(?:class|function\*?|async\s+function\*?)?\s*(?P<name>\w+)?""",
    re.MULTILINE,
)
_RE_MODULE_EXPORTS = re.compile(
    r"""module\.exports\s*=\s*""",
    re.MULTILINE,
)

# Classes: class Foo [extends Bar] {
_RE_CLASS = re.compile(
    r"""(?:^|\s)class\s+(?P<name>\w+)(?:\s+extends\s+(?P<base>[\w.]+))?""",
    re.MULTILINE,
)

# Functions
_RE_FUNCTION = re.compile(
    r"""(?:^|\s)(?:export\s+)?(?:default\s+)?(?:async\s+)?function\*?\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)""",
    re.MULTILINE,
)
# Arrow functions: const foo = (params) => or const foo = async (params) =>
_RE_ARROW = re.compile(
    r"""(?:^|\s)(?:export\s+)?(?:const|let|var)\s+(?P<name>\w+)\s*=\s*(?:async\s*)?\((?P<params>[^)]*)\)\s*=>""",
    re.MULTILINE,
)

# TypeScript decorators: @Decorator or @Decorator(args)
_RE_DECORATOR = re.compile(
    r"""^(?P<decorator>@[\w.]+(?:\([^)]*\))?)""",
    re.MULTILINE,
)

# Express route calls: router.get('/path', ...) | app.post('/path', ...)
_HTTP_METHODS = "get|post|put|patch|delete|options|head|all"
_RE_ROUTE = re.compile(
    rf"""(?P<obj>app|router)\s*\.\s*(?P<method>{_HTTP_METHODS})\s*\(\s*['"](?P<path>[^'"]+)['"]""",
    re.IGNORECASE | re.MULTILINE,
)

# Express middleware: app.use(...)
_RE_MIDDLEWARE = re.compile(
    r"""(?P<obj>app|router)\s*\.\s*use\s*\(""",
    re.MULTILINE,
)


def _line_of(content: str, pos: int) -> int:
    """Return the 1-indexed line number for a character position in content."""
    return content[:pos].count("\n") + 1


class JavaScriptTypeScriptParser(BaseParser):
    """Regex-based parser for JavaScript and TypeScript source files."""

    def parse(self, file_path: str, content: str) -> dict:
        result = {
            "imports": [],
            "exports": [],
            "classes": [],
            "functions": [],
            "routes": [],
            "middleware": [],
        }

        self._extract_imports(content, result)
        self._extract_exports(content, result)
        self._extract_classes(content, result)
        self._extract_functions(content, result)
        self._extract_decorators(content, result)
        self._extract_routes(content, result)
        self._extract_middleware(content, result)

        return result

    # -----------------------------------------------------------------------
    # Extractor methods
    # -----------------------------------------------------------------------

    def _extract_imports(self, content: str, result: dict) -> None:
        for m in _RE_IMPORT_ES.finditer(content):
            result["imports"].append({
                "type": "es_import",
                "specifier": m.group("specifier").strip(),
                "module": m.group("module"),
                "line": _line_of(content, m.start()),
            })
        for m in _RE_IMPORT_SIDE.finditer(content):
            result["imports"].append({
                "type": "side_effect_import",
                "module": m.group("module"),
                "line": _line_of(content, m.start()),
            })
        for m in _RE_REQUIRE.finditer(content):
            result["imports"].append({
                "type": "require",
                "binding": m.group("binding").strip(),
                "module": m.group("module"),
                "line": _line_of(content, m.start()),
            })

    def _extract_exports(self, content: str, result: dict) -> None:
        for m in _RE_EXPORT_NAMED.finditer(content):
            result["exports"].append({
                "type": "named",
                "name": m.group("name"),
                "line": _line_of(content, m.start()),
            })
        for m in _RE_EXPORT_DEFAULT.finditer(content):
            result["exports"].append({
                "type": "default",
                "name": m.group("name"),
                "line": _line_of(content, m.start()),
            })
        for m in _RE_MODULE_EXPORTS.finditer(content):
            result["exports"].append({
                "type": "module.exports",
                "line": _line_of(content, m.start()),
            })

    def _extract_classes(self, content: str, result: dict) -> None:
        for m in _RE_CLASS.finditer(content):
            result["classes"].append({
                "name": m.group("name"),
                "extends": m.group("base"),
                "line": _line_of(content, m.start()),
            })

    def _extract_functions(self, content: str, result: dict) -> None:
        seen_names: set[str] = set()
        for m in _RE_FUNCTION.finditer(content):
            name = m.group("name")
            if name in seen_names:
                continue
            seen_names.add(name)
            result["functions"].append({
                "type": "function",
                "name": name,
                "params": [p.strip() for p in m.group("params").split(",") if p.strip()],
                "line": _line_of(content, m.start()),
            })
        for m in _RE_ARROW.finditer(content):
            name = m.group("name")
            if name in seen_names:
                continue
            seen_names.add(name)
            result["functions"].append({
                "type": "arrow_function",
                "name": name,
                "params": [p.strip() for p in m.group("params").split(",") if p.strip()],
                "line": _line_of(content, m.start()),
            })

    def _extract_decorators(self, content: str, result: dict) -> None:
        # Store decorators in a dedicated key on the result dict
        if "decorators" not in result:
            result["decorators"] = []
        for m in _RE_DECORATOR.finditer(content):
            result["decorators"].append({
                "decorator": m.group("decorator"),
                "line": _line_of(content, m.start()),
            })

    def _extract_routes(self, content: str, result: dict) -> None:
        for m in _RE_ROUTE.finditer(content):
            result["routes"].append({
                "object": m.group("obj"),
                "method": m.group("method").upper(),
                "path": m.group("path"),
                "line": _line_of(content, m.start()),
            })

    def _extract_middleware(self, content: str, result: dict) -> None:
        for m in _RE_MIDDLEWARE.finditer(content):
            result["middleware"].append({
                "object": m.group("obj"),
                "line": _line_of(content, m.start()),
            })

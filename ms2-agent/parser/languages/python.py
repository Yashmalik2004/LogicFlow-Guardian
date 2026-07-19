"""
Python Parser — uses Python's built-in `ast` module.

Extracts:
    - imports (import x, from y import z)
    - classes (name, bases, decorators, start/end lines)
    - functions and methods (name, params, decorators, start/end lines)
    - routes (FastAPI/Flask/Django route decorators)
    - decorators (with arguments)

Inherits from BaseParser.
"""
import ast
from parser.base import BaseParser


# ---------------------------------------------------------------------------
# Route decorator patterns for Python web frameworks
# ---------------------------------------------------------------------------
_ROUTE_PREFIXES = {
    "app.get", "app.post", "app.put", "app.patch", "app.delete", "app.options",
    "app.head", "app.route",
    "router.get", "router.post", "router.put", "router.patch", "router.delete",
    "router.options", "router.head", "router.route",
    "blueprint.get", "blueprint.post", "blueprint.put", "blueprint.patch",
    "blueprint.delete", "blueprint.route",
    # Django URLs are handled at the import level
}


def _decorator_name(node: ast.expr) -> str:
    """Return a string representation of a decorator expression."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_decorator_name(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return "<decorator>"


def _decorator_args(node: ast.expr) -> list[str]:
    """Return positional string args of a decorator call."""
    if not isinstance(node, ast.Call):
        return []
    args = []
    for arg in node.args:
        if isinstance(arg, ast.Constant):
            args.append(str(arg.value))
        else:
            try:
                args.append(ast.unparse(arg))
            except Exception:
                args.append("<expr>")
    return args


def _param_names(func: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Extract ordered parameter names from a function definition."""
    params = []
    for arg in func.args.posonlyargs + func.args.args + func.args.kwonlyargs:
        params.append(arg.arg)
    if func.args.vararg:
        params.append(f"*{func.args.vararg.arg}")
    if func.args.kwarg:
        params.append(f"**{func.args.kwarg.arg}")
    return params


class PythonParser(BaseParser):
    """AST-based parser for Python source files."""

    def parse(self, file_path: str, content: str) -> dict:
        result = {
            "imports": [],
            "exports": [],      # Python has no explicit exports; leave empty
            "classes": [],
            "functions": [],
            "routes": [],
            "middleware": [],
        }

        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError as exc:
            result["_parse_error"] = str(exc)
            return result

        for node in ast.walk(tree):
            # ---------------------------------------------------------------
            # Imports
            # ---------------------------------------------------------------
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append({
                        "type": "import",
                        "module": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno,
                    })

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    result["imports"].append({
                        "type": "from_import",
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno,
                    })

        # Walk top-level and class-level nodes for classes and functions
        self._visit_body(tree.body, result, parent_class=None)
        return result

    # -----------------------------------------------------------------------
    # Recursive body visitor
    # -----------------------------------------------------------------------

    def _visit_body(
        self,
        body: list[ast.stmt],
        result: dict,
        parent_class: str | None,
    ) -> None:
        for node in body:
            if isinstance(node, (ast.ClassDef,)):
                self._handle_class(node, result)

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._handle_function(node, result, parent_class=parent_class)

    def _handle_class(self, node: ast.ClassDef, result: dict) -> None:
        bases = []
        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except Exception:
                bases.append("<base>")

        decorators = self._extract_decorators(node)
        class_entry = {
            "name": node.name,
            "bases": bases,
            "decorators": decorators,
            "start_line": node.lineno,
            "end_line": node.end_lineno,
            "methods": [],
        }

        # Visit methods inside the class
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_entry = self._build_function_entry(
                    item, parent_class=node.name
                )
                class_entry["methods"].append(method_entry)
                # Routes inside a class (e.g. Django class-based views)
                self._check_route(item, result)

        result["classes"].append(class_entry)

        # Also recurse nested classes
        for item in node.body:
            if isinstance(item, ast.ClassDef):
                self._handle_class(item, result)

    def _handle_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        result: dict,
        parent_class: str | None,
    ) -> None:
        if parent_class:
            return  # Handled inside _handle_class
        entry = self._build_function_entry(node, parent_class=None)
        result["functions"].append(entry)
        self._check_route(node, result)

    def _build_function_entry(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        parent_class: str | None,
    ) -> dict:
        decorators = self._extract_decorators(node)
        return {
            "name": node.name,
            "params": _param_names(node),
            "decorators": decorators,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "parent_class": parent_class,
            "start_line": node.lineno,
            "end_line": node.end_lineno,
        }

    def _extract_decorators(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
    ) -> list[dict]:
        decorators = []
        for dec in node.decorator_list:
            decorators.append({
                "name": _decorator_name(dec),
                "args": _decorator_args(dec),
            })
        return decorators

    def _check_route(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        result: dict,
    ) -> None:
        """If the function has route decorators, record them in result['routes']."""
        for dec in node.decorator_list:
            name = _decorator_name(dec)
            if any(name == prefix or name.startswith(prefix + ".") for prefix in _ROUTE_PREFIXES):
                args = _decorator_args(dec)
                result["routes"].append({
                    "handler": node.name,
                    "decorator": name,
                    "path": args[0] if args else None,
                    "line": node.lineno,
                })

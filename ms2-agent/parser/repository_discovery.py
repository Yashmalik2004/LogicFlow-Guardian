"""
Repository discovery — metadata-only language and framework detection.

Detection is based exclusively on the presence of well-known project metadata
files (e.g., package.json, requirements.txt, pom.xml). Source code is never
read or parsed.
"""
import os
from typing import Tuple

# ---------------------------------------------------------------------------
# Detection rules
# Each entry: (language, framework, trigger_files)
# Rules are evaluated in order; first match wins.
# ---------------------------------------------------------------------------
_RULES: list[Tuple[str, str | None, list[str]]] = [
    # Python — framework-specific first
    ("Python", "Django",      ["manage.py", "requirements.txt"]),
    ("Python", "Flask",       ["requirements.txt", "wsgi.py"]),
    ("Python", "FastAPI",     ["requirements.txt", "main.py"]),
    ("Python", "FastAPI",     ["pyproject.toml", "main.py"]),
    ("Python", None,          ["requirements.txt"]),
    ("Python", None,          ["pyproject.toml"]),
    ("Python", None,          ["setup.py"]),
    ("Python", None,          ["Pipfile"]),
    # JavaScript / TypeScript
    ("TypeScript", "Next.js", ["package.json", "next.config.ts"]),
    ("TypeScript", "Next.js", ["package.json", "next.config.js"]),
    ("JavaScript", "Next.js", ["package.json", "next.config.js"]),
    ("TypeScript", "NestJS",  ["package.json", "nest-cli.json"]),
    ("JavaScript", "Express", ["package.json", "app.js"]),
    ("TypeScript", "Express", ["package.json", "app.ts"]),
    ("JavaScript", None,      ["package.json"]),
    ("TypeScript", None,      ["tsconfig.json"]),
    # Java
    ("Java", "Spring Boot",   ["pom.xml", "src/main/java"]),
    ("Java", "Spring Boot",   ["build.gradle", "src/main/java"]),
    ("Java", None,            ["pom.xml"]),
    ("Java", None,            ["build.gradle"]),
    # Go
    ("Go", None,              ["go.mod"]),
    # Rust
    ("Rust", None,            ["Cargo.toml"]),
    # Ruby
    ("Ruby", "Rails",         ["Gemfile", "config/routes.rb"]),
    ("Ruby", None,            ["Gemfile"]),
    # PHP
    ("PHP", "Laravel",        ["composer.json", "artisan"]),
    ("PHP", None,             ["composer.json"]),
    # C# / .NET
    ("C#", None,              [".sln"]),  # directory scan
    ("C#", None,              [".csproj"]),
]


def _files_exist(repo_path: str, filenames: list[str]) -> bool:
    """Return True if all trigger files/directories exist in the repo."""
    for name in filenames:
        # Support both direct paths and simple extension-based glob (e.g. ".sln")
        if name.startswith(".") and "." in name[1:]:
            # Treat as extension — check if any file with this ext exists in root
            found = any(
                f.endswith(name)
                for f in os.listdir(repo_path)
                if os.path.isfile(os.path.join(repo_path, f))
            )
            if not found:
                return False
        else:
            if not os.path.exists(os.path.join(repo_path, name)):
                return False
    return True


def detect_language_and_framework(
    repo_path: str,
) -> Tuple[str | None, str | None]:
    """
    Inspect the repository's project metadata files and return
    (language, framework). Both values may be None if detection fails.

    Source code files are never opened or parsed.
    """
    for language, framework, triggers in _RULES:
        if _files_exist(repo_path, triggers):
            print(
                f"[INFO] [Discovery] Detected language={language} framework={framework} "
                f"(triggers={triggers})"
            )
            return language, framework

    print("[INFO] [Discovery] Language/framework could not be determined.")
    return None, None

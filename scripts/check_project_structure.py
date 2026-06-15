from __future__ import annotations

import fnmatch
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "README.md",
    "requirements.txt",
    "run.bat",
    "run.ps1",
    ".gitignore",
    ".env.example",
    "app.py",
    ".streamlit/config.toml",
    "config",
    "docs",
    "src",
    "quantum_panorama",
    "scripts",
]

OPTIONAL_BUT_RECOMMENDED = [
    ".github/workflows/auto_collect.yml",
    ".streamlit/secrets.toml.example",
    "docs/GITHUB_UPLOAD_GUIDE.md",
    "docs/DEVELOPMENT_GUIDE.md",
    "docs/PROJECT_STRUCTURE.md",
    "data/.gitkeep",
    "database/.gitkeep",
    "tests/.gitkeep",
]

SENSITIVE_EXACT = [
    ".env",
    ".env.local",
    ".streamlit/secrets.toml",
]

GENERATED_PATTERNS = [
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "*.log",
    "*.pyc",
]

GENERATED_DIRS = {
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "outputs",
    "temp",
    "tmp",
}


def rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def exists(path_text: str) -> bool:
    return (PROJECT_ROOT / path_text).exists()


def scan_files() -> list[Path]:
    ignored_roots = {".git"}
    files: list[Path] = []
    for path in PROJECT_ROOT.rglob("*"):
        relative_parts = path.relative_to(PROJECT_ROOT).parts
        if any(part in ignored_roots for part in relative_parts):
            continue
        files.append(path)
    return files


def find_sensitive(files: list[Path]) -> list[str]:
    found = []
    for item in SENSITIVE_EXACT:
        if exists(item):
            found.append(item)
    return found


def find_generated(files: list[Path]) -> list[str]:
    generated: list[str] = []
    for path in files:
        parts = set(path.relative_to(PROJECT_ROOT).parts)
        if parts & GENERATED_DIRS:
            generated.append(rel(path))
            continue
        if path.is_file() and any(fnmatch.fnmatch(path.name, pattern) for pattern in GENERATED_PATTERNS):
            generated.append(rel(path))
    return sorted(set(generated))


def main() -> int:
    print("Quantum Panorama project structure check")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    missing_required = []
    print("[Required files]")
    for item in REQUIRED_PATHS:
        ok = exists(item)
        print(f"  {'OK  ' if ok else 'MISS'} {item}")
        if not ok:
            missing_required.append(item)

    missing_optional = []
    print()
    print("[Recommended files]")
    for item in OPTIONAL_BUT_RECOMMENDED:
        ok = exists(item)
        print(f"  {'OK  ' if ok else 'WARN'} {item}")
        if not ok:
            missing_optional.append(item)

    files = scan_files()
    sensitive = find_sensitive(files)
    generated = find_generated(files)

    print()
    print("[Sensitive files]")
    if sensitive:
        for item in sensitive:
            print(f"  FOUND {item}  <-- do not upload")
    else:
        print("  OK no .env or Streamlit secrets file found")

    print()
    print("[Generated/runtime files]")
    if generated:
        for item in generated[:50]:
            print(f"  IGNORE {item}")
        if len(generated) > 50:
            print(f"  ... and {len(generated) - 50} more")
        print("  These should stay ignored by .gitignore.")
    else:
        print("  OK no generated runtime files found")

    print()
    if missing_required or sensitive:
        print("[Conclusion] NOT READY for GitHub upload.")
        if missing_required:
            print("Missing required paths:", ", ".join(missing_required))
        if sensitive:
            print("Remove or ignore sensitive files before uploading:", ", ".join(sensitive))
        return 1

    if missing_optional:
        print("[Conclusion] READY with warnings. Recommended paths are missing:")
        print(", ".join(missing_optional))
        return 0

    print("[Conclusion] READY for GitHub upload.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

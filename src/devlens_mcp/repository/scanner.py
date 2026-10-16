"""Repository scanner service for DevLens MCP.

Discovers repository structure, detected programming languages, key project
files, and file extension metrics while respecting exclusion rules.
"""

import os
from collections import Counter
from pathlib import Path
from typing import Set, List
from devlens_mcp.config import get_settings
from devlens_mcp.security.exclusions import should_exclude_dir, should_exclude_file
from devlens_mcp.repository.git_info import get_git_status
from devlens_mcp.schemas import RepositoryOverview

# Common extension to language mapping
EXTENSION_TO_LANGUAGE = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".jsx": "JavaScript (React)",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".cs": "C#",
    ".php": "PHP",
    ".rb": "Ruby",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".sql": "SQL",
    ".md": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".xml": "XML",
}

# Important build, configuration, and documentation file names
IMPORTANT_FILE_NAMES = {
    "readme.md",
    "pyproject.toml",
    "package.json",
    "cargo.toml",
    "go.mod",
    "requirements.txt",
    "setup.py",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "makefile",
    "agents.md",
    "license",
    "license.md",
    "tsconfig.json",
}


def scan_repository_overview(repo_root: Path | None = None) -> RepositoryOverview:
    """Scan and compile a structured overview of the target repository.

    Args:
        repo_root: Optional root directory override (defaults to configured repo_root).

    Returns:
        Structured RepositoryOverview model.
    """
    root = (repo_root or get_settings().repo_root).resolve()

    # 1. Inspect top-level non-excluded files and directories
    top_level_dirs: List[str] = []
    top_level_files: List[str] = []

    try:
        for entry in root.iterdir():
            if entry.is_dir():
                if not should_exclude_dir(entry.name):
                    top_level_dirs.append(entry.name)
            elif entry.is_file():
                if not should_exclude_file(entry):
                    top_level_files.append(entry.name)
    except OSError:
        pass

    top_level_dirs.sort()
    top_level_files.sort()

    # 2. Walk the repository tree respecting exclusions
    detected_languages: Set[str] = set()
    extension_counts: Counter[str] = Counter()
    important_files: List[str] = []
    total_files = 0

    for current_dir, dirnames, filenames in os.walk(root):
        # In-place directory filtering: Prevents descending into .git, .venv, node_modules, etc.
        dirnames[:] = [d for d in dirnames if not should_exclude_dir(d)]

        dir_path = Path(current_dir)

        for filename in filenames:
            file_path = dir_path / filename

            # Skip binary and excluded files
            if should_exclude_file(file_path):
                continue

            total_files += 1

            ext = file_path.suffix.lower() or "(no extension)"
            extension_counts[ext] += 1

            # Detect language
            if ext in EXTENSION_TO_LANGUAGE:
                detected_languages.add(EXTENSION_TO_LANGUAGE[ext])

            # Check for important project files
            if filename.lower() in IMPORTANT_FILE_NAMES:
                try:
                    rel_path = file_path.relative_to(root).as_posix()
                    important_files.append(rel_path)
                except ValueError:
                    pass

    # 3. Retrieve Git status
    git_status = get_git_status(root)

    return RepositoryOverview(
        repo_root=str(root),
        detected_languages=sorted(detected_languages),
        top_level_directories=top_level_dirs,
        top_level_files=top_level_files,
        important_project_files=sorted(important_files),
        file_counts_by_extension=dict(extension_counts.most_common()),
        total_files_scanned=total_files,
        git_status=git_status,
    )

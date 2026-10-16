"""Repository discovery tools for DevLens MCP."""

from devlens_mcp.schemas import RepositoryOverview
from devlens_mcp.repository.scanner import scan_repository_overview


def get_repository_overview() -> RepositoryOverview:
    """Get a structured overview of the local repository.

    Returns the canonical repository root, detected programming languages,
    top-level directories and files, key project configurations (e.g. pyproject.toml,
    README), file counts grouped by extension, and Git working-tree status.
    """
    return scan_repository_overview()

"""Pydantic schemas for structured MCP tool responses and resources.

Defines strict type models to ensure clean, structured data returns for
AI clients rather than loose markdown or unstructured text.
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class GitStatusInfo(BaseModel):
    """Read-only Git repository status information."""

    git_available: bool = Field(
        description="Whether git is installed and the directory is inside a git repository."
    )
    branch: Optional[str] = Field(
        default=None, description="Current checked out Git branch name."
    )
    is_dirty: Optional[bool] = Field(
        default=None, description="Whether working tree has uncommitted modifications."
    )
    modified_count: Optional[int] = Field(
        default=None, description="Count of modified or staged files."
    )
    untracked_count: Optional[int] = Field(
        default=None, description="Count of untracked files."
    )


class RepositoryOverview(BaseModel):
    """Structured overview of the local repository."""

    repo_root: str = Field(
        description="Canonical absolute path to the repository root."
    )
    detected_languages: List[str] = Field(
        description="Programming languages detected based on file extensions."
    )
    top_level_directories: List[str] = Field(
        description="List of top-level non-excluded directories."
    )
    top_level_files: List[str] = Field(
        description="List of top-level non-excluded files."
    )
    important_project_files: List[str] = Field(
        description="Key build, config, dependency, and documentation files found."
    )
    file_counts_by_extension: Dict[str, int] = Field(
        description="Mapping of file extensions to counts of discovered files."
    )
    total_files_scanned: int = Field(
        description="Total count of non-excluded files discovered in the repository."
    )
    git_status: Optional[GitStatusInfo] = Field(
        default=None, description="Git branch and dirty status, if available."
    )


class CodeSearchMatch(BaseModel):
    """Individual match excerpt within a file."""

    file_path: str = Field(description="Relative path of the matching file.")
    line_number: int = Field(description="1-indexed line number of the matching line.")
    line_content: str = Field(description="Text content of the matching line.")
    context_before: List[str] = Field(
        default_factory=list, description="Lines of context preceding the match."
    )
    context_after: List[str] = Field(
        default_factory=list, description="Lines of context following the match."
    )


class CodeSearchResult(BaseModel):
    """Structured result of a code search query."""

    query: str = Field(description="The query string or regex pattern that was searched.")
    total_matches: int = Field(description="Total number of matches found across all files.")
    returned_matches: int = Field(description="Number of matches included in this response.")
    is_truncated: bool = Field(
        description="Whether results were capped due to max_search_results limit."
    )
    matches: List[CodeSearchMatch] = Field(description="List of matching excerpts.")


class ReadFileResult(BaseModel):
    """Structured result of reading a file safely."""

    file_path: str = Field(description="Relative path of the file that was read.")
    total_lines: int = Field(description="Total number of lines in the file.")
    start_line: int = Field(description="1-indexed starting line of the returned excerpt.")
    end_line: int = Field(description="1-indexed ending line of the returned excerpt.")
    content: str = Field(description="The requested text lines joined as a string.")
    is_truncated: bool = Field(
        description="Whether the output was truncated due to max_read_lines limit."
    )

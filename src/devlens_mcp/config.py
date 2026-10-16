"""
    Configuration for my Devlens MCP server

Provides type-safe configuration using Pydantic settings with 
support for env variables and defaults.
"""

from functools import lru_cache
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """ Dev Lens MCP Configuration settings """

    model_config = SettingsConfigDict(
        env_prefix="DEVLENS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    repo_root: Path = Field(
        default_factory=lambda: Path.cwd().resolve(),
        description="Resolved absolute path to the target repository root to inspect",
    )

    max_file_size_bytes: int = Field(
        default=1_048_576, #1 MB
        description="Maximum file size in bytes allowed for reading"
    )

    max_search_results:int = Field(
        default=50,
        description="Max number of search result returned for a tool call"
    )

    max_read_lines:int = Field(
        default=2000,
        description="macimum number of lines returned in a single read_file call"
    )

    # Default excluded directories 
    excluded_dirs: set[str] = Field(
        default_factory=lambda:{
            "__pycache__",
            ".git",
            ".venv",
            ".venv39",
            ".venv311",
            ".venv312",
            ".env",
            "node_modules",
            "build",
            "dist",
            "target",
            ".idea",
            ".vscode"
        },
        description="Set of directory names to automatically exclude from file search and indexing"
    )

    # Binary and other files extension to skip

    excluded_extensions: set[str] = Field(
        default_factory=lambda:{
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", 
            ".ico", ".svg", ".pyc", ".pyo", ".pyd", ".exe", ".dll", ".so",
            ".bin", ".o", ".a", ".lib", ".obj", ".pdb", ".map",
            ".lock", # Conda, pip, etc lock files
            ".tar", ".gz", ".bz2", ".xz", ".zst", # Archives
            ".zip", # Zips can be large
            ".db", ".sqlite", ".sqlite3", # Local databases
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", # Documents
            ".msg", # Outlook message files
            ".eml", # Email files
        },
        description="Set of file extensions to automatically exclude from file search and indexing"
    )

    @field_validator("repo_root", mode="after")
    @classmethod
    def validate_and_resolve_root(cls, v:Path) -> Path:
        """ Ensure root repo exists and a directory """
        resolved = v.resolve()
        if not resolved.exists():
            raise ValueError(f"Configured repository root does not exist: {resolved}")
        if not resolved.is_dir():
            raise ValueError(f"The configured repo is not a directory or something we cant understand: {resolved}")
        
        return resolved

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """ Return a cached singleton instance of settings """
    return Settings()
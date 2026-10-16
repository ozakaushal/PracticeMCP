"""Exclusion rules and filtering logic for DevLens MCP.
Provides utilities to determine if directories, files, or paths should be
skipped during repository walking, indexing, and searching.
"""

import textwrap
from pathlib import Path 
from typing import Optional, Iterable
from devlens_mcp.config import get_settings


def should_exclude_dir(dir_name:str, extra_excluded:Optional[Iterable[str]]= None) -> bool:
    """Check if a single directory name should be excluded.
    Args:
        dir_name: The name of the directory (e.g., 'node_modules', '.git').
        extra_excluded: Optional additional directory names to treat as excluded.
    Returns:
        True if the directory should be skipped, False otherwise.
    """

    settings = get_settings()
    excluded = settings.excluded_dirs
    if extra_excluded:
        excluded = excluded.union(extra_excluded)
    return dir_name in excluded


def should_exclude_file(file_path:Path, extra_extension: Optional[Iterable[str]] = None) -> bool:
    """Check if a single file should be excluded based on file extension.
    Args: 
        file_path: The Path object of the file to check.
        extra_extension: Optional iterable of additional extensions to treat as excluded.
    Returns: 
        True if the file should be skipped, False otherwise
    """
    settings = get_settings()
    excluded_extensions = settings.excluded_extensions
    if extra_extension:
        excluded_extensions = excluded_extensions.union(ext.lower() for ext in extra_extension) 

    # check extension
    if file_path.suffix.lower() in excluded_extensions:
        return True

    if file_path.name in {".env", ".env.local", ".env.production", ".env.development"}:
        return True 
    
    return False

def is_path_excluded(relative_path: Path, extra_dirs: Optional[Iterable[str]] = None, extra_extensions: Optional[Iterable[str]] = None) -> bool:
    """
    Determines if a file path should be excluded based on directory names, file name, or file extension.

    Args:
        relative_path: The Path object of the file to check.
        extra_dirs: Optional additional directory names to treat as excluded.
        extra_extensions: Optional iterable of additional extensions to treat as excluded.

    Returns:
        True if the path should be skipped, False otherwise.
    """

    settings = get_settings()
    excluded_dirs = settings.excluded_dirs
    if extra_dirs:
        excluded_dirs = excluded_dirs.union(extra_dirs)

    #check all the parent directories in the path
    for part in relative_path.parts[:-1]:
        if part in excluded_dirs:
            return True
    
    # if the relative path itself is a directory that is excluded
    if len(relative_path.parts) == 1 and relative_path.name in excluded_dirs:
        return True

    
    return should_exclude_file(relative_path, extra_extensions)
    
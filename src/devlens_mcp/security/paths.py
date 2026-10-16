"""Path security and traversal protection for DevLens MCP.
Ensures that all file operations are strictly confined within the configured
repository root, resolves symlinks safely, and blocks binary or oversized files.
"""

from pathlib import Path
from typing import Optional
from devlens_mcp.config import get_settings

class PathSecurityError(ValueError):
    """ Raised when a path violates security rules """
    pass

def resolve_safe_path(relative_path:str | Path, repo_root: Optional[Path] = None) -> Path:
    """Validate and resolve a relative path strictly within the repository root.
    Args:
        relative_path: Path relative to repository root provided by the user/client.
        repo_root: Optional root directory override (defaults to configured repo_root).
    Returns:
        The canonical, fully resolved Path object.
    Raises:
        PathSecurityError: If the path is absolute, attempts traversal (e.g., ../),
                           or resolves to a symlink pointing outside repo_root.
    """
    root = (repo_root or get_settings().repo_root).resolve()
    
    raw_path_str = str(relative_path).strip()
    if not raw_path_str:
        raise PathSecurityError("File path can not be empty")
    
    # Reject null bytes
    if "\x00" in raw_path_str:
        raise PathSecurityError("NULL bytes are not allowed")

    path_obj = Path(raw_path_str)

    if path_obj.is_absolute():
        raise PathSecurityError(f"Absolute path are not permitted")
    
    try:
        resolved_path = (root / path_obj).resolve()
    except Exception as e:
        raise PathSecurityError(f"Failed to resolve path '{raw_path_str}' : {e}") from e

    # Ensure path is inside the repo root or the repo root itself
    try:
        resolved_path.relative_to(root)
    except ValueError:
        raise PathSecurityError(f"This path : '{raw_path_str}' is outside repository root : '{root}'")

    return resolved_path


def is_binary_file(file_path:Path, sample_size:int = 8791) -> bool:
    """Check if the file is a binary file by reading a sample."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(sample_size)
            return b"\x00" in chunk
    except OSError:
        return True



def validate_file_for_reading(
    file_path:Path, max_size_bytes: Optional[int] = None, excluded_extensions: Optional[set[str]] = None
) -> None:
    """Ensure a file exists, is a regular file, is not oversized, and is not binary.
    Args:
        file_path: Canonical resolved path to validate.
        max_size_bytes: Maximum size allowed in bytes.
        excluded_extensions: Set of extensions to reject.
    Raises:
        FileNotFoundError: If the file does not exist.
        PathSecurityError: If the path is a directory, binary, or violates limits.
    """

    settings = get_settings()
    max_size = max_size_bytes or settings.max_file_size_bytes
    disallowed_ext = excluded_extensions or settings.excluded_extensions

    if not file_path.exists():
        raise FileNotFoundError(f"The requested file: '{file_path}' not found")

    if not file_path.is_file():
        raise FileNotFoundError(f"The requested file: '{file_path}' seems to be a directory not a file")

    if file_path.suffix.lower() in disallowed_ext:
        raise PathSecurityError(f"File extension is not allowed")

    file_size = file_path.stat().st_size
    if file_size > max_size:
        raise PathSecurityError(f"The file is too large: Size: {file_size} > {max_size} (allowed)")

    if is_binary_file(file_path):
        raise PathSecurityError(f"The file is detected as a binary file which is not allowed")

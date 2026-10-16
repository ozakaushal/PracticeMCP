"""Safe, read-only Git status inspector for DevLens MCP.

Extracts current branch name and working-tree clean/dirty status using
read-only Git commands without modifying state or exposing credentials.
"""

import shutil
import subprocess
from pathlib import Path
from devlens_mcp.schemas import GitStatusInfo


def get_git_status(repo_root: Path) -> GitStatusInfo:
    """Inspect Git branch and working-tree status safely and non-destructively.

    Args:
        repo_root: Absolute canonical path to the repository root.

    Returns:
        GitStatusInfo containing branch and status details, or git_available=False
        if git is not installed or the directory is not a Git repository.
    """
    # 1. Check if git executable exists on system PATH
    git_bin = shutil.which("git")
    if not git_bin:
        return GitStatusInfo(git_available=False)

    try:
        # 2. Check if repo_root is inside a Git working tree
        is_git_repo = subprocess.run(
            [git_bin, "rev-parse", "--is-inside-work-tree"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if is_git_repo.returncode != 0 or is_git_repo.stdout.strip() != "true":
            return GitStatusInfo(git_available=False)

        # 3. Get current branch name
        branch_res = subprocess.run(
            [git_bin, "branch", "--show-current"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        branch_name = branch_res.stdout.strip()

        # Fallback for detached HEAD state
        if not branch_name:
            head_res = subprocess.run(
                [git_bin, "rev-parse", "--short", "HEAD"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            branch_name = head_res.stdout.strip() or "HEAD (detached)"

        # 4. Check working-tree status (read-only porcelain status)
        status_res = subprocess.run(
            [git_bin, "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        lines = [line for line in status_res.stdout.splitlines() if line.strip()]
        untracked = [line for line in lines if line.startswith("??")]
        modified = [line for line in lines if not line.startswith("??")]

        return GitStatusInfo(
            git_available=True,
            branch=branch_name,
            is_dirty=len(lines) > 0,
            modified_count=len(modified),
            untracked_count=len(untracked),
        )

    except (subprocess.SubprocessError, OSError):
        # Gracefully handle unexpected execution errors or timeouts
        return GitStatusInfo(git_available=False)

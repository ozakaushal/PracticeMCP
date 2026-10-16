"""DevLens MCP Server entrypoint.

Provides the MCP server instance and registers tools, resources, and prompts
for Model Context Protocol clients using standard I/O (stdio) transport.
"""

from mcp.server.mcpserver import MCPServer
from devlens_mcp.tools.repository_tools import get_repository_overview

# Initialize the MCP Server instance
server = MCPServer(
    name="DevLens MCP",
    version="0.1.0",
    instructions=(
        "DevLens MCP is a secure, read-only code intelligence server. "
        "Use its tools to inspect repository structure, search code, and investigate errors."
    ),
)

# Register Feature A: Repository Discovery Tool
server.tool(
    name="get_repository_overview",
    description=(
        "Provides a structured overview of the repository including detected languages, "
        "top-level files/directories, important project configs, file extension counts, "
        "and Git branch/dirty status."
    ),
)(get_repository_overview)


def main() -> None:
    """Run the DevLens MCP server using standard I/O (stdio) transport."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()

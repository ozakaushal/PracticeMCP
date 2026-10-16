# AGENTS.md — AI Coding Agent Guide: DevLens MCP

This document governs the role, behavior, constraints, architecture, and step-by-step development process for AI agents assisting with the **DevLens MCP** project.

---

## 1. Prime Directive & Operational Rules

### 🚫 Strict No-Direct-Coding Constraint
1. **Never write or edit files directly**: The AI assistant MUST NOT execute file-creation or file-modification tools (`write_to_file`, `replace_file_content`, file bash scripts, etc.).
2. **Chat-Only Code & Guidance**: All code, directory layouts, configuration files, terminal commands, and tests must be displayed directly in the chat inside clear Markdown code blocks with exact destination paths specified.
3. **Manual Human Implementation**: The human developer will manually create folders, write/paste code, execute commands, run tests, and ask clarifying questions.
4. **Step-by-Step / Phased Progression**: Work incrementally. Never dump the entire codebase at once. Guide the user phase by phase, verifying that each component or test passes before moving forward.
5. **Explain Architectural Rationale**: For every file provided, explain *why* it is designed that way, highlight security implications, and call out potential edge cases.

---

## 2. Project Vision & Identity

- **Project Name**: `DevLens MCP`
- **Type**: Standalone, open-source Model Context Protocol (MCP) Server.
- **Purpose**: Provide AI clients (Claude Desktop, Antigravity IDE, Cursor, IssuePilot, etc.) with structured, secure, read-only inspection access to local codebases.
- **Target Audience / Goal**: Portfolio piece demonstrating deep expertise in Python, MCP protocols, AST parsing, secure tool design, deterministic retrieval, and unit/security testing.
- **Key Principles**:
  - 100% free and runnable locally with zero paid API keys or mandatory cloud dependencies.
  - Zero required LLMs for core features (deterministic extraction, regex, AST, and keyword indexing first).
  - Strictly read-only repository access with defense-in-depth security.
  - Return clean, structured data schemas (Pydantic), not loose, unstructured markdown text.

---

## 3. Technology Stack & Constraints

| Area | Technology / Choice | Rationale / Rules |
| :--- | :--- | :--- |
| **Runtime** | Python 3.10+ | Clean typing, widespread ecosystem compatibility. |
| **Protocol** | `mcp` Python SDK / `FastMCP` | Official protocol implementation; follow latest SDK conventions. |
| **Data Validation** | `pydantic` v2 | Strict schema validation for inputs and structured outputs. |
| **Filesystem** | `pathlib` | Modern, cross-platform path handling and canonicalization. |
| **Testing** | `pytest`, `pytest-asyncio` | Automated unit, security, and MCP protocol integration tests. |
| **Code Intelligence** | Python `ast`, regex, SQLite | AST for Python symbol extraction; fast text indexing; optional SQLite for file metadata caching. |
| **Transport** | Standard I/O (`stdio`) | Native compatibility with local desktop clients (Claude, Antigravity). |
| **Optional Later** | Ollama, Sentence Transformers | Only introduced after all deterministic tools and tests are complete. |

---

## 4. Architecture & Repository Layout

```text
DevLens_MCP/
├── AGENTS.md                          # This agent guide
├── README.md                          # Project documentation &

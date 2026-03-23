"""gcd-errors MCP server — Known LLM computational chemistry failure modes.

Provides access to the catalog of systematic LLM failure patterns in
computational chemistry (wrong charge/multiplicity, missing dispersion,
confusing electronic energy with free energy, etc.).
"""

from __future__ import annotations

import json
import re
import asyncio
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("gcd-errors")

ERRORS_FILE = Path(__file__).resolve().parents[1] / "specs" / "references" / "verification" / "llm-chem-errors.md"


def _parse_errors() -> list[dict]:
    """Parse the error catalog markdown into structured records."""
    if not ERRORS_FILE.exists():
        return []

    content = ERRORS_FILE.read_text()
    errors = []
    current_error: dict | None = None
    current_section = ""

    for line in content.splitlines():
        # Error header: ### E001: Description
        err_match = re.match(r"^###\s+(E\d+):\s+(.+)", line)
        if err_match:
            if current_error:
                errors.append(current_error)
            current_error = {
                "id": err_match.group(1),
                "title": err_match.group(2).strip(),
                "severity": current_section,
                "pattern": "",
                "example": "",
                "guard": "",
            }
            continue

        # Section headers
        if line.startswith("## Critical"):
            current_section = "critical"
        elif line.startswith("## Serious"):
            current_section = "serious"
        elif line.startswith("## Subtle"):
            current_section = "subtle"

        if current_error:
            if line.startswith("**Pattern**:"):
                current_error["pattern"] = line.replace("**Pattern**:", "").strip()
            elif line.startswith("**Example**:"):
                current_error["example"] = line.replace("**Example**:", "").strip()
            elif line.startswith("**Guard**:"):
                current_error["guard"] = line.replace("**Guard**:", "").strip()

    if current_error:
        errors.append(current_error)

    return errors


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_errors",
            description="List all known LLM computational chemistry failure modes with IDs and severity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "description": "Filter by severity level",
                        "enum": ["critical", "serious", "subtle"],
                    },
                },
            },
        ),
        Tool(
            name="get_error",
            description="Get full details of a specific error pattern by ID (e.g., E001).",
            inputSchema={
                "type": "object",
                "properties": {
                    "error_id": {"type": "string", "description": "Error ID (e.g., 'E001')"},
                },
                "required": ["error_id"],
            },
        ),
        Tool(
            name="search_errors",
            description="Search error patterns by keyword. Useful for checking if a planned action might trigger a known failure mode.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword (e.g., 'basis set', 'dispersion', 'charge')"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_guards_for_task",
            description="Given a task description, return all relevant error guards that should be checked.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_description": {"type": "string", "description": "Description of the computational task being performed"},
                },
                "required": ["task_description"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    errors = _parse_errors()

    if name == "list_errors":
        severity = arguments.get("severity")
        if severity:
            errors = [e for e in errors if e["severity"] == severity]
        summary = [{"id": e["id"], "title": e["title"], "severity": e["severity"]} for e in errors]
        return [TextContent(type="text", text=json.dumps(summary, indent=2))]

    elif name == "get_error":
        error_id = arguments["error_id"].upper()
        match = next((e for e in errors if e["id"] == error_id), None)
        if match is None:
            return [TextContent(type="text", text=json.dumps({
                "error": f"Error '{error_id}' not found",
                "available": [e["id"] for e in errors],
            }))]
        return [TextContent(type="text", text=json.dumps(match, indent=2))]

    elif name == "search_errors":
        query = arguments["query"].lower()
        matches = [
            e for e in errors
            if query in e["title"].lower()
            or query in e["pattern"].lower()
            or query in e["example"].lower()
            or query in e["guard"].lower()
        ]
        return [TextContent(type="text", text=json.dumps(matches, indent=2))]

    elif name == "get_guards_for_task":
        desc = arguments["task_description"].lower()
        # Keyword mapping for relevant error patterns
        keyword_map = {
            "charge": ["E001"],
            "multiplicity": ["E001"],
            "spin": ["E001"],
            "metal": ["E001", "E002"],
            "heavy": ["E002"],
            "ecp": ["E002"],
            "pseudopotential": ["E002"],
            "dispersion": ["E003"],
            "pi-stack": ["E003"],
            "non-covalent": ["E003"],
            "hydrogen bond": ["E003"],
            "free energy": ["E004"],
            "thermodynamic": ["E004"],
            "enthalpy": ["E004"],
            "entropy": ["E004"],
            "frequency": ["E005"],
            "transition state": ["E005"],
            "binding energy": ["E006"],
            "interaction energy": ["E006"],
            "bsse": ["E006"],
            "functional": ["E007"],
            "dft": ["E003", "E004", "E005", "E007"],
            "optimization": ["E005", "E009"],
            "geometry": ["E005", "E009"],
            "md": ["E003"],
            "molecular dynamics": ["E003"],
        }
        relevant_ids: set[str] = set()
        for keyword, eids in keyword_map.items():
            if keyword in desc:
                relevant_ids.update(eids)
        guards = [e for e in errors if e["id"] in relevant_ids]
        return [TextContent(type="text", text=json.dumps(guards, indent=2))]

    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

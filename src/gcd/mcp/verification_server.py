"""gcd-verification MCP server — Chemical consistency and convergence checks.

Exposes the verification kernel for running predicates over evidence registries:
energy conservation, geometry convergence, frequency validation, basis set
convergence, functional sensitivity, symmetry, thermodynamics, and more.
"""

from __future__ import annotations

import json
import asyncio
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gcd.core.constants import VERIFICATION_CHECKS
from gcd.core.kernel import VerificationKernel, DEFAULT_PREDICATES

server = Server("gcd-verification")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_checks",
            description="List all available verification checks with descriptions.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="run_verification",
            description=(
                "Run the full verification kernel against an evidence registry. "
                "Returns a content-addressed verdict with PASS/FAIL/PARTIAL status, "
                "SHA-256 hashes, and per-check results with suggestions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "evidence": {
                        "type": "object",
                        "description": (
                            "Evidence registry — keys map to check-specific data. "
                            "Examples: energy_values, energy_drift, geometry_converged, "
                            "frequencies, imaginary_frequencies, basis_set_series, "
                            "functionals_tested, expected_symmetry, thermodynamic_data, "
                            "experimental_values, expected_charge, sampling_method, etc."
                        ),
                    },
                },
                "required": ["evidence"],
            },
        ),
        Tool(
            name="run_single_check",
            description="Run a single verification check against evidence.",
            inputSchema={
                "type": "object",
                "properties": {
                    "check_id": {
                        "type": "string",
                        "description": "Check to run",
                        "enum": VERIFICATION_CHECKS,
                    },
                    "evidence": {
                        "type": "object",
                        "description": "Evidence data for this specific check",
                    },
                },
                "required": ["check_id", "evidence"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "list_checks":
        checks = []
        for check_id in VERIFICATION_CHECKS:
            predicate = DEFAULT_PREDICATES.get(check_id)
            checks.append({
                "check_id": check_id,
                "description": predicate.__doc__.strip().split("\n")[0] if predicate and predicate.__doc__ else check_id,
                "has_predicate": predicate is not None,
            })
        return [TextContent(type="text", text=json.dumps(checks, indent=2))]

    elif name == "run_verification":
        kernel = VerificationKernel()
        verdict = kernel.verify(arguments["evidence"])
        return [TextContent(type="text", text=json.dumps(verdict.to_dict(), indent=2))]

    elif name == "run_single_check":
        check_id = arguments["check_id"]
        predicate = DEFAULT_PREDICATES.get(check_id)
        if predicate is None:
            return [TextContent(type="text", text=json.dumps({
                "error": f"No predicate registered for check '{check_id}'",
                "available": list(DEFAULT_PREDICATES.keys()),
            }))]
        result = predicate(arguments["evidence"])
        return [TextContent(type="text", text=json.dumps({
            "check_id": result.check_id,
            "name": result.name,
            "status": result.status,
            "severity": result.severity.value,
            "message": result.message,
            "evidence": result.evidence,
            "suggestions": result.suggestions,
        }, indent=2))]

    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

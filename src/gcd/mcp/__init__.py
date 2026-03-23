"""GCD MCP Servers — Model Context Protocol interface for Get Chem Done.

Six servers exposing computational chemistry research tools:
  - state_server: Project state queries
  - conventions_server: Computational parameter lock management
  - protocols_server: Chemistry methodology protocols
  - verification_server: Chemical consistency and convergence checks
  - errors_server: Known LLM computational chemistry failure modes
  - patterns_server: Cross-project learned patterns
"""

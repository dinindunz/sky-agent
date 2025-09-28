"""GitHub MCP streamable-http wrapper package.

This package provides a streamable-http wrapper around the stdio-only GitHub MCP server.
"""

from .proxy import StdioMCPProxy
from .server import create_server, main

__version__ = "0.1.0"
__all__ = ["StdioMCPProxy", "create_server", "main"]
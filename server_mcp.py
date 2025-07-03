# tool_server.py
# --- Imports ---
from fastmcp import FastMCP

# --- Server Setup ---
# Initialize the FastMCP server. It now handles the web server setup internally.
# IMPORTANT: The `llm_base_url` should point to your actual local LLM endpoint.
server = FastMCP(name="Wayland")

@server.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@server.tool
def ls(directory: str) -> str:
    "List the contents of a directory."
    import os
    return "\n".join(os.listdir(directory))

# --- Main Execution Block ---
# This makes the script runnable. We now use the server's own run method,
# which manages the underlying web server.
if __name__ == "__main__":
    print("--- Starting FastMCP Tool Server ---")
    print("The 'add' tool is now available for the LLM.")
    print("Server running on http://localhost:8001")
    print("------------------------------------")
    server.run(transport="http", host="127.0.0.1", port=8001, path="/mcp")

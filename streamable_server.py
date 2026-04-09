import sys
sys.path.insert(0, '/app')

from mcp_kipris.server import mcp

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=6274, path="/mcp")

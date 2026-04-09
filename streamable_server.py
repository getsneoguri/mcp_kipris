import sys
sys.path.insert(0, '/app')

import os
os.environ["FASTMCP_HOST"] = "0.0.0.0"
os.environ["FASTMCP_PORT"] = "6274"
os.environ["FASTMCP_JSON_RESPONSE"] = "true"

from mcp_kipris.server import mcp

mcp.run(transport="streamable-http")

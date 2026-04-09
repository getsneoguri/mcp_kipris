import sys
sys.path.insert(0, '/app')

import os
from mcp_kipris.server import mcp
import uvicorn

# FastMCP에서 Starlette app 직접 추출
app = mcp.streamable_http_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=6274,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )

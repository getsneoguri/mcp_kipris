import sys
sys.path.insert(0, '/app')

import os
from mcp_kipris.server import mcp
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.requests import Request
from starlette.responses import Response
import httpx

mcp_app = mcp.streamable_http_app()

app = Starlette(
    routes=[
        Mount("/mcp", app=mcp_app),
    ]
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "6274"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*",
        root_path=""
    )

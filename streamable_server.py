import sys
sys.path.insert(0, '/app')

import os
from mcp_kipris.server import mcp
import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.routing import Mount

# FastMCP starlette app 추출
mcp_app = mcp.streamable_http_app()

# HTTPSRedirect 없이 직접 마운트
app = Starlette(
    routes=[
        Mount("/mcp", app=mcp_app),
    ]
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=6274,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )

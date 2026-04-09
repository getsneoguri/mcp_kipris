import os
import sys
sys.path.insert(0, '/app')

os.environ.setdefault("KIPRIS_API_KEY", os.getenv("KIPRIS_API_KEY", ""))

from mcp_kipris.server import app
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn

session_manager = StreamableHTTPSessionManager(
    app=app,
    event_store=None,
    json_response=False,
    stateless=True,
)

async def handle_streamable_http(scope, receive, send):
    await session_manager.handle_request(scope, receive, send)

starlette_app = Starlette(
    routes=[
        Mount("/mcp", app=handle_streamable_http),
    ]
)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=6274)

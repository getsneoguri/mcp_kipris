import argparse
import datetime
import json
import logging
import os
import sys
from collections.abc import Sequence
from typing import List

import uvicorn
from dotenv import find_dotenv, load_dotenv
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route



from mcp_kipris.kipris.abc import ToolHandler
from mcp_kipris.kipris.tools import (
    ForeignPatentApplicantSearchTool,
    ForeignPatentApplicationNumberSearchTool,
    ForeignPatentFreeSearchTool,
    ForeignPatentInternationalApplicationNumberSearchTool,
    ForeignPatentInternationalOpenNumberSearchTool,
    KoreanPatentApplicantSearchTool,
    KoreanPatentApplicationNumberSearchTool,
    KoreanPatentDetailSearchTool,
    KoreanPatentFreeSearchTool,
    KoreanPatentRighterSearchTool,
    KoreanPatentSearchTool,
    KoreanPatentSummarySearchTool,
)

_ = load_dotenv(find_dotenv(".env"))

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp-kipris")

api_key = os.getenv("KIPRIS_API_KEY")

if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")

app = Server("mcp-kipris")

tool_handlers = {}


def add_tool_handler(tool_class: ToolHandler):
    global tool_handlers
    tool_handlers[tool_class.name] = tool_class
    logger.info(f"Tool handler added: {tool_class.name}")


def get_tool_handler(name: str) -> ToolHandler | None:
    if name not in tool_handlers:
        return None
    return tool_handlers[name]


add_tool_handler(KoreanPatentApplicantSearchTool())
add_tool_handler(KoreanPatentSearchTool())
add_tool_handler(KoreanPatentRighterSearchTool())
add_tool_handler(KoreanPatentApplicationNumberSearchTool())
add_tool_handler(KoreanPatentSummarySearchTool())
add_tool_handler(KoreanPatentDetailSearchTool())
add_tool_handler(KoreanPatentFreeSearchTool())
add_tool_handler(ForeignPatentApplicantSearchTool())
add_tool_handler(ForeignPatentApplicationNumberSearchTool())
add_tool_handler(ForeignPatentFreeSearchTool())
add_tool_handler(ForeignPatentInternationalApplicationNumberSearchTool())
add_tool_handler(ForeignPatentInternationalOpenNumberSearchTool())


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [tool.get_tool_description() for tool in tool_handlers.values()]


@app.call_tool()
async def call_tool(name: str, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    if not isinstance(args, dict):
        raise RuntimeError("arguments must be dictionary")

    tool_handler = get_tool_handler(name)
    if not tool_handler:
        raise ValueError(f"Unknown tool: {name}")

    try:
        start_time = datetime.datetime.now()
        try:
            result = await tool_handler.run_tool_async(args)
        except (AttributeError, NotImplementedError) as e:
            result = tool_handler.run_tool(args)
        elapsed = (datetime.datetime.now() - start_time).total_seconds()
        logger.info(f"완료: {name}, {elapsed:.2f}초")
        return result
    except Exception as e:
        logger.error(f"오류: {str(e)}")
        raise RuntimeError(f"Error: {str(e)}")


def tool_to_dict(tool: Tool) -> dict:
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema,
    }


def content_to_dict(content) -> dict:
    if isinstance(content, TextContent):
        return {"type": "text", "text": content.text}
    elif isinstance(content, ImageContent):
        return {"type": "image", "url": content.url}
    else:
        return {"type": "embedded", "url": getattr(content, "url", "")}


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    sse = SseServerTransport("/messages/")

    routes = []

    async def handle_sse(request: Request) -> Response:
        try:
            logger.info("SSE 연결 요청")
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as (read_stream, write_stream):
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
            return Response(status_code=204)
        except Exception as e:
            logger.error(f"SSE 오류: {str(e)}")
            return Response(status_code=500)

    async def list_tools_endpoint(request: Request) -> JSONResponse:
        tools = [tool.get_tool_description() for tool in tool_handlers.values()]
        return JSONResponse([tool_to_dict(t) for t in tools])

    async def well_known_mcp(request):
        body = json.dumps({
            "mcpVersion": "2024-01-01",
            "capabilities": ["sse"],
            "sse": {
                "url": "https://mcp-kipris.onrender.com/sse",
                "message_url": "https://mcp-kipris.onrender.com/messages",
            },
        })
        return Response(
            content=body.encode("utf-8"),
            media_type="application/json; charset=utf-8",
            headers={"Content-Length": str(len(body.encode("utf-8")))},
        )

    routes.extend([
        Route("/.well-known/mcp", endpoint=well_known_mcp),
        Route("/sse", endpoint=handle_sse),
        Route("/sse/", endpoint=handle_sse),
        Route("/tools", endpoint=list_tools_endpoint),
        Mount("/messages/", app=sse.handle_post_message),
    ])

  

    return Starlette(debug=debug, routes=routes)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", action="store_true")
    parser.add_argument("--port", type=int, default=6274)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    if args.http:
        logger.info(f"HTTP 서버 시작: {args.host}:{args.port}")
        starlette_app = create_starlette_app(app, debug=True)
        config = uvicorn.Config(app=starlette_app, host=args.host, port=args.port)
        server = uvicorn.Server(config)
        await server.serve()
    else:
        logger.info("stdio 서버 시작")
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

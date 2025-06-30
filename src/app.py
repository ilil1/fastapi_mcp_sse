from fastapi import FastAPI, Request
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from logispot_mcp import mcp
from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse

# FastAPI 앱 생성
app = FastAPI(
    title="FastAPI MCP SSE",
    description="A demonstration of Server-Sent Events with Model Context Protocol integration",
    version="0.1.0",
)

# SSE 메시지 핸들링용 Transport 인스턴스
sse = SseServerTransport("/messages/")

# /messages 엔드포인트를 Mount (실제 메시지 POST는 내부적으로 처리됨)
app.router.routes.append(Mount("/messages", app=sse.handle_post_message))

# /messages 문서용 dummy route
@app.get("/messages", tags=["MCP"], include_in_schema=True)
def messages_docs():
    """
    Messages endpoint for SSE communication.

    This endpoint is used for posting messages to SSE clients.
    Note: This route is for documentation purposes only.
    The actual implementation is handled by the SSE transport.
    """
    pass

# 공통 SSE 핸들러 함수 정의
async def handle_mcp_stream(request: Request):
    """
    SSE connection handler that bridges FastAPI with the MCP server.
    """
    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        await mcp._mcp_server.run(
            read_stream,
            write_stream,
            mcp._mcp_server.create_initialization_options(),
        )

async def handle_mcp_stream_smithery(request: Request, endpoint: str):
    from logispot_mcp import mcp  # 또는 실제 MCP 모듈
    import sse_starlette.sse as sse  # 혹은 사용 중인 SSE 모듈

    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        initialization_options = mcp._mcp_server.create_initialization_options()
        initialization_options["endpoint"] = endpoint

        await mcp._mcp_server.run(
            read_stream,
            write_stream,
            initialization_options,
        )

# /sse 엔드포인트 (예: 브라우저 테스트용)
@app.get("/sse", tags=["MCP"])
async def dev_sse(request: Request):
    """
    Development SSE Endpoint (for direct browser testing).
    """
    return await handle_mcp_stream(request)

# /mcp 엔드포인트 (예: AI용 공식 MCP 통신)
@app.get("/mcp")
async def inspect():
    return {
        "tools": [
            {
                "name": "save_project_context",
                "description": "Save project-specific context with relationships",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Unique identifier for the context"},
                        "projectId": {"type": "string", "description": "Project identifier"},
                        "content": {"type": "string", "description": "Context content to save"},
                        "parentContextId": {"type": "string", "description": "Optional ID of parent context"},
                        "references": {"type": "array", "items": {"type": "string"}, "description": "Optional related context IDs"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional tags for categorizing"},
                        "metadata": {"type": "object", "description": "Optional additional metadata"},
                    },
                    "required": ["id", "projectId", "content"],
                },
            },
            {
                "name": "save_conversation_context",
                "description": "Save conversation context with continuation support",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Unique identifier for the context"},
                        "sessionId": {"type": "string", "description": "Conversation session identifier"},
                        "content": {"type": "string", "description": "Context content to save"},
                        "continuationOf": {"type": "string", "description": "Optional ID of previous context"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional tags for categorizing"},
                        "metadata": {"type": "object", "description": "Optional additional metadata"},
                    },
                    "required": ["id", "sessionId", "content"],
                },
            },
            {
                "name": "get_context",
                "description": "Retrieve context by ID and optional project ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "ID of the context to retrieve"},
                        "projectId": {"type": "string", "description": "Optional project ID for project contexts"},
                    },
                    "required": ["id"],
                },
            },
            {
                "name": "list_contexts",
                "description": "List contexts with filtering options",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectId": {"type": "string", "description": "Optional project ID to filter by"},
                        "tag": {"type": "string", "description": "Optional tag to filter by"},
                        "type": {"type": "string", "enum": ["project", "conversation"], "description": "Optional type to filter by"},
                    },
                },
            },
        ],
        "version": "0.1.0",
        "status": "success"
    }

# 기타 라우트 불러오기 (circular import 방지)
import routes  # noqa

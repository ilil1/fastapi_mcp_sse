import os
from fastapi import FastAPI, Request
from fastapi_mcp import FastApiMCP           # ⬅️  NEW
from logispot_mcp import mcp                 # 기존 직접 등록한 툴 유지 시 사용 가능

app = FastAPI(
    title="FastAPI MCP SSE",
    version="1.0.0",
)

# ────────────────────────────────────────────────
# ❶  일반 REST / 기타 라우트 먼저 선언
# ────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "ok"}

# ────────────────────────────────────────────────
# ❷  MCP 서버를 FastAPI 앱에 “마운트”
#     ※ 모든 라우트를 선언한 **뒤**에 mount 해야
#        툴이 누락되지 않습니다 :contentReference[oaicite:1]{index=1}
# ────────────────────────────────────────────────
mcp_server = FastApiMCP(
    app,
    name="FastAPI MCP SSE Demo",
    registry=mcp._mcp_server,   # ✅ 명시적으로 registry 전달
    mount_path="/mcp",
    base_url=os.getenv("PUBLIC_URL", "https://fastapi-mcp-sse.onrender.com")
)

mcp_server.mount()               # /mcp , /mcp/sse 라우트 자동 생성


# from fastapi import FastAPI, Request
# from mcp.server.sse import SseServerTransport
# from starlette.routing import Mount
# from logispot_mcp import mcp
# from fastapi import FastAPI, Request, Query
# from fastapi.responses import JSONResponse
#
# # FastAPI 앱 생성
# app = FastAPI(
#     title="FastAPI MCP SSE",
#     description="A demonstration of Server-Sent Events with Model Context Protocol integration",
#     version="0.1.0",
# )
#
# # SSE 메시지 핸들링용 Transport 인스턴스
# sse = SseServerTransport("/messages/")
#
# # /messages 엔드포인트를 Mount (실제 메시지 POST는 내부적으로 처리됨)
# app.router.routes.append(Mount("/messages", app=sse.handle_post_message))
#
# # /messages 문서용 dummy route
# @app.get("/messages", tags=["MCP"], include_in_schema=True)
# def messages_docs():
#     """
#     Messages endpoint for SSE communication.
#
#     This endpoint is used for posting messages to SSE clients.
#     Note: This route is for documentation purposes only.
#     The actual implementation is handled by the SSE transport.
#     """
#     pass
#
# # 공통 SSE 핸들러 함수 정의
# async def handle_mcp_stream(request: Request):
#     """
#     SSE connection handler that bridges FastAPI with the MCP server.
#     """
#     async with sse.connect_sse(request.scope, request.receive, request._send) as (
#         read_stream,
#         write_stream,
#     ):
#         await mcp._mcp_server.run(
#             read_stream,
#             write_stream,
#             mcp._mcp_server.create_initialization_options(),
#         )
#
# # /sse 엔드포인트 (예: 브라우저 테스트용)
# @app.get("/sse", tags=["MCP"])
# async def dev_sse(request: Request):
#     """
#     Development SSE Endpoint (for direct browser testing).
#     """
#     return await handle_mcp_stream(request)
#
# # 기타 라우트 불러오기 (circular import 방지)
# import routes  # noqa

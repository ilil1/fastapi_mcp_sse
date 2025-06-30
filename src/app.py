"""
FastAPI + FastApiMCP + Logispot 툴
"""
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

# logispot_mcp.py 파일에 정의된 FastMCP 인스턴스 가져오기
from logispot_mcp import mcp as logispot_mcp

app = FastAPI(
    title="Logispot MCP Server",
    version="1.0.0",
)

@app.get("/")
async def health():
    return {"status": "ok"}

# FastApiMCP 서버 생성
mcp_server = FastApiMCP(
    app,
    mount_path="/mcp",     # Smithery 가 스캔할 경로
    # transport_path 생략 → 기본 /mcp/sse
)

# logispot 툴 등록 (★ 핵심 한 줄)
mcp_server.register_tools(logispot_mcp)

# 반드시 마지막에 호출
mcp_server.mount()



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

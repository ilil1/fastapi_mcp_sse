from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

# ① FastAPI 앱
app = FastAPI(title="Logispot MCP Demo", version="1.0.0")

@app.get("/")
async def root():
    return {"status": "ok"}

# ② MCP 서버 생성 ― ⛔ mount_path 넣지 않음
mcp_server = FastApiMCP(app)

# ③ (선택) FastAPI 엔드포인트 외에 별도 MCP Tool을 추가하려면
#     └ fastapi-mcp 0.2+에서는 register_tools 메서드가 삭제됐습니다.
#       - 별도 Tool을 노출하려면
#         1) logispot_mcp에 정의한 함수를 FastAPI 라우트로 감싸거나
#         2) modelcontextprotocol SDK의 Low-level Server를 별도 엔드포인트로 mount
#       중 하나를 선택해야 합니다.

# ④ MCP 서버 mount. 여기서 경로를 지정
mcp_server.mount(mount_path="/mcp")   # SSE는 /mcp/sse, POST는 /mcp/messages/

# uvicorn 실행 시: uvicorn src.app:app --reload





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

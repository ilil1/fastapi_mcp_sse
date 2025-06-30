# src/app.py  ───────────────────────────────────────────────────────────────
from fastapi import FastAPI, APIRouter
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from logispot_mcp import token_authentication, get_order_list  # 기존 툴 함수

# 1) FastAPI 앱
app = FastAPI(title="Logispot MCP Demo", version="1.0.0")
router = APIRouter(prefix="/logispot", tags=["Logispot"])

# 2) 로그인 툴 → 라우트
class TokenAuthIn(BaseModel):
    id: str
    password: str
    user_type: int

@router.post(
    "/token-auth",
    operation_id="token_authentication",   # MCP 툴 이름
    response_model=dict
)
async def token_auth_ep(body: TokenAuthIn):
    return await token_authentication(**body.dict())

# 3) 오더 목록 툴 → 라우트
class OrderListIn(BaseModel):
    reference_date: str
    is_driver_management: bool
    start_date: str
    end_date: str
    page: int = 1
    max_result: int = 20
    version2: bool = True

@router.post(
    "/order-list",
    operation_id="get_order_list",         # MCP 툴 이름
    response_model=str
)
async def order_list_ep(body: OrderListIn):
    return await get_order_list(**body.dict())

# 4) 라우터 등록
app.include_router(router)

# 5) MCP 서버 ― mount_path는 여기서만 지정
mcp_server = FastApiMCP(app)
mcp_server.mount(mount_path="/mcp")        # SSE: /mcp/sse , POST: /mcp/messages/

# 6) 테스트용 루트 엔드포인트
@app.get("/")
async def root():
    return {"status": "ok"}



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

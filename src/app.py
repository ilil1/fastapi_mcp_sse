# src/app.py
import os, logging
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("logispot.app")

app = FastAPI(
    title="Logispot MCP Demo",
    version="1.0.0",
    docs_url="/docs",
)

router = APIRouter(prefix="/logispot", tags=["Logispot"])

# ----------------- 툴 엔드포인트 -----------------
class TokenAuthIn(BaseModel):
    id: str = Field(..., example="driver001")
    password: str = Field(..., example="p@ssw0rd!")
    user_type: int = Field(..., example=1)

@router.post("/token-auth", operation_id="token_authentication")
async def token_auth_ep(body: TokenAuthIn):
    from logispot_mcp import token_authentication
    return await token_authentication(**body.model_dump())

class OrderListIn(BaseModel):
    reference_date: str
    is_driver_management: bool
    start_date: str
    end_date: str
    page: int = 1
    max_result: int = 20
    version2: bool = True

@router.post("/order-list", operation_id="get_order_list")
async def order_list_ep(body: OrderListIn):
    from logispot_mcp import get_order_list
    return await get_order_list(**body.model_dump())

app.include_router(router)

# ------------- MCP 서버 초기화 & 마운트 -------------
mcp_server = FastApiMCP(app)

# (선택) 초기화 옵션 커스터마이즈
init_opts = mcp_server._mcp_server.create_initialization_options()
init_opts.system_prompt = "모든 응답은 한국어로, 톤은 차분·친절하게."
mcp_server._mcp_server.initialization_options = init_opts

# 마운트 후 자동으로 /mcp/sse, /mcp/messages/* 경로가 준비됨
mcp_server.mount("/mcp")

# 헬스체크
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

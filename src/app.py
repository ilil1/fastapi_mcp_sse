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

# ------------- MCP 서버 초기화 & 커스텀 옵션 -------------
# MCP 서버 래퍼
mcp_server = FastApiMCP(app)          # <-- FastApiMCP 0.3+ 사용

# 1) 초기화 옵션 객체를 "빈 상태"로 받기
init_opts = mcp_server.server.create_initialization_options()

# 2) SDK 버전에 따라 알맞은 필드에 시스템 프롬프트 넣기
if hasattr(init_opts, "instructions"):        # mcp 1.6+ (권장)
    init_opts.instructions = (
        "당신은 Logispot 물류 전문 AI 비서입니다. "
        "모든 답변은 한국어로, 차분하고 친절한 톤으로 작성하세요."
    )
elif hasattr(init_opts, "system_prompt"):     # 구버전(≤1.5)
    init_opts.system_prompt = (
        "당신은 Logispot 물류 전문 AI 비서입니다. "
        "모든 답변은 한국어로, 차분하고 친절한 톤으로 작성하세요."
    )
else:
    raise RuntimeError("SDK가 다시 바뀐 것 같습니다—필드명을 확인하세요!")

# 3) 수정한 옵션을 서버에 적용
mcp_server.server.initialization_options = init_opts

# 4) 마운트
mcp_server.mount(mount_path="/mcp")         # SSE: /mcp/sse, POST: /mcp/messages/


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

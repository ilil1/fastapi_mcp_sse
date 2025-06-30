# ───────────────────────────────────────────────────────────
#  src/app.py
#  FastAPI + FastApiMCP 서버 (Logispot 데모)
#  -----------------------------------------------------------
import os
import logging
from fastapi import FastAPI, APIRouter
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel, Field

# ------------------------------------------------------------------
# 0. 로깅 설정
# ------------------------------------------------------------------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("logispot.app")

# ------------------------------------------------------------------
# 1. FastAPI 앱 & 공용 라우터
# ------------------------------------------------------------------
app = FastAPI(
    title="Logispot MCP Demo",
    version="1.0.0",
    docs_url="/docs",        # 필요 없으면 None
    redoc_url=None,
)
router = APIRouter(prefix="/logispot", tags=["Logispot"])

# ------------------------------------------------------------------
# 2. 로그인 툴  -------------------------------------------------------
# ------------------------------------------------------------------
class TokenAuthIn(BaseModel):
    id: str = Field(..., example="driver001")
    password: str = Field(..., example="p@ssw0rd!")
    user_type: int = Field(..., example=1)

@router.post(
    "/token-auth",
    operation_id="token_authentication",   # MCP 툴 이름
    response_model=dict,
)
async def token_auth_ep(body: TokenAuthIn):
    # 외부 API 호출은 함수 내부에서만!
    from logispot_mcp import token_authentication
    return await token_authentication(**body.model_dump())

# ------------------------------------------------------------------
# 3. 오더 목록 툴  ---------------------------------------------------
# ------------------------------------------------------------------
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
    operation_id="get_order_list",          # MCP 툴 이름
    response_model=str,
)
async def order_list_ep(body: OrderListIn):
    from logispot_mcp import get_order_list
    return await get_order_list(**body.model_dump())

# ------------------------------------------------------------------
# 4. 라우터 등록
# ------------------------------------------------------------------
app.include_router(router)

# ------------------------------------------------------------------
# 5. MCP 서버 마운트 (/mcp)
#    - SSE  : /mcp/sse
#    - POST : /mcp/messages/
# ------------------------------------------------------------------
mcp_server = FastApiMCP(app)
mcp_server.mount(mount_path="/mcp")

# ------------------------------------------------------------------
# 6. 헬스체크
# ------------------------------------------------------------------
@app.get("/")
async def root():
    return {"status": "ok"}

# ------------------------------------------------------------------
# 7. 로컬 실행용 진입점
#    * Dockerfile CMD 나 `python -m src.app` 으로 실행 가능
# ------------------------------------------------------------------
def main() -> None:
    """Run with:  python -m src.app  (또는 uvicorn)"""
    import uvicorn

    port = int(os.getenv("PORT", "8000"))  # Smithery는 $PORT를 주입
    logger.info(f"🔈  Uvicorn starting on 0.0.0.0:{port}")
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        timeout_keep_alive=90,
    )

if __name__ == "__main__":
    main()



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

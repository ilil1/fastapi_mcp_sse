import os
import logging
from typing import Any
import anyio
import httpx
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP

# ──────────────── 1. 로깅 & 환경변수 ────────────────
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("logispot.mcp")

LARAVEL_API_BASE = os.getenv("LARAVEL_API_BASE", "https://api.test-spot.com/api/v1")

# ──────────────── 2. MCP + FastAPI 앱 생성 ────────────────
app = FastApiMCP(
    "logispot-mcp",
    version="1.0.0",
    description="Logispot MCP Demo (FastApiMCP)",
)

# ──────────────── 3. Laravel API 호출 유틸 ────────────────
def get_api_map() -> dict[str, str]:
    return {
        "token_authentication": f"{LARAVEL_API_BASE}/authentication/token",
        "get_order_list": f"{LARAVEL_API_BASE}/orders/get",
    }

async def call_laravel(func_name: str, payload: dict[str, Any], auth_token: str | None = None) -> dict[str, Any]:
    url = get_api_map().get(func_name)
    if not url:
        return {"error": "API 경로를 찾을 수 없습니다."}

    headers: dict[str, str] = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(url, json=payload, headers=headers)
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError as e:
        logger.error(
            "[Laravel 오류] func=%s status=%s body=%s",
            func_name,
            e.response.status_code,
            e.response.text,
        )
        return {"error": "Laravel API 호출 실패"}
    except Exception as e:
        logger.error("[네트워크 오류] %s", str(e))
        return {"error": "서버와 통신 실패"}

# ──────────────── 4. FastAPI 라우터 (선택적 유지) ────────────────
router = APIRouter(prefix="/logispot", tags=["Logispot"])

class TokenAuthIn(BaseModel):
    id: str = Field(..., example="driver001")
    password: str = Field(..., example="p@ssw0rd!")
    user_type: int = Field(..., example=1)

@router.post("/token-auth", operation_id="token_authentication")
async def token_auth_ep(body: TokenAuthIn):
    """
    ✅ 로그인 (FastAPI REST용)
    """
    resp = await call_laravel("token_authentication", body.model_dump())
    token = resp.get("token") if isinstance(resp, dict) else None
    if token:
        return {"message": "로그인 성공!", "token": token}
    return {"error": "로그인 실패", "detail": resp}

app.include_router(router)

# ──────────────── 5. MCP 툴 등록 ────────────────
@app.mcp.tool(name="token_authentication")
def token_auth_mcp(id: str, password: str, user_type: int = 1) -> dict:
    """
    ✅ 로그인 (MCP용, LLM에서 호출 가능)
    """
    payload = {
        "id": id,
        "password": password,
        "user_type": user_type
    }
    resp = anyio.run(call_laravel, "token_authentication", payload)

    token = resp.get("token") if isinstance(resp, dict) else None
    if token:
        return {"message": "로그인 성공!", "token": token}
    return {"error": "로그인 실패", "detail": resp}

@app.mcp.tool()
def echo(message: str) -> str:
    return f"🔁 {message}"

@app.mcp.tool()
def multiply(x: int, y: int) -> int:
    return x * y

# ──────────────── 6. 시스템 프롬프트 설정 ────────────────
init_opts = app.server.create_initialization_options()
init_opts.instructions = (
    "당신은 Logispot 물류 전문 AI 비서입니다. "
    "모든 답변은 한국어로, 차분하고 친절한 톤으로 작성하세요."
)
app.server.initialization_options = init_opts

# ──────────────── 7. SSE MCP 마운트 ────────────────
app.mount(mount_path="/mcp", transport="sse")

# ──────────────── 8. 헬스체크 ────────────────
@app.get("/")
async def health_check():
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

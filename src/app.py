import os
import logging
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP

# ──────────────── 1. 환경 변수 & 로깅 ────────────────
load_dotenv(".env", override=True)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("logispot.mcp")

# ──────────────── 2. 상수 / 전역 변수 ────────────────
LARAVEL_API_BASE = os.getenv("LARAVEL_API_BASE", "https://api.test-spot.com/api/v1")
AUTH_TOKEN: str | None = None

# ──────────────── 3. FastAPI 앱 ────────────────
app = FastAPI(
    title="Logispot MCP Demo (FastApiMCP)",
    version="1.0.0",
    docs_url="/docs",
)


# ──────────────── 4. Laravel 호출 헬퍼 ────────────────
def get_api_map() -> dict[str, str]:
    return {
        "token_authentication": f"{LARAVEL_API_BASE}/authentication/token",
        "get_order_list": f"{LARAVEL_API_BASE}/orders/get",
    }


async def call_laravel(func_name: str, payload: dict[str, Any], use_auth: bool = False) -> dict[str, Any]:
    """공통 HTTP POST 래퍼"""
    url = get_api_map().get(func_name)
    if not url:
        return {"error": "API 경로를 찾을 수 없습니다."}

    headers: dict[str, str] = {}
    if use_auth and AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:  # 타임아웃 단축
            res = await client.post(url, json=payload, headers=headers)
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError as e:
        logger.error("[Laravel 오류] func=%s status=%s", func_name, e.response.status_code)
        return {"error": "Laravel API 호출 실패"}
    except Exception as e:
        logger.error("[네트워크 오류] %s", str(e))
        return {"error": "서버와 통신 실패"}


# ──────────────── 5. MCP 서버 설정 ────────────────
mcp = FastApiMCP(app)

# 시스템 프롬프트 설정
init_opts = mcp.server.create_initialization_options()
init_opts.instructions = (
    "당신은 Logispot 물류 전문 AI 비서입니다. "
    "모든 답변은 한국어로, 차분하고 친절한 톤으로 작성하세요."
)
mcp.server.initialization_options = init_opts


# ──────────────── 6. MCP 도구 직접 등록 ────────────────
@mcp.tool()
async def token_authentication(
        id: str = Field(..., description="사용자 ID", example="driver001"),
        password: str = Field(..., description="비밀번호", example="p@ssw0rd!"),
        user_type: int = Field(..., description="사용자 타입", example=1)
) -> dict[str, Any]:
    """✅ 로그인 (JWT 저장)"""
    global AUTH_TOKEN

    payload = {"id": id, "password": password, "user_type": user_type}
    resp = await call_laravel("token_authentication", payload)

    token = resp.get("token") if isinstance(resp, dict) else None
    if token:
        AUTH_TOKEN = token
        return {"message": "로그인 성공!"}
    return {"error": "로그인 실패", "detail": resp}


@mcp.tool()
async def get_order_list(
        reference_date: str = Field(..., description="기준 날짜"),
        is_driver_management: bool = Field(..., description="드라이버 관리 여부"),
        start_date: str = Field(..., description="시작 날짜"),
        end_date: str = Field(..., description="종료 날짜"),
        page: int = Field(1, description="페이지 번호"),
        max_result: int = Field(20, description="최대 결과 수"),
        version2: bool = Field(True, description="버전2 사용 여부")
) -> dict[str, Any]:
    """✅ 주문 목록 조회 (토큰 필요)"""

    # 🔥 핵심: 인증 없이도 응답 (도구 스캔용)
    if not AUTH_TOKEN:
        return {
            "status": "authentication_required",
            "message": "이 도구를 사용하려면 먼저 token_authentication으로 로그인하세요.",
            "sample_response": {
                "orders": [],
                "total_count": 0,
                "page": page
            }
        }

    # 실제 API 호출
    payload = {
        "reference_date": reference_date,
        "is_driver_management": is_driver_management,
        "start_date": start_date,
        "end_date": end_date,
        "page": page,
        "max_result": max_result,
        "version2": version2
    }

    resp = await call_laravel("get_order_list", payload, use_auth=True)
    return resp


# ──────────────── 7. MCP 마운트 ────────────────
mcp.mount(mount_path="/mcp", transport="sse")


# ──────────────── 8. 헬스체크 ────────────────
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

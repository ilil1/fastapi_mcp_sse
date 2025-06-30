# from typing import Any
# import httpx
# from mcp.server.fastmcp import FastMCP
# from dotenv import load_dotenv
# import os
#
# # 전역 변수
# auth_token = None
#
# LARAVEL_API_BASE = "https://api.test-spot.com/api/v1"
#
# # MCP 서버 인스턴스
# mcp = FastMCP("logispot_mcp")
#
# # Laravel API 경로 매핑
# def get_api_map():
#     return {
#         "token_authentication": f"{LARAVEL_API_BASE}/authentication/token",
#         "get_order_list": f"{LARAVEL_API_BASE}/orders/get"
#     }
#
# # 공통 API 호출 함수
# async def call_laravel(func_name: str, payload: dict, use_auth: bool = False):
#     url = get_api_map().get(func_name)
#     if not url:
#         return {"error": "API 경로를 찾을 수 없습니다."}
#
#     headers = {}
#     if use_auth and auth_token:
#         headers["Authorization"] = f"Bearer {auth_token}"
#
#     async with httpx.AsyncClient(timeout=10.0) as client:
#         try:
#             res = await client.post(url, json=payload, headers=headers)
#             res.raise_for_status()
#             return res.json()
#         except httpx.HTTPStatusError as e:
#             # 개발 로그용
#             print(f"[Laravel 오류] status={e.response.status_code}, body={e.response.text}")
#             return {"error": "스케줄 조회 중 문제가 발생했습니다. 관리자에게 문의해주세요."}
#         except Exception as e:
#             print(f"[네트워크 오류] {str(e)}")
#             return {"error": "서버와의 연결에 실패했습니다."}
#
#
# # ✅ 9. 토큰 인증 (로그인)
# @mcp.tool()
# async def token_authentication(id: str, password: str, user_type: int):
#     """
#     사용자 로그인 후 토큰은 내부에 저장되며, 외부로는 노출되지 않습니다.
#     """
#     global auth_token
#     response = await call_laravel("token_authentication", {
#         "id": id,
#         "password": password,
#         "user_type": user_type
#     })
#
#     token = None
#     try:
#         token = response.get("token")
#     except Exception:
#         pass
#
#     if token:
#         auth_token = token
#         print("✅ 로그인 성공. 토큰 저장됨.")
#         return {"message": "로그인 성공"}
#     else:
#         print("❌ 로그인 실패:", response)
#         return {"error": "로그인 실패"}
#
# # ✅ 10. 오더 목록 조회 (파라미터 상세 지정)
# @mcp.tool()
# async def get_order_list(
#     reference_date: str,
#     is_driver_management: bool,
#     start_date: str,
#     end_date: str,
#     page: int = 1,
#     max_result: int = 20,
#     version2: bool = True
# ):
#     """
#     오더 목록을 조회합니다. 날짜 기준, 운전기사 관리 여부, 페이지 정보 등을 설정할 수 있습니다.
#     """
#     global auth_token
#     if not auth_token:
#         return "❌ 인증 토큰이 없습니다. 먼저 로그인하세요."
#
#     payload = {
#         "reference_date": reference_date,
#         "is_driver_management": is_driver_management,
#         "start_date": start_date,
#         "end_date": end_date,
#         "page": page,
#         "max_result": max_result,
#         "version2": version2
#     }
#
#     response = await call_laravel("get_order_list", payload, use_auth=True)
#
#     if "error" in response:
#         return f"❌ 오류: {response['error']}"
#
#     orders = response.get("orders", [])
#     pagination = response.get("pagination", {})
#     stats = response.get("stat", [])
#
#     message_lines = [
#         f"{start_date}부터 {end_date}까지의 주문 목록을 조회한 결과입니다:",
#         "📋 **주문 요약**",
#         f"\n총 주문 건수: {pagination.get('total', 0)}건",
#         f"페이지: {pagination.get('current_page', 1)}/{pagination.get('last_page', 1)} (총 {len(orders)}건)\n"
#     ]
#
#     for order in orders:
#         message_lines.append("🚛 **주문 상세 정보**")
#         message_lines.append(f"주문 #{order['order_id']}")
#         message_lines.append("")
#         message_lines.append(f"주문 ID: {order['order_id']} (내부 ID: {order['id']})")
#         message_lines.append(f"주문 생성일: {order['order_created_at']}")
#         message_lines.append(f"주문 상태: {order.get('order_status_text', '알 수 없음')}")
#         message_lines.append("")
#         message_lines.append("👥 **관련자 정보**")
#         message_lines.append(f"고객사: {order.get('client_name', '-')}")
#         message_lines.append(f"주문자: {order.get('user_client_name', '-')}"
#                              f" ({order.get('user_client_phone_number', '-')})")
#         message_lines.append(f"운전기사: {order.get('user_driver_name', '-')}"
#                              f" ({order.get('user_driver_phone_number', '-')})")
#         message_lines.append(f"차량: {order.get('user_driver_number_plate', '-')} ({order.get('car_ton', '-') + '톤 트럭'})")
#         message_lines.append(f"커스텀 코드: {order.get('custom_code', '-')}")
#         message_lines.append("")
#         message_lines.append("📦 **화물 정보**")
#         message_lines.append(f"화물명: {order.get('freight_name', '-')}")
#         message_lines.append("무게/크기: 미지정")  # 필요한 경우 상세 필드 추가
#         message_lines.append("")
#         message_lines.append("🗺️ **운송 정보**")
#         message_lines.append(f"상차일시: {order.get('load_date')} ({order.get('load_time', '-')})")
#         message_lines.append(f"상차지: {order.get('load_company_name')} ({order.get('load_address')})")
#         message_lines.append(f"하차일시: {order.get('unload_date')} ({order.get('unload_time', '-')})")
#         message_lines.append(f"하차지: {order.get('unload_company_name')} ({order.get('unload_address')})")
#         message_lines.append("")
#         message_lines.append("💰 **운임 정보**")
#         fee = order.get('order_pay_order_fee') or order.get('order_pay_contract_fee') or 0
#         message_lines.append(f"계약 운임: {int(fee)}원")
#         message_lines.append(f"결제 방법: {'선불' if order.get('order_pay_method') == 1 else '기타'}")
#         message_lines.append(f"부가세율: {order.get('pays', [{}])[0].get('vat', 0)}%")
#         message_lines.append("")
#
#     # 통계 요약
#     if stats:
#         message_lines.append("📊 **통계 요약**\n")
#         for stat in stats:
#             message_lines.append(f"{stat.get('order_status', '-')} 상태: {stat.get('cnt', 0)}건 "
#                                  f"(계약운임 {stat.get('contract_fee', '0')}원)")
#         message_lines.append("")
#
#     return "\n".join(message_lines).strip()
#
# if __name__ == "__main__":
#     # Initialize and run the server
#     mcp.run(transport="sse")



# import os
#
# api_base = os.getenv("LARAVEL_API_BASE")
#
# if not api_base:
#     raise RuntimeError("LARAVEL_API_BASE 환경변수가 설정되지 않았습니다!")
#
# LARAVEL_API_BASE = api_base

# # .env 파일 불러오기
# load_dotenv()
#
# # 환경 구분
# env = os.getenv("APP_ENV", "local")
#
# # 환경에 따라 API 주소 선택
# if env == "test":
#     api_base = os.getenv("LARAVEL_TEST_API_BASE")
# elif env == "prod":
#     api_base = os.getenv("LARAVEL_PROD_API_BASE")
# else:
#     api_base = os.getenv("LARAVEL_LOCAL_API_BASE")
#
# # 예외 처리: 환경변수가 빠졌을 때 명확하게 알림
# if not api_base:
#     raise RuntimeError("API 주소가 설정되지 않았습니다! .env 파일을 확인해주세요.")
#
# # 전역적으로 사용할 API Base URL
# LARAVEL_API_BASE = api_base
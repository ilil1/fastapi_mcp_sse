import uvicorn
import os
from app import app

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

def run():
    print(f"🔵 MCP server starting on {HOST}:{PORT}")  # 로그 추가
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")

if __name__ == "__main__":
    run()



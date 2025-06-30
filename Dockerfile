FROM python:3.12-slim

# ① 의존성
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ② 소스 코드
COPY src ./src
# 패키지 인식 보조 (이미 있으면 무시)
RUN test -f src/__init__.py || touch src/__init__.py

# ③ 실행
WORKDIR /app/src
EXPOSE 8000
CMD ["sh", "-c", "uvicorn src.app:app --host 0.0.0.0 --port ${PORT:-8000} --timeout-keep-alive 90"]

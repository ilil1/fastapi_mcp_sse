FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY pyproject.toml README.md ./
COPY src ./src

# pip 및 uv 설치 후 의존성 설치 (올바른 방식)
RUN pip install --upgrade pip && pip install uv \
    && uv pip install . --system

# 포트 오픈 (FastAPI 기본 포트)
EXPOSE 8000

# MCP 서버 실행
CMD ["uv", "run", "start"]


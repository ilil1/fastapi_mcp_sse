FROM python:3.13

WORKDIR /app

# 의존성 설치 전 필요한 파일 복사
COPY pyproject.toml README.md ./

# 의존성 설치 (uv 사용 시)
RUN pip install --upgrade pip && pip install uv \
    && uv pip install . --system

# 소스코드 복사
COPY src ./src

EXPOSE 8000

CMD ["uv", "run", "start"]

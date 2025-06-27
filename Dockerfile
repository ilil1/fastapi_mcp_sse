FROM python:3.13

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

# pip, uv 설치 후 pyproject.toml 기반 패키지 설치
RUN pip install --upgrade pip && pip install uv \
    && uv pip install . --system

EXPOSE 8000

CMD ["uv", "run", "start"]


FROM python:3.13

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip && pip install uv \
    && uv pip install . --system

CMD ["python", "src/server.py"]



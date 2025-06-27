FROM python:3.10

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip && pip install uv \
    && uv pip install -r pyproject.toml --system

EXPOSE 8000

CMD ["uv", "run", "start"]

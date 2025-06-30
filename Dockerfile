FROM python:3.13

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

# ✅ uv 대신 pip 사용
RUN pip install --upgrade pip && pip install .  # <--- 변경됨

CMD ["python", "src/server.py"]



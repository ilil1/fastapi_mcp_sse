FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src"

WORKDIR /app

# 의존성 설치 (pyproject → requirements.txt 변환)
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    python - <<'PY' > requirements.txt
import tomllib, pathlib; deps = tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']
pathlib.Path('requirements.txt').write_text('\n'.join(deps))
PY
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY . /app

EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]


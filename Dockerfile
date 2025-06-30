FROM python:3.12-slim

# 1) 시스템 기본 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 2) 의존성 설치
COPY pyproject.toml ./
RUN python -m pip install --upgrade pip \
 && python - <<'PY' > requirements.txt
import tomllib, sys, pathlib
deps = tomllib.load(open('pyproject.toml', 'rb'))['project']['dependencies']
pathlib.Path('requirements.txt').write_text('\n'.join(deps))
PY
RUN pip install --no-cache-dir -r requirements.txt

# 3) 소스 복사
COPY . /app

# 4) 포트 공개 (권장)
EXPOSE 8000

# 5) 실행
CMD ["uvicorn", "gpters_search_mcp_server:app", "--host", "0.0.0.0", "--port", "8000"]



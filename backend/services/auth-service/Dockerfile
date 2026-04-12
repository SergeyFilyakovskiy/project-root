# syntax=docker/dockerfile:1
FROM python:3.12-slim

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install uv -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY app/ ./app/

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
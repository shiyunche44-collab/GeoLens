FROM python:3.12-slim
RUN pip install --no-cache-dir "uv>=0.8,<0.9"
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PATH="/app/.venv/bin:$PATH"
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .
RUN uv sync --frozen --no-dev
EXPOSE 8000
CMD ["uvicorn", "geolens.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

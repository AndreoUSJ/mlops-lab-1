# ---------------------------------------------------------
# Stage 1 - Builder
# ---------------------------------------------------------

FROM python:3.11-slim AS builder

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first for better Docker caching
COPY pyproject.toml uv.lock ./

# Install locked production dependencies.
# --no-install-project is needed here because the source code
# has intentionally not been copied yet.
RUN uv sync --frozen --no-dev --no-install-project


# ---------------------------------------------------------
# Stage 2 - Runtime
# ---------------------------------------------------------

FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy the virtual environment built in Stage 1
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY src/ ./src/

# Make the virtual environment executables available
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "src.food11.serve:app", "--host", "0.0.0.0", "--port", "8000"]
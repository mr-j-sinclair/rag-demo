# Start with a lightweight Linux image containing Python 3.11.
FROM python:3.11-slim

# Copy uv from its official image.
# Pinning the version makes builds reproducible.
COPY --from=ghcr.io/astral-sh/uv:0.12.6 /uv /uvx /bin/

# All following commands run inside /app.
WORKDIR /app

# Copy dependency files before application code.
# Docker can reuse this layer when only our Python code changes.
COPY pyproject.toml uv.lock ./

# Install production dependencies, but not our project yet.
# --no-dev excludes pytest and ruff.
RUN uv sync --locked --no-dev --no-install-project

# Copy the application source, data files, and other required project files.
COPY . /app

# Install the project itself now that its source code exists.
RUN uv sync --locked --no-dev

# The embedding model is NOT baked into the image, to keep it small and reduce
# Artifact Registry storage costs. KnowledgeBase loads it by its Hugging Face Hub id,
# so each cold-started instance downloads only the files it needs (~90 MB) on startup
# (observed cold start: ~1 minute, including indexing).

# Make commands installed in the virtual environment directly available.
ENV PATH="/app/.venv/bin:$PATH"

# Document the application's default listening port.
EXPOSE 8080

# Start the FastAPI server.
# Cloud Run supplies PORT; 8080 is the fallback value.
CMD ["sh", "-c", "uvicorn rag_demo.api:app --host 0.0.0.0 --port ${PORT:-8080}"]

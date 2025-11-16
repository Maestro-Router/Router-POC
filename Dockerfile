# syntax=docker/dockerfile:1

# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock uv.toml ./

# Install dependencies
# Using --frozen to ensure lock file is respected
# Using --no-dev to avoid installing development dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY app ./app
COPY translator.py ./

# Expose Gradio default port
EXPOSE 7860

# Set environment variables for better container behavior
ENV PYTHONUNBUFFERED=1

# Run the application
# Using uv run to ensure proper environment
CMD ["uv", "run", "gradio", "app/main.py", "--server-name", "0.0.0.0", "--server-port", "7860"]

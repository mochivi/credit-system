FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy requirements first for better caching
COPY pyproject.toml ./

# Install Python deps
RUN python -m pip install -U pip setuptools wheel \
 && python -m pip install .

# Copy project files
COPY . /app

# Default command can be overridden by compose
CMD ["uvicorn", "ecs.app:app", "--host", "0.0.0.0", "--port", "8000"]

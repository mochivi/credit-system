FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy project
COPY . /app

# Install Python deps
RUN python -m pip install -U pip setuptools wheel \
 && python -m pip install .

# Default command can be overridden by compose
CMD ["uvicorn", "ecs.app:app", "--host", "0.0.0.0", "--port", "8000"]

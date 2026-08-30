FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY database/ ./database/
COPY api/ ./api/
COPY config/ ./config/
COPY models/ ./models/
COPY recommendation/ ./recommendation/
COPY learning_path/ ./learning_path/
COPY adaptive_learning/ ./adaptive_learning/
COPY skill_gap/ ./skill_gap/
COPY services/ ./services/
COPY frontend/ ./frontend/

# Expose port
EXPOSE 8000

# Start command: Apply migrations, seed, and launch FastAPI
CMD ["sh", "-c", "alembic upgrade head && python -m database.seed && uvicorn api.main:app --host 0.0.0.0 --port 8000"]

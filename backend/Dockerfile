# --- Stage 1: Build & Install Dependencies ---
FROM python:3.11-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed for compiling certain Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages into a local virtual environment path
RUN python -m venv /opt/.vnv
ENV PATH="/opt/.vnv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final Lean Runtime ---
FROM python:3.11-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/.vnv/bin:$PATH"

WORKDIR /app

# Copy the pre-compiled virtual environment from the builder stage
COPY --from=builder /opt/.vnv /opt/.vnv

# Copy the rest of your application code
COPY . .

# Create a non-root user for security and switch to it
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Expose your application's port (change 7689 to match your framework)
EXPOSE 7689

# Specify the command to run your app (e.g., Uvicorn for FastAPI/Flask, or python main.py)
CMD ["python", "src/run.py"]

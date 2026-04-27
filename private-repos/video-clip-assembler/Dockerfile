FROM python:3.11-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY scripts/ scripts/
COPY static/ static/
COPY fonts/ fonts/

# Create temp directory
RUN mkdir -p temp/clips

# Environment
ENV HOST=0.0.0.0
ENV PORT=8765

EXPOSE 8765

CMD ["python", "scripts/server.py"]

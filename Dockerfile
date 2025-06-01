FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . .

# Create directories for volumes
RUN mkdir -p /app/input /app/output

# Set volumes
VOLUME ["/app/input", "/app/output"]

# Command to run when container starts
CMD ["python", "main.py"]
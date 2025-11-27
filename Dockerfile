# Use a slim Python image
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Optional: Install system dependencies if needed (e.g. for some libraries)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#  && rm -rf /var/lib/apt/lists/*

# Create a non-root user (good practice)
RUN useradd -m botuser

WORKDIR /app

# Copy requirements first (better layer caching)
COPY requirements.txt /app/

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . /app

# Change ownership to non-root user
RUN chown -R botuser:botuser /app
USER botuser

# If you store sqlite DBs in /app/data, make sure it exists
RUN mkdir -p /app/data

# Default command to run your bot
# If your entry file is not bot.py, change it here
CMD ["python", "bot.py"]

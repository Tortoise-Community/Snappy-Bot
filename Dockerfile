FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Optional: Install system dependencies if needed (e.g. for some libraries)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#  && rm -rf /var/lib/apt/lists/*

RUN useradd -m botuser

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN chown -R botuser:botuser /app
USER botuser

RUN mkdir -p /app/data

CMD ["python", "bot.py"]

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libgl1 \
    libsdl2-dev \
    libsdl2-ttf-dev \
    libsdl2-image-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app/ /app/
COPY roms/ /roms/

RUN mkdir -p /app/saves

EXPOSE 8080

CMD ["python", "server.py"]
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY main.py /app/main.py

# Instala dependencias del sistema para SpeechRecognition
RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn pydantic SpeechRecognition

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
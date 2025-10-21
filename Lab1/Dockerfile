FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY server.py .
COPY client.py .

EXPOSE 8080

CMD ["python", "server.py"]

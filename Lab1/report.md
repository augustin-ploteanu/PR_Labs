# Laboratory 1 Report

## Source Directory Structure

![img1](Lab1/screenshots/img1.png)

---

## Docker Configuration

### Dockerfile

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY server.py .
COPY client.py .

EXPOSE 8080

CMD ["python", "server.py"]
```

### docker-compose.yml

```yaml
version: "3.9"
services:
  server:
    build: .
    container_name: file_server
    volumes:
      - ./content:/srv/content
    ports:
      - "8080:8080"

  client:
    build: .
    container_name: file_client
    volumes:
      - ./downloads:/app/downloads
    command: ["python", "client.py", "server", "8080", "/", "/app/downloads"]
```

---

## Starting the Container

Build and start the server container:

```bash
docker compose build
docker compose up -d server
```

The server container executes:

```bash
python server.py /srv/content --port 8080
```

---

## Contents of the Served Directory

![img2](Lab1/screenshots/img2.png)

![img3](Lab1/screenshots/img3.png)

---

## Requests

Nonexistent file:

![img4](Lab1/screenshots/img4.png)

PNG file:

![img5](Lab1/screenshots/img5.png)

PDF file:

![img6](Lab1/screenshots/img6.png)

HTML page with image:

![img7](Lab1/screenshots/img7.png)

Logs:

![img8](Lab1/screenshots/img8.png)

---

## Using the Client

Directory listing generated page:

![img9](Lab1/screenshots/img9.png)

Subirectory listing generated page:

![img10](Lab1/screenshots/img10.png)

Downloading a file:

![img11](Lab1/screenshots/img11.png)

---

##  Subdirectory listing page

![img12](Lab1/screenshots/img12.png)
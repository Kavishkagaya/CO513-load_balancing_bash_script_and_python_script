FROM ubuntu:22.04

RUN apt update && apt install -y python3

WORKDIR /app
COPY server.py /app/

CMD ["python3", "/app/server.py"]
FROM ubuntu:22.04

RUN apt update && apt install -y bash curl

WORKDIR /app
COPY client.sh /app/

RUN chmod +x /app/client.sh

CMD ["/app/client.sh"]
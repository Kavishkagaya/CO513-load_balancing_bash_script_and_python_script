FROM ubuntu:22.04

RUN apt update && apt install -y bash socat iputils-ping bc

WORKDIR /app
COPY load_balancer.sh /app/

RUN chmod +x /app/*

CMD ["/app/load_balancer.sh"]
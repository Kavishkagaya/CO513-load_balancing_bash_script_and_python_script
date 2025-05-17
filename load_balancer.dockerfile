FROM ubuntu:22.04

RUN apt update && apt install -y python3 bash iperf3 dnsutils iputils-ping bc net-tools

WORKDIR /app
COPY load_balancer.sh /app/

RUN chmod +x /app/*

CMD ["/app/load_balancer.sh"]
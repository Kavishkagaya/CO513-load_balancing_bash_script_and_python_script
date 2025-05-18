FROM ubuntu:22.04

RUN apt update && apt install -y bash python3 iputils-ping

WORKDIR /app
COPY load_balance.py /app/

CMD ["python3", "/app/load_balance.py"]
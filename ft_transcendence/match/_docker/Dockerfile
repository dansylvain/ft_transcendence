FROM python:3.11-slim

RUN apt update -y && \ 
	apt upgrade -y && \
	apt install curl -y

WORKDIR /app

COPY _docker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x _docker/entrypoint.sh

ENTRYPOINT ["/bin/sh", "_docker/entrypoint.sh"]
FROM python:3.11-slim

RUN apt update -y && \ 
	apt upgrade -y && \
	apt install curl -y

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

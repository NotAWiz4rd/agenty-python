FROM python:3.12-alpine

RUN apk add bind-tools git
WORKDIR /app

COPY ../agent /app
COPY ../docker/agent.run.sh /app
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x agent.run.sh

EXPOSE 8000
ENTRYPOINT ["sh", "agent.run.sh"]

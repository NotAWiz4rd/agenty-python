FROM python:3.12-alpine

WORKDIR /app

COPY ../oversight_officer /app
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x main.py

EXPOSE 8000
ENTRYPOINT ["python", "-u", "main.py", "--port", "8000"]

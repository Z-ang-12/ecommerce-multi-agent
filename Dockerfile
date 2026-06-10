FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY api_server.py .

EXPOSE 8000

CMD ["python", "api_server.py"]
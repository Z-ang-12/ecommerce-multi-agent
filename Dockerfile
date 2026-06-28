FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# 复制所有必要的代码文件和目录
COPY api_server.py .
COPY dependencies.py .
COPY auth.py .
COPY multimodal_agent.py .
COPY static/ static/

EXPOSE 8000

CMD ["python", "api_server.py"]
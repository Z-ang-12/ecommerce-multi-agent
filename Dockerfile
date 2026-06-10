FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim

WORKDIR /app

# 设置镜像源为阿里云，加速后续可能的包安装
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 复制你的 Python 第三方依赖库（跳过标准库，只复制第三方包）
COPY python-runtime/Lib/site-packages /usr/local/lib/python3.11/site-packages

# 复制项目代码
COPY api_server.py .

EXPOSE 8000

CMD ["python", "api_server.py"]
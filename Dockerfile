
#设置官方python镜像
FROM python:3.11-slim

#设置工作目录
WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple


COPY . .

CMD ["python", "app.py"]
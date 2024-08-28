FROM python:3.12-slim
WORKDIR /app
# 先只拷贝 requirements.txt 以利用缓存
COPY requirements.txt /requirements.txt

COPY . /app
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["python", "app/main.py"]
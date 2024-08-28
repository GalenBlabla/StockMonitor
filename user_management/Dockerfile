FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 先只拷贝 requirements.txt 以利用缓存
COPY requirements.txt /app/requirements.txt

# 安装依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 然后拷贝剩余的应用代码
COPY . /app

# 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

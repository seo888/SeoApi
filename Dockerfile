# 使用官方 Python 镜像作为基础镜像
FROM python:3.14.2-slim

# 设置工作目录
WORKDIR /app

# 将依赖文件复制到容器中
COPY requirements.txt requirements.txt

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 将当前目录内容复制到容器中
COPY . .

# ARG VERSION=$(cat VERSION)

# ENV APP_VERSION=${VERSION}

# 暴露 Sanic 的默认端口
EXPOSE 17888

# 设置容器启动时的默认命令
CMD ["python", "main.py"]
#!/bin/bash

cd /www

# 检查是否已经存在 "SeoApi" 目录
if [ -d "SeoApi" ]; then
  echo "目录 'SeoApi' 存在，开始更新"
else
  echo "目录 'SeoApi' 不存在，请先安装程序。"
  exit 0
  # 在这里添加你需要执行的命令
fi

# 安装 jq 和 tar，如果它们尚未安装
if command -v yum &>/dev/null; then
  echo "CentOS系统"
  yum install -y jq tar
else
  echo "Debian/Ubuntu系统"
  apt install -y jq tar
fi

# 从 GitHub API 获取最新的发布信息
RELEASE_JSON=$(curl -s https://api.github.com/repos/seo888/SeoApi/releases/latest)

# 从 JSON 响应中提取 tarball URL
TAR_URL=$(echo "$RELEASE_JSON" | jq -r .tarball_url)

# 检查 TAR URL 是否为空
if [ -z "$TAR_URL" ]; then
  echo "从 GitHub API 获取 TAR URL 失败"
  exit 1
fi

# 定义基于版本标签的输出 tar 文件名
TAR_FILE="SeoApi-$(echo "$RELEASE_JSON" | jq -r .tag_name).tar.gz"

TARGET_DIR="SeoApi_New"

# 使用 curl 下载 tarball
echo "从 $TAR_URL 下载发布版本..."
curl -L -o "$TAR_FILE" "$TAR_URL"

# 检查下载是否成功
if [ $? -eq 0 ]; then
  echo "下载成功！"
else
  echo "下载失败！"
  exit 1
fi

# 检查文件是否存在
# if [ ! -f "$TAR_FILE" ]; then
#   echo "错误：文件 $TAR_FILE 不存在"
#   exit 1
# fi

rm -rf "$TARGET_DIR"

# 创建目标目录
mkdir -p "$TARGET_DIR"

# 尝试不同解压方式
if tar --help | grep -q "one-top-level"; then
  # 支持新语法
  tar -xzf "$TAR_FILE" --one-top-level="$TARGET_DIR" --strip-components=1
else
  # 传统方式
  TEMP_DIR=$(mktemp -d)
  tar -xzf "$TAR_FILE" -C "$TEMP_DIR" --strip-components=1
  mv "$TEMP_DIR"/* "$TARGET_DIR"/
  rm -rf "$TEMP_DIR"
fi

# 检查结果
if [ $? -eq 0 ]; then
  echo "解压成功到 $TARGET_DIR/"
  rm -f "$TAR_FILE"
else
  echo "解压失败！"
  exit 1
fi

echo "'镜像精灵 SeoApi $(echo "$RELEASE_JSON" | jq -r .tag_name) 下载成功'"

new="/www/SeoApi_New/app/SeoApi"
old="/www/SeoApi/app/SeoApi"
mv -f "$new" "$old"

new="/www/SeoApi_New/docker-compose.yml"
old="/www/SeoApi/docker-compose.yml"
mv -f "$new" "$old"

new="/www/SeoApi_New/update.sh"
old="/www/SeoApi/update.sh"
mv -f "$new" "$old"

# new="/www/SeoApi_New/app/_"
# old="/www/SeoApi/app/_"
# # 确保目标目录存在
# if [ -d "$old" ]; then
#     rm -rf "$old"/*  # 删除目标目录中的所有内容
# fi
# # 使用 cp 命令复制新目录的内容到目标目录
# cp -r "$new"/* "$old"/

new="/www/SeoApi_New/app/_"
old="/www/SeoApi/app/_"
backup_dir="/tmp/js_backup" # 临时备份目录

# 1. 备份原 js 目录
if [ -d "$old/static/js" ]; then
  mkdir -p "$backup_dir"
  cp -r "$old/static/js" "$backup_dir/"
fi

# 2. 完全清空目标目录
if [ -d "$old" ]; then
  find "$old" -mindepth 1 -delete
fi

# 3. 复制新内容
cp -r "$new"/* "$old/"

# 4. 恢复原 js 目录
if [ -d "$backup_dir/js" ]; then
  mkdir -p "$old/static/"
  cp -r "$backup_dir/js" "$old/static/"
  rm -rf "$backup_dir" # 清理备份
fi

PROJECT_DIR="/www/SeoApi"
# 切换到项目目录
cd "$PROJECT_DIR" || exit 1

# 检查并创建 postgres_data 目录（如果不存在）
POSTGRES_DATA_DIR="/www/SeoApi/data/postgres_data"
if [ ! -d "$POSTGRES_DATA_DIR" ]; then
  echo "创建 PostgreSQL 数据目录: $POSTGRES_DATA_DIR"
  mkdir -p "$POSTGRES_DATA_DIR"
  # 设置权限为 PostgreSQL 用户（UID 999）
  chown 999:999 "$POSTGRES_DATA_DIR"
  chmod 700 "$POSTGRES_DATA_DIR"
fi

# 清理临时文件
rm -f /tmp/temp_replacement.txt

# 重启容器
docker compose down && docker compose up -d || exit 1

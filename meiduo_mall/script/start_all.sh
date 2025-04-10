##!/bin/bash
#
## 启动前端服务
#cd /home/B2Cproject/front_end_pc  # 前端项目目录
#python3 -m http.server 8080 &
#
## 启动 Django 服务
#cd /home/B2Cproject/meiduo_mall  # Django 项目目录
#python3 manage.py runserver 0.0.0.0:8000 &
#
## 启动 Celery 服务
#cd /home/B2Cproject/meiduo_mall  # Celery 项目目录
#celery -A celery_tasks worker -l INFO
#
#
## 启动 Docker 容器
#docker start tracker &
#docker start storge &

#!/bin/bash
# 检查并启动前端服务
if ! lsof -i :8080 > /dev/null; then
    echo "Starting frontend server..."
    cd /home/B2Cproject/front_end_pc  # 前端项目目录
    python3 -m http.server 8080
else
    echo "Frontend server is already running."
fi

# 检查并启动 Celery
if ! pgrep -f "celery worker" > /dev/null; then
    echo "Starting Celery..."
    cd /home/B2Cproject/meiduo_mall  # Celery 项目目录
    celery -A celery_tasks worker -l INFO &
else
    echo "Celery is already running."
fi

# 检查并启动 Tracker 容器
if ! docker ps --filter "name=tracker" --filter "status=up" -q; then
    echo "Starting Tracker container..."
    docker start tracker
else
    echo "Tracker container is already running."
fi

# 检查并启动 Storage 容器
if ! docker ps --filter "name=storge" --filter "status=up" -q; then
    echo "Starting Storage container..."
    docker start storge
else
    echo "Storge container is already running."
fi


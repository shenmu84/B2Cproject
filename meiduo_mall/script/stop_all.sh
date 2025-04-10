#!/bin/bash

# 停止前端服务（通过找到对应的进程并杀掉）
echo "Stopping frontend server..."
if lsof -i :8080 > /dev/null; then
    # 停止前端服务器的进程
    kill $(lsof -t -i :8080)
    echo "Frontend server stopped."
else
    echo "Frontend server is not running."
fi

# 停止 Celery Worker
echo "Stopping Celery..."
if pgrep -f "celery worker" > /dev/null; then
    # 停止 Celery worker
    pkill -f "celery worker"
    echo "Celery stopped."
else
    echo "Celery is not running."
fi

# 停止 Tracker 容器
echo "Stopping Tracker container..."
if docker ps --filter "name=tracker" --filter "status=up" -q; then
    # 停止 Tracker 容器
    docker stop tracker
    echo "Tracker container stopped."
else
    echo "Tracker container is not running."
fi

# 停止 Storage 容器
echo "Stopping Storage container..."
if docker ps --filter "name=storge" --filter "status=up" -q; then
    # 停止 Storage 容器
    docker stop storge
    echo "Storge container stopped."
else
    echo "Storge container is not running."
fi

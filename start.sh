#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
JAVA_HOME="${JAVA_HOME:-/Users/zhengfeifei/Library/Java/JavaVirtualMachines/corretto-17.0.8/Contents/Home}"

echo "=== AI电商客服系统 V2 启动脚本 ==="

if ! command -v java &> /dev/null; then
    echo "错误: 未找到Java，请安装JDK 17+"
    exit 1
fi

if ! command -v mvn &> /dev/null && ! command -v ./mvnw &> /dev/null; then
    echo "错误: 未找到Maven"
    exit 1
fi

echo "[1/3] 启动Java Mock服务..."
cd "$PROJECT_DIR/mock-server"
JAVA_HOME="$JAVA_HOME" mvn spring-boot:run > "$PROJECT_DIR/.ai-dev/logs/mock-server.log" 2>&1 &
MOCK_PID=$!
echo "Java Mock服务 PID: $MOCK_PID"

echo "[2/3] 等待Mock服务启动(30秒)..."
for i in $(seq 1 30); do
    if curl --noproxy '*' -s http://localhost:8080/api/products?page=0&size=1 > /dev/null 2>&1; then
        echo "Mock服务已启动!"
        break
    fi
    sleep 1
done

echo "[3/3] 启动Python服务..."
cd "$PROJECT_DIR"
python3 main.py &
PYTHON_PID=$!
echo "Python服务 PID: $PYTHON_PID"

cleanup() {
    echo "正在停止服务..."
    kill $MOCK_PID 2>/dev/null || true
    kill $PYTHON_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

echo ""
echo "=== 服务已启动 ==="
echo "Java Mock: http://localhost:8080"
echo "Python UI: http://127.0.0.1:7860"
echo "按Ctrl+C停止所有服务"
echo ""

wait

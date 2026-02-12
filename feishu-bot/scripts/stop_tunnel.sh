#!/bin/bash
# Cloudflare 隧道停止脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$SKILL_DIR/tunnel.pid"

echo "========================================"
echo "  Cloudflare 隧道 - 停止"
echo "========================================"
echo ""

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  未找到隧道 PID 文件"
    echo "   尝试查找运行中的隧道..."

    # 尝试查找并停止所有 cloudflared 进程
    PIDS=$(pgrep -f "cloudflared tunnel")
    if [ -n "$PIDS" ]; then
        echo "   找到运行中的隧道进程: $PIDS"
        echo "$PIDS" | xargs kill
        echo "✓ 隧道已停止"
    else
        echo "   没有运行中的隧道"
    fi
    exit 0
fi

TUNNEL_PID=$(cat "$PID_FILE")

if ps -p "$TUNNEL_PID" > /dev/null 2>&1; then
    echo "✓ 停止隧道 (PID: $TUNNEL_PID)..."
    kill "$TUNNEL_PID"
    rm -f "$PID_FILE"
    echo "✓ 隧道已停止"
else
    echo "⚠️  隧道进程不存在 (PID: $TUNNEL_PID)"
    rm -f "$PID_FILE"
    echo "✓ 清理 PID 文件"
fi

echo ""
echo "提示: 使用 'start_tunnel.sh' 重新启动隧道"

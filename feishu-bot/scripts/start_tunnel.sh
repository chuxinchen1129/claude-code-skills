#!/bin/bash
# Cloudflare 隧道自动启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$SKILL_DIR/tunnel.pid"
URL_FILE="$SKILL_DIR/tunnel_url.txt"

echo "========================================"
echo "  Cloudflare 隧道 - 自动启动"
echo "========================================"
echo ""

# 检查是否已在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "✓ 隧道已在运行 (PID: $OLD_PID)"
        if [ -f "$URL_FILE" ]; then
            echo "✓ 公网地址: $(cat "$URL_FILE")"
        fi
        exit 0
    else
        echo "⚠️  清理旧的 PID 文件"
        rm -f "$PID_FILE"
    fi
fi

# 启动隧道
echo "✓ 正在启动 Cloudflare 隧道..."
echo ""

# 后台启动并捕获输出
/opt/homebrew/bin/cloudflared tunnel --url http://localhost:5001 > "$SKILL_DIR/tunnel.log" 2>&1 &
TUNNEL_PID=$!

# 保存 PID
echo "$TUNNEL_PID" > "$PID_FILE"

# 等待并提取 URL
echo "✓ 等待隧道启动..."
sleep 5

# 从日志中提取 URL
for i in {1..30}; do
    if [ -f "$SKILL_DIR/tunnel.log" ]; then
        URL=$(grep -o 'https://[^[:space:]]*\.trycloudflare\.com' "$SKILL_DIR/tunnel.log" | head -1)
        if [ -n "$URL" ]; then
            echo "$URL" > "$URL_FILE"
            echo ""
            echo "========================================"
            echo "  ✓ 隧道启动成功！"
            echo "========================================"
            echo ""
            echo "公网地址:"
            echo "  $URL"
            echo ""
            echo "Webhook URL:"
            echo "  $URL/webhook"
            echo ""
            echo "配置到飞书事件订阅:"
            echo "  1. 访问 https://open.feishu.cn/app"
            echo "  2. 进入你的应用 → 事件订阅"
            echo "  3. 设置 Request URL 为上述地址"
            echo ""
            echo "管理命令:"
            echo "  停止: kill $TUNNEL_PID"
            echo "  查看日志: tail -f $SKILL_DIR/tunnel.log"
            echo ""
            exit 0
        fi
    fi
    sleep 1
done

echo "❌ 无法获取隧道 URL"
exit 1

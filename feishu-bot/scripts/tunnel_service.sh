#!/bin/bash
# 永久隧道服务管理脚本
# 自动重启并跟踪地址变化

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$SKILL_DIR/tunnel.pid"
URL_FILE="$SKILL_DIR/tunnel_url.txt"
URL_HISTORY="$SKILL_DIR/tunnel_history.log"
WEBHOOK_CONFIG="$SKILL_DIR/last_webhook_url.txt"

show_url_change_notification() {
    local new_url="$1"
    local old_url="$2"

    if [ -n "$old_url" ] && [ "$new_url" != "$old_url" ]; then
        echo ""
        echo "========================================"
        echo "  ⚠️  隧道地址已变化！"
        echo "========================================"
        echo ""
        echo "旧地址: $old_url"
        echo "新地址: $new_url"
        echo ""
        echo "需要更新飞书配置："
        echo "  1. 访问: https://open.feishu.cn/app"
        echo "  2. 你的应用 → 事件订阅"
        echo "  3. 更新 Request URL 为:"
        echo "     $new_url/webhook"
        echo ""
        echo "========================================"
        echo ""

        # 记录到历史
        echo "$(date '+%Y-%m-%d %H:%M:%S') - $old_url -> $new_url" >> "$URL_HISTORY"

        # 保存为新地址
        echo "$new_url" > "$WEBHOOK_CONFIG"
    fi
}

start_tunnel() {
    echo "========================================"
    echo "  启动 Cloudflare 隧道"
    echo "========================================"
    echo ""

    # 读取旧地址
    OLD_URL=""
    if [ -f "$URL_FILE" ]; then
        OLD_URL=$(cat "$URL_FILE")
    fi

    # 检查是否已在运行
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            echo "⚠️  隧道已在运行 (PID: $OLD_PID)"
            if [ -f "$URL_FILE" ]; then
                echo "✓ 当前地址: $(cat "$URL_FILE")/webhook"
            fi
            exit 0
        else
            echo "⚠️  清理旧的 PID 文件"
            rm -f "$PID_FILE"
        fi
    fi

    # 停止现有的 cloudflared 进程
    pkill -f "cloudflared tunnel" 2>/dev/null || true
    sleep 2

    # 启动隧道
    echo "✓ 正在启动 Cloudflare 隧道..."
    /opt/homebrew/bin/cloudflared tunnel --url http://localhost:5001 \
        > "$SKILL_DIR/tunnel.log" 2>&1 &

    TUNNEL_PID=$!
    echo "$TUNNEL_PID" > "$PID_FILE"

    # 等待并提取 URL
    echo "✓ 等待隧道启动..."
    for i in {1..60}; do
        if [ -f "$SKILL_DIR/tunnel.log" ]; then
            NEW_URL=$(grep -o 'https://[^[:space:]]*\.trycloudflare\.com' "$SKILL_DIR/tunnel.log" 2>/dev/null | tail -1)
            if [ -n "$NEW_URL" ]; then
                echo "$NEW_URL" > "$URL_FILE"
                echo ""
                echo "========================================"
                echo "  ✓ 隧道启动成功！"
                echo "========================================"
                echo ""
                echo "Webhook URL:"
                echo "  $NEW_URL/webhook"
                echo ""
                echo "管理命令:"
                echo "  查看状态: $0 status"
                echo "  查看日志: $0 logs"
                echo "  停止隧道: $0 stop"
                echo ""

                # 检查地址是否变化
                show_url_change_notification "$NEW_URL" "$OLD_URL"

                exit 0
            fi
        fi
        sleep 1
    done

    echo "❌ 无法获取隧道 URL"
    echo "查看日志: $SKILL_DIR/tunnel.log"
    exit 1
}

stop_tunnel() {
    echo "========================================"
    echo "  停止 Cloudflare 隧道"
    echo "========================================"
    echo ""

    if [ -f "$PID_FILE" ]; then
        TUNNEL_PID=$(cat "$PID_FILE")
        if ps -p "$TUNNEL_PID" > /dev/null 2>&1; then
            echo "✓ 停止隧道 (PID: $TUNNEL_PID)..."
            kill "$TUNNEL_PID"
            rm -f "$PID_FILE"
            echo "✓ 隧道已停止"
        else
            echo "⚠️  隧道进程不存在"
            rm -f "$PID_FILE"
        fi
    else
        # 尝试找到并停止 cloudflared 进程
        PIDS=$(pgrep -f "cloudflared tunnel" || true)
        if [ -n "$PIDS" ]; then
            echo "✓ 停止运行中的隧道..."
            echo "$PIDS" | xargs kill
            echo "✓ 隧道已停止"
        else
            echo "⚠️  没有运行中的隧道"
        fi
    fi
}

show_status() {
    echo "========================================"
    echo "  Cloudflare 隧道状态"
    echo "========================================"
    echo ""

    # 检查进程
    if pgrep -f "cloudflared tunnel" > /dev/null; then
        echo "✓ 隧道状态: 运行中"
    else
        echo "✗ 隧道状态: 未运行"
    fi

    # 显示当前地址
    if [ -f "$URL_FILE" ]; then
        CURRENT_URL=$(cat "$URL_FILE")
        echo ""
        echo "当前地址:"
        echo "  $CURRENT_URL/webhook"
    fi

    # 显示地址历史
    if [ -f "$URL_HISTORY" ] && [ -s "$URL_HISTORY" ]; then
        echo ""
        echo "地址变更历史:"
        tail -5 "$URL_HISTORY" | while read line; do
            echo "  • $line"
        done
    fi

    echo ""
}

show_logs() {
    if [ -f "$SKILL_DIR/tunnel.log" ]; then
        tail -50 "$SKILL_DIR/tunnel.log"
    else
        echo "未找到隧道日志"
    fi
}

# 主程序
case "${1:-start}" in
    start)
        start_tunnel
        ;;
    stop)
        stop_tunnel
        ;;
    restart)
        stop_tunnel
        sleep 2
        start_tunnel
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Cloudflare 隧道服务管理"
        echo ""
        echo "用法: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "命令:"
        echo "  start   - 启动隧道"
        echo "  stop    - 停止隧道"
        echo "  restart - 重启隧道"
        echo "  status  - 查看状态"
        echo "  logs    - 查看日志"
        exit 1
        ;;
esac

#!/bin/bash
# 飞书机器人管理脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$1" in
    start)
        echo "启动机器人服务..."
        cd "$SCRIPT_DIR"
        python3 bot_server.py
        ;;
    stop)
        echo "停止机器人服务..."
        pkill -f bot_server.py
        echo "✓ 服务已停止"
        ;;
    restart)
        echo "重启机器人服务..."
        pkill -f bot_server.py
        sleep 2
        cd "$SCRIPT_DIR"
        nohup python3 bot_server.py > /tmp/feishu_bot.log 2>&1 &
        echo "✓ 服务已重启"
        ;;
    status)
        echo "=== 服务状态 ==="
        if pgrep -f bot_server.py > /dev/null; then
            echo "✓ 机器人服务: 运行中 (localhost:5001)"
            curl -s http://localhost:5001/ | python3 -m json.tool 2>/dev/null || echo "  API 响应异常"
        else
            echo "✗ 机器人服务: 未运行"
        fi

        if pgrep -f cloudflared > /dev/null; then
            echo "✓ Cloudflare 隧道: 运行中"
            # 显示隧道地址
            SKILL_DIR="$(dirname "$SCRIPT_DIR")"
            if [ -f "$SKILL_DIR/tunnel_url.txt" ]; then
                echo "  公网地址: $(cat "$SKILL_DIR/tunnel_url.txt")/webhook"
            fi
        else
            echo "✗ Cloudflare 隧道: 未运行"
        fi
        ;;
    logs)
        echo "=== 机器人日志 ==="
        tail -50 /tmp/feishu_bot.log
        ;;
    tunnel)
        echo "启动 Cloudflare 隧道..."
        "$SCRIPT_DIR/tunnel_service.sh" start
        ;;
    tunnel-stop)
        echo "停止 Cloudflare 隧道..."
        "$SCRIPT_DIR/tunnel_service.sh" stop
        ;;
    tunnel-logs)
        echo "=== 隧道日志 ==="
        "$SCRIPT_DIR/tunnel_service.sh" logs
        ;;
    *)
        echo "飞书机器人管理脚本"
        echo ""
        echo "用法: $0 {start|stop|restart|status|logs|tunnel|tunnel-stop|tunnel-logs}"
        echo ""
        echo "命令:"
        echo "  start       - 启动机器人服务"
        echo "  stop        - 停止机器人服务"
        echo "  restart     - 重启机器人服务"
        echo "  status      - 查看服务状态"
        echo "  logs        - 查看机器人日志"
        echo "  tunnel      - 启动 Cloudflare 隧道"
        echo "  tunnel-stop - 停止 Cloudflare 隧道"
        echo "  tunnel-logs - 查看隧道日志"
        exit 1
        ;;
esac

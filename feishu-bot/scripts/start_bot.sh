#!/bin/bash
# 飞书交互机器人启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "  飞书交互机器人 - 启动脚本"
echo "========================================"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

# 检查 Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask 未安装，正在安装..."
    pip3 install flask pyyaml
fi

# 检查配置文件
CONFIG_FILE="$SKILL_DIR/config/bot_config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 检查是否有 App ID
if ! grep -q 'app_id: "[^"]' "$CONFIG_FILE"; then
    echo "⚠️  警告: 未配置飞书 App ID"
    echo "   请编辑配置文件: $CONFIG_FILE"
    echo ""
    read -p "是否继续启动？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 启动服务器
echo "✓ 正在启动飞书机器人服务器..."
echo ""
cd "$SCRIPT_DIR"
python3 bot_server.py

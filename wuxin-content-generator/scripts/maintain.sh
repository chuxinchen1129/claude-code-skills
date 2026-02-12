#!/bin/bash
# 小红书关键词维护脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "$1" in
    "convert")
        echo "🔄 转换Markdown到JSON..."
        python3 scripts/convert_xiaohongshu_keywords.py
        ;;
    "validate")
        echo "✅ 验证JSON格式..."
        python3 -m json.tool assets/xiaohongshu_keywords.json > /dev/null
        if [ $? -eq 0 ]; then
            echo "✅ JSON格式正确"
        else
            echo "❌ JSON格式错误"
        fi
        ;;
    "stats")
        echo "📊 关键词统计:"
        python3 - <<'PYTHON'
import json
import os
json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../assets/xiaohongshu_keywords.json')
with open(json_path, 'r') as f:
    data = json.load(f)
print(f'  版本: {data["version"]}')
print(f'  Top关键词: {data["top_keywords_count"]}条')
print(f'  总关键词: {data["total_keywords"]}条')
print(f'  内容规划: {len(data["data"]["content_plans"])}条')
PYTHON
        ;;
    *)
        echo "用法: ./maintain.sh [command]"
        echo ""
        echo "命令:"
        echo "  convert  - 转换Markdown到JSON"
        echo "  validate - 验证JSON格式"
        echo "  stats    - 显示统计信息"
        ;;
esac

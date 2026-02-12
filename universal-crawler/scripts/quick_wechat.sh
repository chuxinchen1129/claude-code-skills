#!/bin/bash
# 微信公众号文章快速采集脚本

echo "=== 微信公众号文章快速采集 ==="
echo ""
echo "步骤 1: 获取文章链接"
echo "  1. 访问: https://weixin.sogou.com/"
echo "  2. 搜索关键词"
echo "  3. 复制文章链接"
echo ""

read -p "按 Enter 继续，或 Ctrl+C 退出..."

# 检查是否有链接文件
if [ ! -f "wechat_urls.txt" ]; then
    echo ""
    echo "请创建 wechat_urls.txt 文件，每行一个微信文章链接"
    echo "格式示例："
    echo "  https://mp.weixin.qq.com/s/xxxxx1"
    echo "  https://mp.weixin.qq.com/s/xxxxx2"
    echo ""
    echo "创建完成后重新运行此脚本"
    exit 1
fi

echo ""
echo "步骤 2: 批量爬取文章"
echo ""

# 计算链接数
total=$(wc -l < wechat_urls.txt)
echo "✓ 发现 $total 个链接"

# 调用 Universal Crawler
python3 ~/.claude/skills/universal-crawler/scripts/crawl.py \
  --urls wechat_urls.txt \
  --output "wechat_$(date +%Y%m%d).md"

echo ""
echo "✅ 采集完成！"
echo "📁 输出文件: wechat_$(date +%Y%m%d).md"

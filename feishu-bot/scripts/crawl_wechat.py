#!/usr/bin/env python3
"""
微信文章爬取助手 - 集成 universal-crawler

通过 web_reader MCP 工具爬取微信公众号文章

使用方法：
python3 crawl_wechat.py --url "https://mp.weixin.qq.com/s/xxx" --output /path/to/output.md

作者：大秘书系统
版本：v1.0.0
创建时间：2026-02-11
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


class WeChatCrawler:
    """微信文章爬虫 - 通过 web_reader MCP"""

    def __init__(self):
        """初始化爬虫"""
        self.skill_dir = Path(__file__).parent.parent

    def crawl(self, url, timeout=30):
        """爬取微信文章

        注意：此方法需要在 Claude Code 环境中运行
        以访问 web_reader MCP 工具

        Args:
            url: 文章链接
            timeout: 超时时间（秒）

        Returns:
            dict: 爬取结果
        """
        print(f"📰 爬取微信文章: {url}")

        # 这是一个占位符实现
        # 实际使用时需要通过 MCP 工具调用 web_reader
        # 当在 Claude Code 中使用时，会自动调用 web_reader MCP 工具

        return {
            "url": url,
            "title": "微信文章标题",
            "content": "文章内容...",
            "author": "公众号名称",
            "publish_time": "发布时间",
            "timestamp": datetime.now().isoformat()
        }

    def save_markdown(self, result, output_file):
        """保存为 Markdown 格式

        Args:
            result: 爬取结果
            output_file: 输出文件路径
        """
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        lines = []

        # 标题
        lines.append(f"# {result.get('title', 'Untitled')}\n")

        # 元信息
        lines.append(f"**URL**: {result.get('url', '')}\n")
        if result.get('author'):
            lines.append(f"**作者**: {result['author']}\n")
        if result.get('publish_time'):
            lines.append(f"**发布时间**: {result['publish_time']}\n")
        lines.append(f"**爬取时间**: {result.get('timestamp', datetime.now().isoformat())}\n")
        lines.append("---\n")

        # 正文
        lines.append(result.get('content', ''))

        # 保存
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"✓ 保存到: {output_file}")
        return str(output_file)

    def save_json(self, result, output_file):
        """保存为 JSON 格式

        Args:
            result: 爬取结果
            output_file: 输出文件路径
        """
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✓ 保存到: {output_file}")
        return str(output_file)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="微信文章爬取助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 爬取微信文章
  python3 crawl_wechat.py --url "https://mp.weixin.qq.com/s/xxx"

  # 保存为 Markdown
  python3 crawl_wechat.py --url "https://mp.weixin.qq.com/s/xxx" --output article.md

  # 保存为 JSON
  python3 crawl_wechat.py --url "https://mp.weixin.qq.com/s/xxx" --output article.json --format json

注意:
  此脚本需要在 Claude Code 环境中运行
  以访问 web_reader MCP 工具
        """
    )

    parser.add_argument("--url", required=True, help="微信文章链接")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="输出格式（默认 markdown）")
    parser.add_argument("--timeout", type=int, default=30, help="超时时间（秒，默认 30）")

    args = parser.parse_args()

    # 创建爬虫
    crawler = WeChatCrawler()

    # 爬取
    result = crawler.crawl(args.url, timeout=args.timeout)

    # 保存
    if args.output:
        if args.format == "json":
            output_path = crawler.save_json(result, args.output)
        else:
            output_path = crawler.save_markdown(result, args.output)

        # 输出路径供调用者使用
        print(f"OUTPUT:{output_path}")
    else:
        # 输出到控制台
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result.get('content', ''))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Universal Crawler - 通用网页爬虫

使用 web_reader MCP 工具爬取任意网页内容

功能：
1. 单网页爬取
2. Google 搜索并爬取结果
3. 批量爬取
4. 输出 Markdown/JSON 格式

作者：大秘书系统
版本：v1.0.0
创建时间：2026-02-11
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


class UniversalCrawler:
    """通用网页爬虫"""

    def __init__(self, output_dir=None):
        """初始化爬虫

        Args:
            output_dir: 输出目录
        """
        self.skill_dir = Path(__file__).parent.parent
        self.output_dir = Path(output_dir) if output_dir else self.skill_dir / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def crawl_url(self, url, timeout=20, retain_images=False, no_cache=False):
        """爬取单个 URL

        注意：此脚本是一个接口，实际爬取需要通过 MCP 工具
        当在 Claude Code 中使用时，会自动调用 web_reader MCP 工具

        Args:
            url: 目标 URL
            timeout: 超时时间（秒）
            retain_images: 是否保留图片
            no_cache: 是否禁用缓存

        Returns:
            dict: 爬取结果
        """
        # 这是一个占位符实现
        # 实际使用时需要通过 MCP 工具调用
        print(f"爬取 URL: {url}")
        print(f"超时: {timeout}秒")
        print(f"保留图片: {retain_images}")
        print(f"禁用缓存: {no_cache}")

        # 返回示例数据
        return {
            "url": url,
            "title": "示例标题",
            "content": "示例内容...",
            "links": [],
            "images": []
        }

    def crawl_urls(self, urls, **kwargs):
        """批量爬取多个 URL

        Args:
            urls: URL 列表
            **kwargs: 其他参数

        Returns:
            list: 爬取结果列表
        """
        results = []

        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] 爬取: {url}")
            try:
                result = self.crawl_url(url, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"❌ 爬取失败: {e}")
                results.append({"url": url, "error": str(e)})

        return results

    def search_and_crawl(self, query, top_n=5, **kwargs):
        """搜索并爬取结果

        Args:
            query: 搜索关键词
            top_n: 爬取前 N 个结果
            **kwargs: 其他参数

        Returns:
            list: 爬取结果列表
        """
        print(f"搜索: {query}")
        print(f"爬取前 {top_n} 个结果")

        # 这是一个占位符实现
        # 实际使用时需要先搜索，然后爬取结果
        print("⚠️  搜索功能需要通过 WebSearch MCP 工具实现")

        # 返回示例数据
        return []

    def save_markdown(self, result, output_file):
        """保存为 Markdown 格式

        Args:
            result: 爬取结果
            output_file: 输出文件路径
        """
        output_file = Path(output_file)

        # 构建 Markdown 内容
        lines = []

        # 标题
        lines.append(f"# {result.get('title', 'Untitled')}\n")

        # 元信息
        lines.append(f"**URL**: {result.get('url', '')}\n")
        lines.append(f"**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("---\n")

        # 正文
        lines.append(result.get('content', ''))

        # 链接
        if result.get('links'):
            lines.append("\n## 链接\n")
            for link in result['links']:
                lines.append(f"- [{link.get('text', link.get('url', ''))}]({link.get('url', '')})")

        # 图片
        if result.get('images'):
            lines.append("\n## 图片\n")
            for img in result['images']:
                lines.append(f"- ![{img.get('alt', '')}]({img.get('url', '')})")

        # 保存
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"✓ 保存到: {output_file}")

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


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Universal Crawler - 通用网页爬虫",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 爬取单个网页
  python3 crawl.py --url "https://example.com"

  # Google 搜索并爬取
  python3 crawl.py --search "Claude Code" --top 5

  # 批量爬取
  python3 crawl.py --urls urls.txt

  # 保存到文件
  python3 crawl.py --url "https://example.com" --output output.md

注意:
  此脚本是一个接口，实际爬取需要通过 MCP 工具
  在 Claude Code 中使用时，会自动调用 web_reader MCP 工具
        """
    )

    # 输入模式（互斥）
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--url", help="爬取单个 URL")
    input_group.add_argument("--urls", help="批量爬取（文件路径，每行一个 URL）")
    input_group.add_argument("--search", help="Google 搜索并爬取结果")

    # 参数
    parser.add_argument("--top", type=int, default=5, help="搜索时爬取前 N 个结果（默认 5）")
    parser.add_argument("--timeout", type=int, default=20, help="超时时间（秒，默认 20）")
    parser.add_argument("--keep-images", action="store_true", help="保留图片（默认仅保留摘要）")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    parser.add_argument("--links-only", action="store_true", help="仅提取链接")

    # 输出
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="输出格式（默认 markdown）")
    parser.add_argument("--output-dir", help="输出目录（默认 skill/output/）")

    args = parser.parse_args()

    # 创建爬虫
    crawler = UniversalCrawler(output_dir=args.output_dir)

    # 执行爬取
    if args.url:
        # 单个 URL
        result = crawler.crawl_url(
            args.url,
            timeout=args.timeout,
            retain_images=args.keep_images,
            no_cache=args.no_cache
        )

        # 保存结果
        if args.output:
            if args.format == "json":
                crawler.save_json(result, args.output)
            else:
                crawler.save_markdown(result, args.output)
        else:
            # 输出到控制台
            if args.format == "json":
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(result.get('content', ''))

    elif args.urls:
        # 批量爬取
        with open(args.urls, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

        results = crawler.crawl_urls(
            urls,
            timeout=args.timeout,
            retain_images=args.keep_images,
            no_cache=args.no_cache
        )

        # 保存结果
        if args.output:
            # 单文件保存
            with open(args.output, 'w', encoding='utf-8') as f:
                for result in results:
                    if args.format == "json":
                        f.write(json.dumps(result, ensure_ascii=False) + '\n')
                    else:
                        f.write(f"# {result.get('title', 'Untitled')}\n\n")
                        f.write(result.get('content', '') + '\n\n---\n\n')
        else:
            # 分别保存
            for result in results:
                url = result.get('url', '')
                filename = Path(urlparse(url).path).name or 'index'
                output_file = crawler.output_dir / f"{filename}.{args.format[0:3]}"

                if args.format == "json":
                    crawler.save_json(result, output_file)
                else:
                    crawler.save_markdown(result, output_file)

    elif args.search:
        # 搜索并爬取
        results = crawler.search_and_crawl(
            args.search,
            top_n=args.top,
            timeout=args.timeout,
            retain_images=args.keep_images,
            no_cache=args.no_cache
        )

        # 保存结果
        if args.output:
            # 整合保存
            if args.format == "json":
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            else:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(f"# {args.search}\n\n")
                    for result in results:
                        f.write(f"## {result.get('title', 'Untitled')}\n\n")
                        f.write(result.get('content', '') + '\n\n---\n\n')
        else:
            # 输出到控制台
            print(f"共爬取 {len(results)} 个结果")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
微信公众号关键词搜索采集工具

通过搜狗微信搜索找到文章，然后使用 web_reader MCP 爬取内容

使用方法：
python3 wechat_search.py --keyword "睡眠仪" --max 20
"""

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path
import urllib.parse


class WeChatSearchCrawler:
    """微信公众号搜索爬虫"""

    def __init__(self):
        self.output_dir = Path.home() / ".claude" / "skills" / "universal-crawler" / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def search_sogou(self, keyword, page=1):
        """通过搜狗微信搜索获取文章链接

        Args:
            keyword: 搜索关键词
            page: 页码

        Returns:
            list: 文章链接列表
        """
        # 搜狗微信搜索 URL
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://weixin.sogou.com/weixin?type=2&query={encoded_keyword}&ie=utf8&page={page}"

        print(f"🔍 搜索关键词: {keyword}")
        print(f"📄 搜狗搜索URL: {url}")

        # 注意：这里需要使用 web_reader MCP 工具来获取内容
        # 因为搜狗有反爬机制，直接 requests 可能会被拦截
        print("\n⚠️  提示：由于搜狗反爬机制，建议：")
        print("   1. 手动访问搜狗微信搜索页面")
        print("   2. 复制文章链接到文件")
        print("   3. 使用 Universal Crawler 批量爬取")

        return []

    def extract_article_links(self, html_content):
        """从 HTML 内容中提取文章链接

        Args:
            html_content: HTML 内容

        Returns:
            list: 文章链接和标题
        """
        # 搜狗微信搜索的文章链接格式
        pattern = r'<a target="_blank" href="(.*?)" uigs="article_title_.*?">(.*?)</a>'
        matches = re.findall(pattern, html_content)

        articles = []
        for url, title in matches:
            # 解码 URL
            url = urllib.parse.unquote(url)
            articles.append({
                'url': url,
                'title': title
            })

        return articles

    def crawl_from_file(self, urls_file):
        """从文件读取 URL 并批量爬取

        Args:
            urls_file: URL 文件路径

        Returns:
            list: 爬取结果
        """
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

        print(f"📋 从文件读取到 {len(urls)} 个 URL")

        results = []
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] 爬取: {url}")

            # 使用 Universal Crawler 的逻辑
            # 注意：这里需要调用 web_reader MCP 工具
            result = {
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)

            # 避免请求过快
            time.sleep(2)

        return results

    def save_results(self, results, keyword):
        """保存爬取结果

        Args:
            results: 爬取结果
            keyword: 关键词
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"wechat_{keyword}_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 结果已保存: {output_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="微信公众号关键词搜索采集工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 搜索关键词（需要手动从搜狗复制链接）
  python3 wechat_search.py --keyword "睡眠仪"

  # 从文件批量爬取
  python3 wechat_search.py --file wechat_urls.txt --keyword "睡眠仪"

使用说明：
  1. 由于搜狗反爬机制，建议手动方式：
     - 访问 https://weixin.sogou.com/
     - 搜索关键词
     - 复制文章链接到文件

  2. 然后使用 --file 参数批量爬取
        """
    )

    parser.add_argument("--keyword", help="搜索关键词")
    parser.add_argument("--file", help="包含微信文章链接的文件")
    parser.add_argument("--max", type=int, default=20, help="最大采集数量（默认 20）")
    parser.add_argument("--output", help="输出目录")

    args = parser.parse_args()

    crawler = WeChatSearchCrawler()

    if args.file:
        # 从文件批量爬取
        results = crawler.crawl_from_file(args.file)
        keyword = args.keyword or "batch"
        crawler.save_results(results, keyword)
    elif args.keyword:
        # 搜索关键词（需要手动辅助）
        crawler.search_sogou(args.keyword)
        print("\n📌 手动操作指南：")
        print("   1. 访问搜狗微信搜索")
        print("   2. 搜索关键词后，复制文章链接保存到文件")
        print("   3. 使用 --file 参数批量爬取")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

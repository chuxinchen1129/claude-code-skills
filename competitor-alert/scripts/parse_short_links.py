#!/usr/bin/env python3
"""
小红书短链接解析脚本

功能：
1. 解析小红书短链接（xhslink.com）
2. 提取笔记ID和完整URL
3. 输出可用于 MediaCrawler 的格式

使用方式：
- 直接提供短链接列表
- 从文件读取链接
- 从混合文本中提取链接

作者：大秘书系统
版本：v1.0
创建时间：2026-02-11
"""

import requests
import re
import json
import argparse
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path


class ShortLinkParser:
    """小红书短链接解析器"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
        }

    def parse_single_link(self, url):
        """
        解析单个短链接

        Args:
            url: 短链接或完整链接

        Returns:
            dict: 解析结果，包含 short_url, long_url, note_id, status
        """
        result = {
            'short_url': url,
            'long_url': '',
            'note_id': '',
            'status': 'unknown',
            'error': None
        }

        try:
            # 方法1: 不跟随重定向，获取 Location 头
            # 注意：xhslink.com 必须使用 GET 请求，HEAD 返回 404
            response = requests.get(url, headers=self.headers, allow_redirects=False, timeout=10)

            if response.status_code in [301, 302, 303, 307, 308]:
                # 从 Location 头获取完整 URL
                long_url = response.headers.get('Location', '')

                # 检查是否成功解析
                if self._is_valid_xhs_url(long_url):
                    result['long_url'] = long_url
                    result['note_id'] = self._extract_note_id(long_url)
                    result['status'] = 'success'
                else:
                    # 可能是错误页面
                    result['status'] = 'error'
                    result['error'] = 'Redirected to error page'
            elif response.status_code == 200:
                # 没有重定向，直接使用当前 URL
                long_url = response.url
                result['long_url'] = long_url
                result['note_id'] = self._extract_note_id(long_url)
                result['status'] = 'success'
            else:
                result['status'] = 'error'
                result['error'] = f'HTTP {response.status_code}'

        except requests.Timeout:
            result['status'] = 'error'
            result['error'] = 'Timeout'
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)[:100]

        return result

    def _is_valid_xhs_url(self, url):
        """检查是否是有效的小红书 URL"""
        # 排除错误页面
        if 'login' in url or 'error' in url or '404' in url:
            return False

        # 检查是否包含 xiaohongshu.com
        if 'xiaohongshu.com' not in url:
            return False

        return True

    def _extract_note_id(self, url):
        """
        从 URL 中提取笔记ID

        支持多种 URL 格式：
        1. 标准格式：/explore/{note_id}
        2. 登录重定向：redirectPath 包含 /explore/{note_id}
        3. 错误页面：noteId={note_id}
        """
        # 方法1: 直接从 URL 路径中提取 /explore/{note_id} 或 /discovery/item/{note_id}
        path_match = re.search(r'/(?:explore|discovery/item)/([a-f0-9]{24})', url)
        if path_match:
            return path_match.group(1)

        # 方法2: 解析 URL 参数
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            # 检查 redirectPath 参数（需要 URL 解码）
            if 'redirectPath' in params:
                redirect_path = params['redirectPath'][0]
                # URL 解码
                redirect_path = unquote(redirect_path)
                # 从 redirectPath 中提取 note_id
                redirect_match = re.search(r'/explore/([a-f0-9]{24})', redirect_path)
                if redirect_match:
                    return redirect_match.group(1)

            # 检查 noteId 参数
            if 'noteId' in params:
                note_id = params['noteId'][0]
                # 过滤掉错误页面的 noteId=page，只接受 24 位十六进制 ID
                if re.match(r'^[a-f0-9]{24}$', note_id):
                    return note_id

            # 检查所有参数值中的 note_id 模式
            for key, values in params.items():
                for value in values:
                    match = re.search(r'noteId(?:=|_)?([a-f0-9]{24})', value)
                    if match:
                        return match.group(1)

        except Exception:
            pass

        return None

    def parse_links(self, links):
        """
        批量解析短链接

        Args:
            links: 链接列表

        Returns:
            list: 解析结果列表
        """
        results = []

        for i, link in enumerate(links, 1):
            print(f"[{i}/{len(links)}] 解析: {link[:60]}...")

            result = self.parse_single_link(link)

            if result['status'] == 'success':
                print(f"  ✓ 成功: {result['note_id']}")
            elif result['status'] == 'error':
                print(f"  ✗ 失败: {result.get('error', 'Unknown')}")
            else:
                print(f"  ? 未知状态")

            results.append(result)

        return results

    def extract_links_from_text(self, text):
        """
        从文本中提取小红书链接

        支持格式：
        - 纯链接：http://xhslink.com/xxxxx
        - 混合文本：标题 http://xhslink.com/xxxxx 更多文字
        """
        # 提取 xhslink.com 链接
        xhs_links = re.findall(r'https?://[^\s]*xhslink\.com/[^\s]*', text)

        # 提取完整的小红书链接
        xhs_full_links = re.findall(r'https?://[^\s]*xiaohongshu\.com/[^\s]*', text)

        # 合并并去重
        all_links = list(set(xhs_links + xhs_full_links))

        return all_links

    def generate_mediacrawler_config(self, results):
        """
        生成 MediaCrawler 配置

        将解析结果转换为 MediaCrawler 可用的格式
        """
        # 过滤出成功的解析
        successful = [r for r in results if r['status'] == 'success']

        if not successful:
            print("❌ 没有成功解析的链接，无法生成配置")
            return None

        # 提取完整 URL（包含参数）
        full_urls = [r['long_url'] for r in successful]

        return full_urls

    def save_results(self, results, output_file):
        """保存解析结果到 JSON 文件"""
        output = {
            'parse_time': datetime.now().isoformat(),
            'total_links': len(results),
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'error']),
            'results': results
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 结果已保存到: {output_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='小红书短链接解析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--input', '-i',
        help='输入文件路径（每行一个链接）'
    )

    parser.add_argument(
        '--links', '-l',
        help='直接提供链接列表（逗号分隔）'
    )

    parser.add_argument(
        '--text', '-t',
        help='从文本中提取链接'
    )

    parser.add_argument(
        '--output', '-o',
        default='/tmp/xhs_parse_results.json',
        help='输出文件路径（默认：/tmp/xhs_parse_results.json）'
    )

    parser.add_argument(
        '--config',
        action='store_true',
        help='生成 MediaCrawler 配置格式输出'
    )

    args = parser.parse_args()

    parser = ShortLinkParser()

    print("=" * 60)
    print("小红书短链接解析工具")
    print("=" * 60)
    print()

    # 收集需要解析的链接
    links = []

    if args.links:
        # 从命令行参数获取链接
        links = [l.strip() for l in args.links.split(',') if l.strip()]
        print(f"📋 从命令行读取 {len(links)} 个链接")
    elif args.input:
        # 从文件读取链接
        input_path = Path(args.input)
        if input_path.exists():
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            links = [line.strip() for line in content.split('\n') if line.strip()]
            print(f"📂 从文件读取 {len(links)} 个链接: {args.input}")
        else:
            print(f"❌ 文件不存在: {args.input}")
            return 1
    elif args.text:
        # 从文本中提取链接
        links = parser.extract_links_from_text(args.text)
        print(f"📝 从文本提取 {len(links)} 个链接")
    else:
        print("❌ 请提供输入：--input, --links, 或 --text")
        parser.print_help()
        return 1

    if not links:
        print("❌ 未找到任何链接")
        return 1

    print()

    # 解析链接
    results = parser.parse_links(links)

    # 输出汇总
    print()
    print("=" * 60)
    print("解析结果汇总")
    print("=" * 60)

    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'error']

    print(f"总链接数: {len(results)}")
    print(f"解析成功: {len(successful)}")
    print(f"解析失败: {len(failed)}")

    if successful:
        print()
        print("✅ 成功解析的笔记ID:")
        for r in successful:
            print(f"  - {r['note_id']}")

    if failed:
        print()
        print("❌ 失败的链接:")
        for r in failed:
            print(f"  - {r['short_url'][:50]}... ({r.get('error', 'Unknown')})")

    # 保存结果
    parser.save_results(results, args.output)

    # 如果需要，生成 MediaCrawler 配置
    if args.config:
        print()
        print("=" * 60)
        print("MediaCrawler 配置")
        print("=" * 60)

        urls = parser.generate_mediacrawler_config(results)

        if urls:
            print(f"\n# MediaCrawler XHS 配置")
            print(f"# 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            print('# 复制以下内容到 ~/MediaCrawler/config/xhs_config.py')
            print()
            print('XHS_SPECIFIED_NOTE_URL_LIST = [')
            for i, url in enumerate(urls, 1):
                if i < len(urls):
                    print(f'    "{url}",')
                else:
                    print(f'    "{url}"')
            print(']')
            print()
            print("# 然后运行: cd ~/MediaCrawler && .venv/bin/python3.11 main.py")
        else:
            print("❌ 没有成功解析的链接，无法生成配置")

    print()
    print("=" * 60)

    return 0 if len(successful) > 0 else 1


if __name__ == '__main__':
    exit(main())

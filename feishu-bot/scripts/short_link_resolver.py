#!/usr/bin/env python3
"""
短链接解析模块

集成到飞书机器人，自动解析小红书/抖音短链接
调用 MediaCrawler 采集笔记和评论

作者：大秘书系统
版本：v1.0
创建时间：2026-02-11
"""

import re
import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote

class ShortLinkResolver:
    """短链接解析器 - 支持小红书短链接自动解析"""

    def __init__(self, log_file=None):
        """初始化解析器"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        # MediaCrawler 配置路径
        self.mediacrawler_dir = Path.home() / "MediaCrawler"
        self.mediacrawler_config = self.mediacrawler_dir / "config" / "base_config.py"
        self.mediacrawler_python = self.mediacrawler_dir / ".venv" / "bin" / "python"

        # 日志文件
        if log_file:
            self.log_file = log_file
        else:
            self.log_file = Path("/tmp/short_link_resolver.log")

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"

        print(log_entry)

        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)

    def resolve_xhs_short_link(self, short_url):
        """
        解析小红书短链接

        Args:
            short_url: 小红书短链接

        Returns:
            dict: {success: bool, note_id: str, full_url: str, error: str}
        """
        self.log(f"解析短链接: {short_url}")

        try:
            # 发送 HEAD 请求获取重定向
            response = requests.head(
                short_url,
                headers=self.headers,
                allow_redirects=False,
                timeout=10
            )

            # 检查响应
            if response.status_code in [301, 302, 303, 307, 308]:
                # 从 Location 头获取完整 URL
                full_url = response.headers.get('Location', '')

                if full_url:
                    # 提取笔记 ID
                    note_id = self._extract_note_id(full_url)

                    if note_id:
                        self.log(f"✅ 解析成功: {short_url[:50]}... → {note_id}")
                        return {
                            'success': True,
                            'note_id': note_id,
                            'full_url': full_url,
                            'short_url': short_url
                        }
                    else:
                        self.log(f"⚠️  获取完整URL但无法提取笔记ID: {full_url[:80]}")
                        return {
                            'success': True,
                            'note_id': None,
                            'full_url': full_url,
                            'short_url': short_url
                        }

            elif response.status_code == 200:
                # 没有重定向，可能是完整链接
                self.log(f"⚠️ 短链接可能已失效或为完整链接")
                return {
                    'success': False,
                    'note_id': None,
                    'full_url': short_url,
                    'short_url': short_url,
                    'error': '短链接已失效或为完整链接'
                }

            else:
                error_msg = f"HTTP {response.status_code}"
                self.log(f"❌ 解析失败: {error_msg}")
                return {
                    'success': False,
                    'note_id': None,
                    'full_url': short_url,
                    'short_url': short_url,
                    'error': error_msg
                }

        except requests.Timeout:
            error_msg = "请求超时"
            self.log(f"❌ 解析失败: {error_msg}")
            return {
                'success': False,
                'note_id': None,
                'full_url': short_url,
                'short_url': short_url,
                'error': error_msg
            }

        except Exception as e:
            error_msg = str(e)[:100]
            self.log(f"❌ 解析异常: {error_msg}")
            return {
                'success': False,
                'note_id': None,
                'full_url': short_url,
                'short_url': short_url,
                'error': error_msg
            }

    def _extract_note_id(self, url):
        """
        从 URL 中提取笔记 ID

        支持多种格式：
        1. 标准格式：/explore/{note_id}
        2. 登录重定向：redirectPath 包含 /explore/{note_id}
        3. 错误页面：noteId={note_id}
        """
        # 方法1：直接从 URL 路径中提取 /explore/{note_id}
        path_match = re.search(r'/explore/([a-f0-9]{24})', url)
        if path_match:
            return path_match.group(1)

        # 方法2：解析 URL 参数
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

    def batch_resolve_links(self, short_links):
        """批量解析短链接"""
        self.log(f"批量解析 {len(short_links)} 个短链接")

        results = []
        successful = []
        failed = []

        for i, link in enumerate(short_links, 1):
            self.log(f"[{i}/{len(short_links)}] {link[:60]}...")

            result = self.resolve_xhs_short_link(link)

            if result['success']:
                successful.append(result)
                self.log(f"  ✓ 笔记ID: {result['note_id']}")
            else:
                failed.append(result)
                self.log(f"  ✗ 失败: {result.get('error', 'Unknown')}")

        self.log(f"解析完成: 成功 {len(successful)}/{len(short_links)}")

        return {
            'total': len(short_links),
            'successful': successful,
            'failed': failed,
            'success_count': len(successful),
            'fail_count': len(failed)
        }

    def save_note_ids_for_crawler(self, note_ids):
        """保存笔记ID列表用于 MediaCrawler 采集"""
        if not note_ids:
            self.log("没有有效的笔记ID")
            return None

        # 保存到文件供 MediaCrawler 使用
        output_file = Path("/tmp/xhs_note_ids_for_crawler.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            for nid in note_ids:
                f.write(f"{nid}\n")

        self.log(f"已保存 {len(note_ids)} 个笔记ID 到: {output_file}")

        return str(output_file)

    def get_mediacrawler_note_ids(self):
        """获取当前 MediaCrawler 配置的笔记ID列表"""
        try:
            with open(self.mediacrawler_config, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取笔记ID列表
            match = re.search(r'XHS_SPECIFIED_NOTE_URL_LIST\s*=\s*\[([^\]]+)\]', content)
            if match:
                url_list_json = match.group(1)
                note_ids = json.loads(url_list_json.replace("'", '"'))
                self.log(f"MediaCrawler 当前配置 {len(note_ids)} 个笔记ID")
                return note_ids
            else:
                self.log("MediaCrawler 未配置笔记ID列表")
                return []

        except Exception as e:
            self.log(f"读取 MediaCrawler 配置失败: {e}")
            return []


def main():
    """主函数 - 用于测试"""
    import argparse

    parser = argparse.ArgumentParser(description='短链接解析器')
    parser.add_argument('--links', help='短链接列表（逗号分隔）')
    parser.add_argument('--file', help='包含短链接的文件')
    parser.add_argument('--test', action='store_true', help='测试模式')

    args = parser.parse_args()

    resolver = ShortLinkResolver()

    if args.test:
        # 测试模式：测试单个链接解析
        test_link = "http://xhslink.com/o/9BIu7Qm6rEy"
        print(f"测试解析: {test_link}")
        result = resolver.resolve_xhs_short_link(test_link)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.links:
        # 批量解析
        links = [l.strip() for l in args.links.split(',') if l.strip()]
        results = resolver.batch_resolve_links(links)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.file:
        # 从文件读取
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取短链接
        links = re.findall(r'http://xhslink\.com/[a-zA-Z0-9]+', content)

        results = resolver.batch_resolve_links(links)
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

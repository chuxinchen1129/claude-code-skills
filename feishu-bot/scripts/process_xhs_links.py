#!/usr/bin/env python3
"""
小红书链接处理脚本

处理流程：
1. 从文件读取小红书链接（支持短链接 xhslink.com）
2. 解析短链接获取完整 URL
3. 配置 MediaCrawler 使用 detail 模式采集

作者：大秘书系统
版本：v1.0.0
"""

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
import httpx


class XHSLinkProcessor:
    """小红书链接处理器"""

    def __init__(self):
        self.mediacrawler_dir = Path.home() / "MediaCrawler"
        self.config_file = self.mediacrawler_dir / "config" / "base_config.py"
        self.xhs_config = self.mediacrawler_dir / "config" / "xhs_config.py"

    def resolve_short_url(self, url):
        """解析短链接获取完整 URL

        Args:
            url: 短链接或完整链接

        Returns:
            str: 完整 URL
        """
        try:
            with httpx.Client(follow_redirects=True, timeout=10) as client:
                response = client.head(url)
                full_url = str(response.url)
                print(f"  ✓ 解析: {url[:50]}...")
                print(f"    → {full_url[:80]}...")
                return full_url
        except Exception as e:
            print(f"  ⚠️  解析失败: {e}")
            return url

    def read_links_from_file(self, file_path):
        """从文件读取链接

        Args:
            file_path: 文件路径

        Returns:
            list: 链接列表
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line.strip()]

        # 提取 xhslink.com 链接（如果链接中包含其他文字）
        xhs_links = []
        for line in links:
            # 匹配 xhslink.com URL
            match = re.search(r'https?://[^\s]*xhslink\.com[^\s]*', line)
            if match:
                xhs_links.append(match.group(0))
            elif line.startswith('http'):
                xhs_links.append(line)

        return xhs_links

    def modify_config_for_detail_mode(self, url_list):
        """修改配置为 detail 模式

        Args:
            url_list: URL 列表
        """
        # 读取配置
        with open(self.config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 设置为 detail 模式
        content = re.sub(
            r'CRAWLER_TYPE = \([^)]+\)',
            'CRAWLER_TYPE = "detail"',
            content
        )

        # 写回配置
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # 修改 xhs_config.py
        with open(self.xhs_config, 'r', encoding='utf-8') as f:
            xhs_content = f.read()

        # 格式化 URL 列表
        url_list_str = json.dumps(url_list, ensure_ascii=False, indent=4)
        url_list_str = url_list_str.replace('\n', '\n    ')

        # 替换 URL 列表
        xhs_content = re.sub(
            r'XHS_SPECIFIED_NOTE_URL_LIST = \[[^\]]*\]',
            f'XHS_SPECIFIED_NOTE_URL_LIST = {url_list_str}',
            xhs_content
        )

        # 写回配置
        with open(self.xhs_config, 'w', encoding='utf-8') as f:
            f.write(xhs_content)

        print("✓ 配置已更新为 detail 模式")
        print(f"  - URL 数量: {len(url_list)}")

    def run_mediacrawler(self):
        """运行 MediaCrawler"""
        print("\n开始运行 MediaCrawler...")
        print("⚠️  注意：如果 URL 缺少 xsec_token，采集可能会失败")
        print()

        venv_python = self.mediacrawler_dir / ".venv" / "bin" / "python"
        original_dir = Path.cwd()

        try:
            import os
            os.chdir(self.mediacrawler_dir)

            result = subprocess.run(
                [str(venv_python), "main.py"],
                capture_output=False,
                text=True,
                timeout=1200
            )

            return result.returncode == 0

        finally:
            os.chdir(original_dir)

    def process(self, input_file):
        """处理链接文件

        Args:
            input_file: 输入文件路径
        """
        print("=" * 60)
        print("小红书链接采集")
        print("=" * 60)
        print(f"输入文件: {input_file}")
        print()

        # 1. 读取链接
        print("[1/4] 读取链接...")
        links = self.read_links_from_file(input_file)

        if not links:
            print("❌ 未找到有效链接")
            return False

        print(f"✓ 找到 {len(links)} 个链接")

        # 2. 解析短链接
        print("\n[2/4] 解析短链接...")
        full_urls = []
        for link in links:
            full_url = self.resolve_short_url(link)
            full_urls.append(full_url)

        # 3. 修改配置
        print("\n[3/4] 配置 MediaCrawler...")
        self.modify_config_for_detail_mode(full_urls)

        # 4. 运行采集
        print("\n[4/4] 运行采集...")
        success = self.run_mediacrawler()

        if success:
            print("\n✓ 采集完成！")
        else:
            print("\n⚠️  采集可能未完成")

        print("=" * 60)
        return success


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="小红书链接处理脚本"
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="包含小红书链接的文件路径"
    )

    args = parser.parse_args()

    processor = XHSLinkProcessor()
    success = processor.process(args.input)

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

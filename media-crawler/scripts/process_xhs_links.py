#!/usr/bin/env python3
"""
小红书链接处理脚本

处理流程：
1. 从文件读取小红书链接（支持短链接 xhslink.com）
2. 解析短链接获取完整 URL（支持 Playwright 和 httpx 回退）
3. 配置 MediaCrawler 使用 detail 模式采集

作者：大秘书系统
版本：v1.4.0
改进：
- 更严格的错误页面过滤（拒绝 error/login/404 页面）
- 验证 note_id 格式（必须是24位十六进制）
- 过滤无效 URL，只保留有效的 explore 链接
"""

import argparse
import asyncio
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

# 尝试导入 Playwright，如不可用则使用 httpx
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    import httpx


class XHSLinkProcessor:
    """小红书链接处理器"""

    def __init__(self):
        self.mediacrawler_dir = Path.home() / "MediaCrawler"
        self.config_file = self.mediacrawler_dir / "config" / "base_config.py"
        self.xhs_config = self.mediacrawler_dir / "config" / "xhs_config.py"
        self.use_playwright = PLAYWRIGHT_AVAILABLE

    async def _resolve_with_playwright(self, url, page):
        """使用 Playwright 解析短链接"""
        try:
            # 设置 User-Agent 模拟真实浏览器
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
            })

            # 首次访问短链接
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(3)  # 等待 JavaScript 执行和重定向

            current_url = page.url

            # 检查是否成功解析 - 只接受有效的 explore URL，排除错误和登录页面
            if ("xiaohongshu.com/explore/" in current_url and
                "login" not in current_url and
                "error" not in current_url and
                "404" not in current_url):
                # 进一步验证 URL 中的 note_id 是否有效（24位十六进制）
                note_id = self._extract_note_id_from_url(current_url)
                if note_id and len(note_id) == 24:
                    print(f"  ✓ 解析成功: {url[:50]}...")
                    print(f"    → {current_url[:80]}...")
                    return current_url

            # 错误页面直接返回 None 标记为失败
            if "error" in current_url or "login" in current_url or "404" in current_url:
                print(f"  ❌ 跳过错误页面: {current_url[:80]}...")
                return None  # 标记为失败，后续过滤

            # 原始链接未解析的情况
            if "xhslink.com" in current_url:
                print(f"  ⚠️  短链接未能解析: {url[:50]}...")
                return None  # 标记为失败

            print(f"  ⚠️  未知URL状态: {current_url[:80]}...")
            return url

        except Exception as e:
            print(f"  ⚠️  解析失败: {e}")
            return url

    def _extract_note_id_from_url(self, url):
        """从 URL 中提取 note_id

        支持多种 URL 格式：
        1. 标准格式：/explore/{note_id}
        2. 登录重定向：redirectPath 包含 /explore/{note_id}
        3. 错误页面：noteId={note_id}
        """
        from urllib.parse import unquote, urlparse, parse_qs
        import urllib.parse

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

        except Exception as e:
            pass  # 解析失败，继续尝试其他方法

        return None

    def _resolve_with_httpx(self, url):
        """使用 httpx 解析短链接（回退方案）"""
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

    async def resolve_short_url(self, url, page=None):
        """解析短链接获取完整 URL（支持 Playwright 和 httpx 回退）

        Args:
            url: 短链接或完整链接
            page: Playwright 页面对象（可选）

        Returns:
            str: 完整 URL
        """
        if self.use_playwright and page is not None:
            # 使用 Playwright 渲染方式
            return await self._resolve_with_playwright(url, page)
        else:
            # 使用 httpx HEAD 请求方式（回退）
            return self._resolve_with_httpx(url)

    def read_links_from_file(self, file_path):
        """从文件读取链接"""
        with open(file_path, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line.strip()]

        # 提取 xhslink.com 链接
        xhs_links = []
        for line in links:
            match = re.search(r'https?://[^\s]*xhslink\.com[^\s]*', line)
            if match:
                xhs_links.append(match.group(0))
            elif line.startswith('http'):
                xhs_links.append(line)

        return xhs_links

    def modify_config_for_detail_mode(self, url_list):
        """修改配置为 detail 模式"""
        # 读取配置
        with open(self.config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 设置为 detail 模式（更精确的正则，匹配引号内的值）
        content = re.sub(
            r'CRAWLER_TYPE = "[^"]*"',
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

    async def process_async(self, input_file):
        """异步处理链接文件（支持 Playwright 和 httpx 回退）"""
        print("=" * 60)
        print("小红书链接采集（智能解析）")
        print("=" * 60)
        print(f"输入文件: {input_file}")
        print(f"Playwright 可用: {self.use_playwright}")
        print()

        # 1. 读取链接
        print("[1/5] 读取链接...")
        links = self.read_links_from_file(input_file)

        if not links:
            print("❌ 未找到有效链接")
            return False

        print(f"✓ 找到 {len(links)} 个链接")

        # 2. 解析短链接（根据 Playwright 可用性选择方式）
        print("\n[2/5] 解析短链接...")
        full_urls = []

        if self.use_playwright:
            # 使用 Playwright 渲染方式
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                })

                for link in links:
                    full_url = await self.resolve_short_url(link, page)
                    if full_url:  # 只添加非 None 的 URL
                        full_urls.append(full_url)

                await browser.close()
        else:
            # 使用 httpx HEAD 请求方式（回退）
            print("  使用 httpx 方式（回退）")
            for link in links:
                full_url = await self.resolve_short_url(link)
                if full_url:  # 只添加非 None 的 URL
                    full_urls.append(full_url)

        # 过滤掉解析失败的链接（None 已经在添加时被过滤了）
        valid_urls = full_urls  # 已经过滤了 None 值
        print(f"\n✓ 成功解析 {len(valid_urls)}/{len(links)} 个链接")

        if not valid_urls:
            print("❌ 没有成功解析任何链接")
            return False

        # 3. 修改配置
        print("\n[3/5] 配置 MediaCrawler...")
        self.modify_config_for_detail_mode(valid_urls)

        # 4. 运行采集
        print("\n[4/5] 运行采集...")
        success = self.run_mediacrawler()

        if success:
            print("\n✓ 采集完成！")
        else:
            print("\n⚠️ 采集可能未完成")

        print("=" * 60)
        return success

    def process(self, input_file):
        """处理链接文件（同步包装）"""
        asyncio.run(self.process_async(input_file))

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="小红书链接处理脚本（支持 Playwright/httpx 双模式）"
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

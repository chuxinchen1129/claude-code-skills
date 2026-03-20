#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 文本提取工具
支持多种库自动检测：PyPDF2、pdfplumber、pymupdf
"""

import os
import sys
import random
from pathlib import Path
from datetime import datetime


class PDFExtractor:
    """PDF 文本提取器，自动检测可用库"""

    def __init__(self, pdf_path, enable_screenshots=False, screenshot_dir=None, zoom=2.0):
        self.pdf_path = Path(pdf_path)
        self.available_libs = self._detect_available_libs()  # 检测可用的PDF解析库
        self.primary_lib = None
        # 截图配置
        self.enable_screenshots = enable_screenshots
        self.screenshot_dir = Path(screenshot_dir) if screenshot_dir else self._default_screenshot_dir()
        self.zoom = zoom
        self.screenshot_count = 6  # 固定截取 6 张

    def _detect_available_libs(self):
        """检测可用的PDF解析库"""
        libs = []

        # 检查 PyPDF2
        try:
            from PyPDF2 import PdfReader
            libs.append('pypdf2')
        except ImportError:
            pass

        # 检查 pdfplumber
        try:
            import pdfplumber
            libs.append('pdfplumber')
        except ImportError:
            pass

        # 检查 pymupdf (fitz)
        try:
            import fitz
            libs.append('pymupdf')
        except ImportError:
            pass

        return libs

    def _default_screenshot_dir(self):
        """获取默认截图保存目录"""
        skill_dir = Path(__file__).resolve().parent.parent
        return skill_dir / "screenshots"

    def _calculate_screenshot_pages(self, total_pages):
        """
        计算要截取的页面
        策略：跳过前2页和最后5页，从剩余页面中随机选6页

        Args:
            total_pages: PDF 总页数

        Returns:
            list: 要截取的页面索引列表（0-based）
        """
        # 边界情况：页数不足
        if total_pages <= 7:
            # 跳过前2页后，剩余页数不足
            available_pages = list(range(2, total_pages))
            return available_pages if available_pages else [0]

        # 计算可截取的页面范围（跳过前2页，跳过最后5页）
        first_page_idx = 2  # 跳过前2页
        last_page_idx = total_pages - 5  # 跳过最后5页
        available_pages = list(range(first_page_idx, last_page_idx))

        # 如果可用页数不足6页，返回所有可用页
        if len(available_pages) <= self.screenshot_count:
            return available_pages

        # 从可用页面中随机选6页
        return sorted(random.sample(available_pages, self.screenshot_count))

    def _cleanup_old_screenshots(self, current_pdf_name=None):
        """
        清理旧的截图文件
        策略：删除当前PDF名称的所有旧截图，或者删除所有旧截图

        Args:
            current_pdf_name: 当前PDF文件名（不含扩展名），如果指定则只删除该PDF的旧截图
        """
        try:
            if not self.screenshot_dir.exists():
                return

            # 获取所有PNG文件
            png_files = list(self.screenshot_dir.glob("*.png"))
            if not png_files:
                return

            deleted_count = 0
            if current_pdf_name:
                # 只删除当前PDF名称的旧截图
                for f in png_files:
                    if f.name.startswith(current_pdf_name):
                        f.unlink()
                        deleted_count += 1
                if deleted_count > 0:
                    print(f"🗑️ 清理旧截图: 删除 {current_pdf_name} 的 {deleted_count} 个旧截图")
            else:
                # 删除所有旧截图
                for f in png_files:
                    f.unlink()
                    deleted_count += 1
                if deleted_count > 0:
                    print(f"🗑️ 清理旧截图: 删除所有 {deleted_count} 个旧截图")

        except Exception as e:
            print(f"⚠️ 清理旧截图失败: {e}")

    def _capture_page(self, doc, page_idx):
        """
        截取单页为 PNG 图片

        Args:
            doc: fitz 文档对象
            page_idx: 页面索引（0-based）

        Returns:
            Path: 截图文件路径，如果失败返回 None
        """
        try:
            import fitz  # 确保导入 fitz

            # 确保截图目录存在
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)

            # 获取页面
            page = doc[page_idx]

            # 使用 2x 缩放渲染（retina 质量）
            mat = fitz.Matrix(self.zoom, self.zoom)
            pix = page.get_pixmap(matrix=mat)

            # 生成文件名：PDF文件名_页码_时间戳.png
            pdf_name = self.pdf_path.stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{pdf_name}_page{page_idx+1}_{timestamp}.png"
            output_path = self.screenshot_dir / filename

            # 保存为 PNG
            pix.save(str(output_path))

            return output_path

        except Exception as e:
            print(f"⚠️ 截图失败（第 {page_idx+1} 页）: {e}")
            return None

    def _extract_with_pypdf2(self, max_pages=None):
        """使用 PyPDF2 提取文本"""
        import PyPDF2

        text_parts = []
        try:
            with open(self.pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)
                pages_to_extract = min(max_pages or num_pages, num_pages)

                for i in range(pages_to_extract):
                    page = reader.pages[i]
                    text = page.extract_text()
                    if text and text.strip():
                        text_parts.append(f"\n--- 第 {i+1} 页 ---\n{text}\n")

            return {
                'success': True,
                'lib': 'pypdf2',
                'total_pages': num_pages,
                'extracted_pages': pages_to_extract,
                'text': ''.join(text_parts)
            }
        except Exception as e:
            return {
                'success': False,
                'lib': 'pypdf2',
                'error': str(e)
            }

    def _extract_with_pdfplumber(self, max_pages=None):
        """使用 pdfplumber 提取文本"""
        import pdfplumber

        text_parts = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                num_pages = len(pdf.pages)
                pages_to_extract = min(max_pages or num_pages, num_pages)

                for i in range(pages_to_extract):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    if text and text.strip():
                        text_parts.append(f"\n--- 第 {i+1} 页 ---\n{text}\n")

            return {
                'success': True,
                'lib': 'pdfplumber',
                'total_pages': num_pages,
                'extracted_pages': pages_to_extract,
                'text': ''.join(text_parts)
            }
        except Exception as e:
            return {
                'success': False,
                'lib': 'pdfplumber',
                'error': str(e)
            }

    def _extract_with_pymupdf(self, max_pages=None):
        """使用 pymupdf (fitz) 提取文本"""
        import fitz
        # 只导入一次，避免重复导入问题

        text_parts = []
        screenshots = []
        try:
            doc = fitz.open(self.pdf_path)
            num_pages = len(doc)
            pages_to_extract = min(max_pages or num_pages, num_pages)

            # 计算要截取的页面（仅当启用截图时）
            screenshot_pages = []
            if self.enable_screenshots:
                # 截图前先清理旧截图
                pdf_name = self.pdf_path.stem
                self._cleanup_old_screenshots(current_pdf_name=pdf_name)

                screenshot_pages = self._calculate_screenshot_pages(num_pages)
                print(f"📷 将截取页面: {[p+1 for p in screenshot_pages]}")

            for i in range(pages_to_extract):
                page = doc[i]
                text = page.get_text()
                if text and text.strip():
                    text_parts.append(f"\n--- 第 {i+1} 页 ---\n{text}\n")

                # 截图（如果当前页在截图列表中）
                if self.enable_screenshots and i in screenshot_pages:
                    screenshot_path = self._capture_page(doc, i)
                    if screenshot_path:
                        screenshots.append({
                            'page': i + 1,  # 1-based for display
                            'path': str(screenshot_path)
                        })

            doc.close()
            result = {
                'success': True,
                'lib': 'pymupdf',
                'total_pages': num_pages,
                'extracted_pages': pages_to_extract,
                'text': ''.join(text_parts)
            }

            # 如果启用了截图，添加截图信息
            if self.enable_screenshots:
                result['screenshots'] = screenshots
                result['screenshot_count'] = len(screenshots)

            return result
        except Exception as e:
            return {
                'success': False,
                'lib': 'pymupdf',
                'error': str(e)
            }

    def extract_source_from_filename(self) -> str:
        """
        从 PDF 文件名中提取来源机构名称

        支持的格式：
        - MMDD-来源-标题.pdf (如：0227-海通证券-2026工控领域领先企业积极开拓机器人赛道.pdf)
        - 来源-标题.pdf (如：艾瑞咨询-2026母婴行业深度研究报告.pdf)
        - MMDD来源标题.pdf (如：0227工控网2026机器人赛道行业竞争.pdf)

        匹配的机构类型：
        - xx证券, xx咨询, xx研究院, xx研究所, xx研究中心
        - xx银行, xx基金, xx公司

        Returns:
            提取的机构名称，如果匹配失败返回 None
        """
        import re

        filename = self.pdf_path.name

        # 模式1: MMDD-来源-标题.pdf (如：0227-海通证券-2026工控领域领先企业积极开拓机器人赛道.pdf)
        match = re.match(r'^\d{4}-(.+?)-(?:20\d{2}.*)?\.pdf$', filename)
        if match:
            source = match.group(1).strip()
            if self._is_valid_source(source):
                return source

        # 模式2: 来源-标题.pdf (如：艾瑞咨询-2026母婴行业深度研究报告.pdf)
        # 确保不是以日期开头（避免与模式1冲突）
        if not re.match(r'^\d{4}', filename):
            match = re.match(r'^(.+?)-(?:20\d{2}.*)?\.pdf$', filename)
            if match:
                source = match.group(1).strip()
                if self._is_valid_source(source):
                    return source

        # 模式3: MMDD来源标题.pdf (如：0227工控网2026机器人赛道行业竞争.pdf)
        # 这种模式比较难匹配，因为需要区分来源和标题
        # 尝试匹配常见的机构名称格式
        # 只有当没有破折号分隔时才尝试（避免与模式1冲突）
        if '-' not in filename[4:]:
            match = re.match(r'^\d{4}(.+?)(?:20\d{2}.*)?\.pdf$', filename)
            if match:
                potential_source = match.group(1).strip()
                # 限制长度，避免匹配到标题
                if len(potential_source) <= 6 and self._is_valid_source(potential_source):
                    return potential_source

        return None

    def _is_valid_source(self, text: str) -> bool:
        """
        验证是否为有效的机构名称

        Args:
            text: 待验证的文本

        Returns:
            是否为有效的机构名称
        """
        import re

        # 匹配常见的机构后缀
        patterns = [
            r'.*证券$',
            r'.*咨询$',
            r'.*研究院$',
            r'.*研究所$',
            r'.*研究中心$',
            r'.*银行$',
            r'.*基金$',
            r'.*公司$',
        ]

        for pattern in patterns:
            if re.match(pattern, text):
                return True

        # 特殊情况：某些机构名称不带后缀（如工控网）
        if len(text) >= 3 and len(text) <= 6:
            return True

        return False

    def extract_source(self, max_chars: int = 500) -> str:
        """
        从封面页提取来源（机构名称）

        优先使用文件名中的来源，提取失败则从 PDF 封面页提取

        Args:
            max_chars: 最多提取前N个字符

        Returns:
            提取的机构名称，如果失败返回默认值"研究报告"
        """
        # 优先：从文件名提取
        source = self.extract_source_from_filename()
        if source:
            return source

        # 回退：从 PDF 封面页提取
        try:
            import re
            import fitz  # 确保导入 fitz

            # 读取第一页
            doc = fitz.open(self.pdf_path)
            page = doc[0]
            text = page.get_text()
            doc.close()

            # 提取前N个字符
            text = text[:max_chars]

            # 匹配机构名称模式
            patterns = [
                r'([^\s]{2,10}(研究院|咨询|证券|基金|银行|公司))',
                r'([^\s]{2,10}(研究所|研究中心|咨询公司))',
            ]

            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1)

            return "研究报告"  # 默认值

        except Exception as e:
            print(f"⚠️ 提取来源失败: {e}")
            return "研究报告"

    def extract(self, max_pages=None):
        """
        提取 PDF 文本
        自动检测可用库并选择最佳方案

        Args:
            max_pages: 最多提取的页数（None表示全部提取）

        Returns:
            dict: 提取结果，包含文本、使用的库、页数等
        """
        # 不在extract方法中重复检测库，使用__init__中已经检测到的库
        if not self.available_libs:
            return {
                'success': False,
                'error': '未找到可用的PDF解析库，请安装 PyPDF2、pdfplumber 或 pymupdf'
            }

        # 优先级选择：pymupdf > pdfplumber > pypdf2
        # pymupdf 最快且支持中文最好
        # pdfplumber 对表格支持最好
        # pypdf2 轻量级，兼容性最好
        lib_priority = {
            'pymupdf': self._extract_with_pymupdf,
            'pdfplumber': self._extract_with_pdfplumber,
            'pypdf2': self._extract_with_pypdf2
        }

        # 按优先级尝试
        for lib_name in ['pymupdf', 'pdfplumber', 'pypdf2']:
            if lib_name in self.available_libs:
                self.primary_lib = lib_name
                result = lib_priority[lib_name](max_pages)
                if result['success']:
                    return result
                # 如果失败，尝试下一个库
                continue

        return {
            'success': False,
            'error': f'所有可用库提取失败: {self.available_libs}',
            'lib': None,
            'text': '',
            'total_pages': 0,
            'extracted_pages': 0,
            'screenshots': [],
            'screenshot_count': 0
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='PDF 文本提取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python pdf_extractor.py document.pdf
  python pdf_extractor.py document.pdf --max-pages 5
  python pdf_extractor.py document.pdf --enable-screenshots
  python pdf_extractor.py document.pdf --screenshots --dir /path/to/screenshots
        '''
    )
    parser.add_argument('pdf_path', help='PDF 文件路径')
    parser.add_argument('--max-pages', '-p', type=int, help='最多提取的页数')
    parser.add_argument('--enable-screenshots', '--screenshots', '-s',
                        action='store_true', help='启用截图功能')
    parser.add_argument('--screenshot-dir', '--dir', '-d',
                        help='截图保存目录（默认: ~/.claude/skills/baogaomiao/screenshots/）')
    parser.add_argument('--zoom', '-z', type=float, default=2.0,
                        help='截图缩放倍数（默认: 2.0）')

    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"错误: 文件不存在 - {args.pdf_path}")
        sys.exit(1)

    # 创建提取器
    extractor = PDFExtractor(
        args.pdf_path,
        enable_screenshots=args.enable_screenshots,
        screenshot_dir=args.screenshot_dir,
        zoom=args.zoom
    )

    result = extractor.extract(max_pages=args.max_pages)

    if result['success']:
        print(f"✅ 提取成功")
        print(f"   库: {result['lib']}")
        print(f"   总页数: {result['total_pages']}")
        print(f"   提取页数: {result['extracted_pages']}")
        print(f"   字符数: {len(result['text'])}")

        # 显示截图信息
        if args.enable_screenshots and 'screenshots' in result:
            print(f"   截图数: {result['screenshot_count']}")
            print(f"   截图目录: {extractor.screenshot_dir}")
            for shot in result['screenshots']:
                print(f"      - 第 {shot['page']} 页: {shot['path']}")

        print(f"\n--- 提取内容 ---")
        print(result['text'][:500])  # 只显示前500字符
        if len(result['text']) > 500:
            print(f"\n... (省略 {len(result['text']) - 500} 字符)")
    else:
        print(f"❌ 提取失败: {result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 文本提取工具
支持多种库自动检测：PyPDF2、pdfplumber、pymupdf
"""

import os
import sys
from pathlib import Path


class PDFExtractor:
    """PDF 文本提取器，自动检测可用库"""

    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
        self.available_libs = []
        self.primary_lib = None

    def _detect_available_libs(self):
        """检测可用的PDF解析库"""
        libs = []

        # 检查 PyPDF2
        try:
            import PyPDF2
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

        text_parts = []
        try:
            doc = fitz.open(self.pdf_path)
            num_pages = len(doc)
            pages_to_extract = min(max_pages or num_pages, num_pages)

            for i in range(pages_to_extract):
                page = doc[i]
                text = page.get_text()
                if text and text.strip():
                    text_parts.append(f"\n--- 第 {i+1} 页 ---\n{text}\n")

            doc.close()
            return {
                'success': True,
                'lib': 'pymupdf',
                'total_pages': num_pages,
                'extracted_pages': pages_to_extract,
                'text': ''.join(text_parts)
            }
        except Exception as e:
            return {
                'success': False,
                'lib': 'pymupdf',
                'error': str(e)
            }

    def extract(self, max_pages=None):
        """
        提取 PDF 文本
        自动检测可用库并选择最佳方案

        Args:
            max_pages: 最多提取的页数（None表示全部提取）

        Returns:
            dict: 提取结果，包含文本、使用的库、页数等
        """
        self.available_libs = self._detect_available_libs()

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
            'error': f'所有可用库提取失败: {self.available_libs}'
        }


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python pdf_extractor.py <pdf文件路径> [最大页数]")
        print("示例: python pdf_extractor.py document.pdf 5")
        sys.exit(1)

    pdf_path = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else None

    if not os.path.exists(pdf_path):
        print(f"错误: 文件不存在 - {pdf_path}")
        sys.exit(1)

    extractor = PDFExtractor(pdf_path)
    result = extractor.extract(max_pages=max_pages)

    if result['success']:
        print(f"✅ 提取成功")
        print(f"   库: {result['lib']}")
        print(f"   总页数: {result['total_pages']}")
        print(f"   提取页数: {result['extracted_pages']}")
        print(f"   字符数: {len(result['text'])}")
        print(f"\n--- 提取内容 ---")
        print(result['text'])
    else:
        print(f"❌ 提取失败: {result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == '__main__':
    main()

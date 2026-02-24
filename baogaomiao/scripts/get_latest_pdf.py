#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取报告喵文件夹中最新的PDF文件

修复问题：
1. 使用 Path.glob() 而非 shell glob，避免 shell 扩展问题
2. 先检查目录是否存在，提供清晰错误信息
3. 支持用户自定义路径和默认路径
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


# 默认报告喵文件夹路径
DEFAULT_SOURCE_DIR = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "家人共享" / "报告喵"


class PDFFinder:
    """PDF 文件查找器"""

    def __init__(self, source_dir=None):
        """
        初始化PDF查找器

        Args:
            source_dir: 自定义源目录路径（None使用默认路径）
        """
        self.source_dir = Path(source_dir) if source_dir else DEFAULT_SOURCE_DIR

    def find_latest(self):
        """
        查找最新的PDF文件

        Returns:
            dict: 包含文件路径、修改时间、文件名等信息
        """
        # 1. 检查目录是否存在
        if not self.source_dir.exists():
            return {
                'success': False,
                'error': f'目录不存在: {self.source_dir}',
                'error_type': 'directory_not_found',
                'suggested_path': str(DEFAULT_SOURCE_DIR)
            }

        if not self.source_dir.is_dir():
            return {
                'success': False,
                'error': f'路径不是目录: {self.source_dir}',
                'error_type': 'not_a_directory'
            }

        # 2. 使用 Path.glob() 查找 PDF 文件（避免 shell glob 问题）
        pdf_files = list(self.source_dir.glob("*.pdf"))

        if not pdf_files:
            # 尝试不区分大小写
            pdf_files = list(self.source_dir.glob("*.PDF"))

        if not pdf_files:
            return {
                'success': False,
                'error': f'目录中没有PDF文件: {self.source_dir}',
                'error_type': 'no_pdf_files',
                'directory': str(self.source_dir),
                'suggestion': '请将PDF文件放入报告喵文件夹'
            }

        # 3. 按修改时间排序，获取最新文件
        latest_file = max(pdf_files, key=lambda f: f.stat().st_mtime)
        mtime = datetime.fromtimestamp(latest_file.stat().st_mtime)
        size_mb = latest_file.stat().st_size / (1024 * 1024)

        return {
            'success': True,
            'file_path': str(latest_file),
            'file_name': latest_file.name,
            'directory': str(self.source_dir),
            'modified_time': mtime.isoformat(),
            'size_mb': round(size_mb, 2),
            'total_pdf_count': len(pdf_files)
        }

    def list_all(self, limit=10):
        """
        列出目录中的所有PDF文件（按修改时间排序）

        Args:
            limit: 最多显示的文件数

        Returns:
            dict: 包含文件列表
        """
        if not self.source_dir.exists():
            return {
                'success': False,
                'error': f'目录不存在: {self.source_dir}',
                'error_type': 'directory_not_found'
            }

        pdf_files = list(self.source_dir.glob("*.pdf"))
        if not pdf_files:
            pdf_files = list(self.source_dir.glob("*.PDF"))

        if not pdf_files:
            return {
                'success': False,
                'error': f'目录中没有PDF文件: {self.source_dir}',
                'error_type': 'no_pdf_files'
            }

        # 按修改时间排序（最新的在前）
        sorted_files = sorted(pdf_files, key=lambda f: f.stat().st_mtime, reverse=True)
        limited_files = sorted_files[:limit]

        files_info = []
        for f in limited_files:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            size_mb = f.stat().st_size / (1024 * 1024)
            files_info.append({
                'file_name': f.name,
                'file_path': str(f),
                'modified_time': mtime.isoformat(),
                'size_mb': round(size_mb, 2)
            })

        return {
            'success': True,
            'files': files_info,
            'total_count': len(pdf_files),
            'shown_count': len(limited_files),
            'directory': str(self.source_dir)
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='获取报告喵文件夹中最新的PDF文件'
    )
    parser.add_argument(
        '--dir', '-d',
        type=str,
        metavar='PATH',
        help='指定PDF目录路径（默认使用报告喵文件夹）'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出所有PDF文件'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='列出时最多显示的文件数（默认10）'
    )
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='以JSON格式输出'
    )

    args = parser.parse_args()

    finder = PDFFinder(source_dir=args.dir)

    if args.list:
        # 列出所有文件
        result = finder.list_all(limit=args.limit)
    else:
        # 查找最新文件
        result = finder.find_latest()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 人类可读格式
        if not result['success']:
            print(f"❌ {result['error']}")
            if result.get('suggested_path'):
                print(f"💡 建议路径: {result['suggested_path']}")
            if result.get('suggestion'):
                print(f"💡 {result['suggestion']}")
            sys.exit(1)

        if args.list:
            print(f"📁 目录: {result['directory']}")
            print(f"📊 总文件数: {result['total_count']}")
            print(f"📋 显示文件数: {result['shown_count']}")
            print("")
            for i, f in enumerate(result['files'], 1):
                print(f"{i}. {f['file_name']}")
                print(f"   大小: {f['size_mb']:.2f} MB")
                print(f"   修改时间: {f['modified_time']}")
                print("")
        else:
            print(f"✅ 找到最新PDF")
            print(f"   文件名: {result['file_name']}")
            print(f"   路径: {result['file_path']}")
            print(f"   大小: {result['size_mb']:.2f} MB")
            print(f"   修改时间: {result['modified_time']}")
            print(f"   目录总PDF数: {result['total_pdf_count']}")


if __name__ == '__main__':
    main()

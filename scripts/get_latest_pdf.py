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
import re
from pathlib import Path
from datetime import datetime


# 默认报告喵文件夹路径
DEFAULT_SOURCE_DIR = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "家人共享" / "报告喵"


def extract_date_from_filename(filename):
    """
    从文件名中提取日期（MMDD格式）

    Args:
        filename: 文件名

    Returns:
        datetime对象或None
    """
    # 匹配文件名开头的MMDD格式（如 0306, 1231）
    match = re.match(r'(\d{4})', filename)
    if match:
        date_str = match.group(1)
        try:
            month = int(date_str[:2])
            day = int(date_str[2:4])
            # 日期有效性检查
            if 1 <= month <= 12 and 1 <= day <= 31:
                # 获取当前日期
                now = datetime.now()
                current_year = now.year
                current_month = now.month

                # 判断文件名中的日期属于哪一年
                # 如果月份 > current_month + 3，说明是上一年（跨年情况）
                # 否则是当年
                # 例如：当前3月，0309是当年（3月），1230是去年（12月，因为 12 > 3+3=6）
                if month > current_month + 3:
                    # 上一年
                    file_year = current_year - 1
                else:
                    # 当年
                    file_year = current_year

                return datetime(file_year, month, day)
        except ValueError:
            pass
    return None


def get_sort_key(file_path):
    """
    获取文件的排序键值

    优先级：
    1. 文件名中的日期（MMDD格式）
    2. 文件系统修改时间

    Args:
        file_path: 文件路径

    Returns:
        排序键值（元组，第一个是是否有日期，第二个是日期或修改时间）
    """
    # 尝试从文件名提取日期
    file_date = extract_date_from_filename(file_path.name)
    if file_date:
        # 有文件名日期，优先使用（日期越大越新）
        return (1, file_date)
    else:
        # 没有文件名日期，使用修改时间
        return (0, file_path.stat().st_mtime)


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

        # 3. 按文件名日期或修改时间排序，获取最新文件
        # 优先使用文件名中的日期（MMDD格式），其次使用修改时间
        latest_file = max(pdf_files, key=get_sort_key)
        mtime = datetime.fromtimestamp(latest_file.stat().st_mtime)
        size_mb = latest_file.stat().st_size / (1024 * 1024)

        # 检查是否有文件名日期
        file_date = extract_date_from_filename(latest_file.name)
        date_str = file_date.strftime('%m-%d') if file_date else None

        return {
            'success': True,
            'file_path': str(latest_file),
            'file_name': latest_file.name,
            'directory': str(self.source_dir),
            'modified_time': mtime.isoformat(),
            'file_date': date_str,  # 新增：文件名中的日期
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

        # 按文件名日期或修改时间排序（最新的在前）
        sorted_files = sorted(pdf_files, key=get_sort_key, reverse=True)
        limited_files = sorted_files[:limit]

        files_info = []
        for f in limited_files:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            size_mb = f.stat().st_size / (1024 * 1024)
            # 提取文件名中的日期
            file_date = extract_date_from_filename(f.name)
            date_str = file_date.strftime('%m-%d') if file_date else None
            files_info.append({
                'file_name': f.name,
                'file_path': str(f),
                'modified_time': mtime.isoformat(),
                'file_date': date_str,  # 新增：文件名中的日期
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
                # 显示文件名中的日期（如果有）
                if f.get('file_date'):
                    print(f"   文件日期: {f['file_date']}")
                print(f"   修改时间: {f['modified_time']}")
                print("")
        else:
            print(f"✅ 找到最新PDF")
            print(f"   文件名: {result['file_name']}")
            print(f"   路径: {result['file_path']}")
            print(f"   大小: {result['size_mb']:.2f} MB")
            # 显示文件名中的日期（如果有）
            if result.get('file_date'):
                print(f"   文件日期: {result['file_date']}")
            print(f"   修改时间: {result['modified_time']}")
            print(f"   目录总PDF数: {result['total_pdf_count']}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 文件重命名工具

功能：
1. 根据中文标题生成标准化文件名
2. 自动重命名 PDF 文件
3. 避免文件名冲突
"""

import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict


class PDFRenamer:
    """PDF 文件重命名器"""

    # 需要移除的 emoji 列表
    EMOJIS = ['🎯', '💥', '📈', '👶', '📊', '🔍', '🛍️', '💰', '⭐', '⚠️', '🚧', '💡', '🔮',
              '🍼', '🚀', '✨', '🌟', '⭐️', '💫', '🔥', '💪', '🎉', '🎊', '🌈', '📱',
              '💻', '🖥️', '💾', '📁', '📂', '🗂️', '📝', '✏️', '🖊️', '🖍️', '📌', '📍']

    # 年份模式（匹配 2024-2029）
    YEAR_PATTERN = re.compile(r'20[2-9][0-9]')

    # 常见报告类型后缀
    REPORT_SUFFIXES = [
        '研究报告', '行业报告', '趋势报告', '白皮书', '洞察报告',
        '分析报告', '年度报告', '季度报告', '调研报告', '发展报告',
        '数据报告', '经营报告', '竞争报告', '市场报告', '案例报告'
    ]

    def __init__(self, default_year: str = "2026"):
        """
        初始化重命名器

        Args:
            default_year: 默认年份（从标题中提取不到时使用）
        """
        self.default_year = default_year

    def generate_filename(self, chinese_title: str, pdf_path: Optional[Path] = None) -> str:
        """
        根据中文标题生成标准化文件名

        命名格式：MMDD-Year+报告名称.pdf
        - MMDD: 当前日期（月日）
        - Year: 年份（从标题提取，默认2026）
        - 报告名称: 12个中文字以内

        Args:
            chinese_title: 中文标题（如：🎯2026 母婴连锁经营数据报告 —— 逆势增长密码）
            pdf_path: 原 PDF 文件路径（可选，用于保留扩展名）

        Returns:
            新文件名（如：0227-2026母婴连锁经营数据报告.pdf）
        """
        # 1. 提取日期：当前日期 MMDD
        date_str = datetime.now().strftime("%m%d")

        # 2. 提取年份
        year = self._extract_year(chinese_title) or self.default_year

        # 3. 提取报告名称
        name = self._extract_report_name(chinese_title)

        # 4. 组合文件名
        new_name = f"{date_str}-{year}{name}.pdf"

        return new_name

    def _extract_year(self, title: str) -> Optional[str]:
        """从标题中提取年份"""
        match = self.YEAR_PATTERN.search(title)
        return match.group() if match else None

    def _extract_report_name(self, title: str) -> str:
        """
        从标题中提取报告名称（12个中文字以内）

        处理步骤：
        1. 移除 emoji
        2. 移除年份前缀（如 "2026 "）
        3. 移除 "——" 后的副标题
        4. 移除已知的报告类型后缀（避免重复）
        5. 截取前12个字符

        Args:
            title: 原始中文标题

        Returns:
            报告名称（12字以内）
        """
        # 1. 移除 emoji
        name = title
        for emoji in self.EMOJIS:
            name = name.replace(emoji, '')

        # 2. 移除年份前缀（如 "2026 "）
        name = self.YEAR_PATTERN.sub('', name).strip()

        # 3. 移除 "——" 后的副标题
        if '——' in name:
            name = name.split('——')[0].strip()
        elif '-' in name:
            name = name.split('-')[0].strip()
        elif '—' in name:
            name = name.split('—')[0].strip()

        # 4. 移除已知报告类型后缀（简化名称）
        base_name = name
        for suffix in self.REPORT_SUFFIXES:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)].strip()
                break

        # 如果移除后缀后太短，保留原名称
        if len(base_name) < 4:
            base_name = name

        # 5. 截取前12个字符
        report_name = base_name[:12]

        return report_name

    def rename_pdf(self, old_path: Path, new_name: str, dry_run: bool = False) -> Dict:
        """
        重命名 PDF 文件

        Args:
            old_path: 原 PDF 文件路径
            new_name: 新文件名
            dry_run: 是否为试运行（不实际重命名）

        Returns:
            结果字典：
            {
                'success': True/False,
                'old_path': Path,
                'new_path': Path,
                'message': str
            }
        """
        old_path = Path(old_path)

        # 检查原文件是否存在
        if not old_path.exists():
            return {
                'success': False,
                'old_path': old_path,
                'new_path': None,
                'message': f'原文件不存在: {old_path}'
            }

        # 构建新路径
        new_path = old_path.parent / new_name

        # 如果新文件已存在，添加序号
        if new_path.exists():
            base_name = new_path.stem
            extension = new_path.suffix
            counter = 1

            while new_path.exists():
                new_path = old_path.parent / f"{base_name}_{counter}{extension}"
                counter += 1

        # 试运行模式
        if dry_run:
            return {
                'success': True,
                'old_path': old_path,
                'new_path': new_path,
                'message': f'[试运行] 将重命名: {old_path.name} -> {new_path.name}'
            }

        # 执行重命名
        try:
            shutil.move(str(old_path), str(new_path))

            return {
                'success': True,
                'old_path': old_path,
                'new_path': new_path,
                'message': f'✓ 重命名成功: {old_path.name} -> {new_path.name}'
            }
        except Exception as e:
            return {
                'success': False,
                'old_path': old_path,
                'new_path': new_path,
                'message': f'重命名失败: {e}'
            }


# ==================== 命令行接口 ====================

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='PDF 文件重命名工具'
    )
    parser.add_argument(
        'title',
        help='中文标题（如：🎯2026 母婴连锁经营数据报告）'
    )
    parser.add_argument(
        'pdf_path',
        nargs='?',
        help='PDF 文件路径（可选，不指定则只生成文件名）'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式，不实际重命名'
    )

    args = parser.parse_args()

    renamer = PDFRenamer()

    # 生成新文件名
    new_name = renamer.generate_filename(args.title)

    print(f"\n新文件名: {new_name}")

    # 如果指定了 PDF 路径，执行重命名
    if args.pdf_path:
        pdf_path = Path(args.pdf_path)
        result = renamer.rename_pdf(pdf_path, new_name, dry_run=args.dry_run)

        print(f"\n{result['message']}")

        if result['success'] and not args.dry_run:
            print(f"  原路径: {result['old_path']}")
            print(f"  新路径: {result['new_path']}")


if __name__ == '__main__':
    main()

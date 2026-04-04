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

    def __init__(self, default_year: str = "2026", report_date: Optional[str] = None):
        """
        初始化重命名器

        Args:
            default_year: 默认年份（从标题中提取不到时使用）
            report_date: 报告日期，格式 MMDD 或 YYYY-MM-DD（默认使用当前日期）
        """
        self.default_year = default_year
        self.report_date = self._parse_date(report_date)

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """
        解析日期字符串

        Args:
            date_str: 日期字符串，支持格式：
                      - MMDD (如 "0315")
                      - YYYY-MM-DD (如 "2026-03-15")
                      - None (使用当前日期)

        Returns:
            datetime 对象
        """
        if not date_str:
            return datetime.now()

        # 尝试解析 YYYY-MM-DD 格式
        if '-' in date_str:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                pass

        # 尝试解析 MMDD 格式
        if len(date_str) == 4 and date_str.isdigit():
            try:
                # 假设是当前年份
                month = int(date_str[:2])
                day = int(date_str[2:])
                now = datetime.now()
                return datetime(now.year, month, day)
            except ValueError:
                pass

        # 解析失败，使用当前日期
        return datetime.now()

    def generate_filename(self, chinese_title: str, pdf_path: Optional[Path] = None) -> str:
        """
        根据中文标题生成标准化文件名

        命名格式：MMDD-Year+报告名称.pdf
        - MMDD: 报告日期（月日）
        - Year: 年份（从标题提取，默认2026）
        - 报告名称: 12个中文字以内

        Args:
            chinese_title: 中文标题（如：🎯2026 母婴连锁经营数据报告 —— 逆势增长密码）
            pdf_path: 原 PDF 文件路径（可选，用于保留扩展名）

        Returns:
            新文件名（如：0227-2026母婴连锁经营数据报告.pdf）
        """
        # 1. 提取日期：报告日期 MMDD
        date_str = self.report_date.strftime("%m%d")

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

def prompt_for_date() -> str:
    """
    交互式提示输入日期

    Returns:
        日期字符串，格式 YYYY-MM-DD
    """
    print("\n请输入报告日期（用于文件名中的 MMDD 部分）")
    print("支持格式：")
    print("  - YYYY-MM-DD（如 2026-03-15）")
    print("  - MMDD（如 0315）")
    print("  - 直接回车使用当前日期")

    while True:
        user_input = input("\n日期: ").strip()

        if not user_input:
            # 使用当前日期
            now = datetime.now()
            return now.strftime("%Y-%m-%d")

        # 验证格式
        if '-' in user_input:
            try:
                datetime.strptime(user_input, "%Y-%m-%d")
                return user_input
            except ValueError:
                print("❌ 格式错误，请使用 YYYY-MM-DD 格式（如 2026-03-15）")
                continue

        if len(user_input) == 4 and user_input.isdigit():
            try:
                month = int(user_input[:2])
                day = int(user_input[2:])
                if 1 <= month <= 12 and 1 <= day <= 31:
                    # 补全年份
                    now = datetime.now()
                    return f"{now.year}-{user_input[:2]}-{user_input[2:]}"
                else:
                    print("❌ 日期无效，月份1-12，日期1-31")
                    continue
            except ValueError:
                print("❌ 格式错误，请使用 MMDD 格式（如 0315）")
                continue

        print("❌ 格式错误，请重新输入")


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='PDF 文件重命名工具'
    )
    parser.add_argument(
        'title',
        nargs='?',
        help='中文标题（如：🎯2026 母婴连锁经营数据报告）'
    )
    parser.add_argument(
        'pdf_path',
        nargs='?',
        help='PDF 文件路径（可选，不指定则只生成文件名）'
    )
    parser.add_argument(
        '--date', '-d',
        help='报告日期，格式 YYYY-MM-DD 或 MMDD（不指定则交互式输入）'
    )
    parser.add_argument(
        '--use-today',
        action='store_true',
        help='使用当前日期，不提示输入'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式，不实际重命名'
    )
    parser.add_argument(
        '--batch', '-b',
        help='批量重命名指定文件夹中的所有PDF文件'
    )
    parser.add_argument(
        '--skip-weekend',
        action='store_true',
        help='批量重命名时跳过周末（仅限工作日）'
    )

    args = parser.parse_args()

    # 批量重命名模式
    if args.batch:
        # 获取开始日期
        if args.use_today:
            start_date = None
        elif args.date:
            start_date = args.date
        else:
            # 交互式输入开始日期
            print("\n" + "=" * 50)
            print("批量重命名模式")
            print("=" * 50)
            if args.skip_weekend:
                print("模式: 跳过周末（仅工作日）")
            start_date = prompt_for_date()

        renamer = PDFRenamer(report_date=start_date)
        return batch_rename(
            Path(args.batch),
            renamer,
            dry_run=args.dry_run,
            skip_weekend=args.skip_weekend
        )

    # 单个文件模式
    # 获取日期
    if args.use_today:
        report_date = None
    elif args.date:
        report_date = args.date
    else:
        # 交互式输入日期
        report_date = prompt_for_date()

    renamer = PDFRenamer(report_date=report_date)

    # 单个文件重命名模式
    if not args.title:
        print("❌ 错误：需要提供标题或使用 --batch 模式")
        parser.print_help()
        return

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


def batch_rename(folder_path: Path, renamer: PDFRenamer, dry_run: bool = False, skip_weekend: bool = False):
    """
    批量重命名文件夹中的所有PDF文件

    Args:
        folder_path: 文件夹路径
        renamer: PDFRenamer 实例
        dry_run: 是否为试运行
        skip_weekend: 是否跳过周末（周六、周日）
    """
    if not folder_path.exists():
        print(f"❌ 文件夹不存在: {folder_path}")
        return

    # 查找所有PDF文件
    pdf_files = list(folder_path.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ 文件夹中没有PDF文件: {folder_path}")
        return

    print(f"\n找到 {len(pdf_files)} 个PDF文件")
    print(f"开始日期: {renamer.report_date.strftime('%Y-%m-%d')}")
    if skip_weekend:
        print(f"模式: 跳过周末（仅工作日）")
    print("-" * 60)

    # 创建子文件夹用于重命名后的文件
    if not dry_run:
        renamed_folder = folder_path / "renamed"
        renamed_folder.mkdir(exist_ok=True)

    success_count = 0
    skip_count = 0
    current_date = renamer.report_date

    for i, pdf_path in enumerate(pdf_files):
        # 从文件名生成标题（简单处理）
        # 移除扩展名
        base_name = pdf_path.stem

        # 为当前PDF创建独立的 renamer 实例（使用当前日期）
        current_renamer = PDFRenamer(report_date=current_date.strftime("%Y-%m-%d"))

        # 生成新文件名
        new_name = current_renamer.generate_filename(base_name)

        # 构建新路径
        if dry_run:
            new_path = pdf_path.parent / new_name
        else:
            new_path = renamed_folder / new_name

        # 检查是否已经是标准格式
        if pdf_path.name.startswith(current_date.strftime("%m%d")):
            print(f"⊘ 跳过（已是标准格式）: {pdf_path.name}")
            skip_count += 1
        else:
            # 执行重命名（复制到新文件夹）
            try:
                weekday_name = current_date.strftime("%a")
                if dry_run:
                    print(f"[试运行] {pdf_path.name} -> {new_name} ({current_date.strftime('%Y-%m-%d')} {weekday_name})")
                else:
                    shutil.copy2(pdf_path, new_path)
                    print(f"✓ {pdf_path.name} -> {new_name} ({current_date.strftime('%Y-%m-%d')} {weekday_name})")
                success_count += 1
            except Exception as e:
                print(f"❌ 失败: {pdf_path.name} - {e}")

        # 计算下一个PDF的日期（跳过周末）
        if skip_weekend:
            # 递增到下一个工作日
            current_date = _next_workday(current_date)
        else:
            # 递增一天
            current_date = _add_days(current_date, 1)

    print("-" * 60)
    print(f"\n批量重命名完成: 成功 {success_count}, 跳过 {skip_count}, 共 {len(pdf_files)}")

    if not dry_run:
        print(f"\n重命名后的文件保存在: {renamed_folder}")


def _add_days(date: datetime, days: int) -> datetime:
    """给日期添加指定天数"""
    from datetime import timedelta
    return date + timedelta(days=days)


def _next_workday(date: datetime) -> datetime:
    """
    获取下一个工作日（跳过周六、周日）

    Args:
        date: 当前日期

    Returns:
        下一个工作日
    """
    from datetime import timedelta
    next_date = date + timedelta(days=1)

    # 如果是周六（5）或周日（6），继续递增
    while next_date.weekday() >= 5:
        next_date = next_date + timedelta(days=1)

    return next_date


if __name__ == '__main__':
    main()

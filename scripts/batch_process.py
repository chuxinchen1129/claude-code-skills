#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理PDF文件 - baogaomiao skill
解析PDF、生成笔记、生成封面、发送到飞书、重命名文件
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 添加脚本路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from pdf_extractor import PDFExtractor
from editorial_cover import EditorialCoverGenerator, EditorialCoverGenerator
from html_to_image import HTMLToImageConverter
from file_namer import PDFRenamer
import shutil
import glob


def _next_workday(date: datetime) -> datetime:
    """获取下一个工作日（跳过周六、周日）"""
    next_date = date + timedelta(days=1)
    while next_date.weekday() >= 5:  # 5=周六, 6=周日
        next_date = next_date + timedelta(days=1)
    return next_date


def process_pdf(pdf_path: str, report_date: str, index: int, total: int, dry_run: bool = False):
    """
    处理单个PDF文件

    Args:
        pdf_path: PDF文件路径
        report_date: 报告日期 (MMDD格式)
        index: 当前索引
        total: 总数量
        dry_run: 是否为试运行
    """
    pdf_name = Path(pdf_path).name

    print(f"\n{'='*60}")
    print(f"处理 PDF {index}/{total}: {pdf_name}")
    print(f"报告日期: {report_date}")
    print(f"{'='*60}")

    try:
        # 1. 解析PDF并生成截图
        print(f"\n[1/5] 解析PDF并生成截图...")
        extractor = PDFExtractor(pdf_path, enable_screenshots=True)
        extract_result = extractor.extract(max_pages=10)
        print(f"   ✅ 提取成功: {extract_result['total_pages']}页, {extract_result['screenshot_count']}张截图")

        # 2. 生成小红书笔记
        print(f"\n[2/5] 生成小红书笔记...")
        title_lines = [
            f"🎯2026{extract_result['text'][:30]}...",
            "梗概：行业洞察与趋势分析",
            "关键词：行业研究、市场分析、发展前景"
        ]
        note_content = "\n".join(title_lines)

        # 3. 生成封面
        print(f"\n[3/5] 生成封面...")
        # 提取基本信息用于封面
        source = "研究报告"
        page_count = extract_result['total_pages']

        # 从文件名提取主题
        base_name = Path(pdf_path).stem
        # 移除机构名称前缀
        if '+' in base_name:
            parts = base_name.split('+')
            if len(parts) > 1:
                base_name = '+'.join(parts[1:])

        # 清理标题：移除年份、扩展名、特殊符号
        import re
        base_name = re.sub(r'20[25]\d', '', base_name)  # 移除2025、2026
        base_name = re.sub(r'[+：：、\-—_]', '', base_name)  # 移除特殊符号

        # 特殊主题映射：将长主题转换为简洁的关键词组合
        theme_mappings = {
            "中国女性身心健康睡眠": "女性睡眠健康",
            "中国女性身心健康": "女性身心健康",
            "短剧内容消费偏好": "短剧消费偏好",
            "海外网红营销生态": "海外网红营销",
            "酒饮即时零售经营": "酒饮即时零售",
            "中国餐饮品牌出海": "中餐品牌出海",
            "茶咖新风向行业演变": "茶咖新风向",
            "知行数据观察防晒品类": "防晒品类研究",
        }

        for old_theme, new_theme in theme_mappings.items():
            if old_theme in base_name:
                base_name = base_name.replace(old_theme, new_theme)
                break

        # 移除常见报告后缀，保留核心主题
        suffixes = ["行业报告", "发展报告", "研究报告", "深度报告", "白皮书",
                    "生态报告", "观察报告", "经营风向标", "趋势解码",
                    "全景观察", "身心健康睡眠", "内容消费偏好"]
        for suffix in suffixes:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break

        # 清理后再次去除可能残留的特殊字符
        base_name = base_name.strip()
        base_name = re.sub(r'[:：、\-—_]', '', base_name)

        # 限制长度但保证语义完整（最多12字）
        if len(base_name) > 12:
            base_name = base_name[:12]

        # 如果标题太短或为空，使用默认
        if len(base_name) < 4:
            base_name = "行业研究"

        # 简化标题用于封面
        chinese_title = f"2026\n{base_name}\n研究报告"
        english_title = "INDUSTRY RESEARCH REPORT"

        generator = EditorialCoverGenerator()
        cover_result = generator.generate_cover(
            source=source,
            page_count=page_count,
            chinese_title=chinese_title,
            english_title=english_title,
            year='2026',
            highlight_title='行业洞察与趋势分析',
            summary_text='行业研究、市场分析',
            report_date=report_date
        )

        # 转换为PNG
        converter = HTMLToImageConverter()
        png_result = converter.convert_to_xhs_style(html_path=cover_result['path'])

        # 移动封面到screenshots目录
        screenshots_dir = Path.home() / '.claude' / 'skills' / 'baogaomiao' / 'screenshots'
        cover_png = Path(png_result['path'])
        target_cover = screenshots_dir / cover_png.name
        shutil.move(str(cover_png), str(target_cover))
        print(f"   ✅ 封面生成: {target_cover.name}")

        # 4. 重命名PDF
        print(f"\n[4/5] 重命名PDF...")
        renamer = PDFRenamer(report_date=report_date)
        chinese_title_for_rename = f"🎯2026{base_name}研究报告"
        new_name = renamer.generate_filename(chinese_title_for_rename)

        if not dry_run:
            rename_result = renamer.rename_pdf(Path(pdf_path), new_name)
            print(f"   ✅ PDF重命名: {rename_result['new_path'].name}")
        else:
            print(f"   [试运行] PDF将重命名为: {new_name}")

        # 5. 发送到飞书
        if not dry_run:
            print(f"\n[5/5] 发送到飞书...")
            # 这里需要集成飞书发送逻辑
            # 暂时跳过，因为需要大量飞书API调用
            print(f"   ⏭️  跳过飞书发送（需要单独处理）")

        print(f"\n✅ PDF {index}/{total} 处理完成!")
        return True

    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        return False


def batch_process_pdfs(folder_path: str, start_date: str, dry_run: bool = False):
    """
    批量处理PDF文件

    Args:
        folder_path: 文件夹路径
        start_date: 开始日期 (MMDD格式)
        dry_run: 是否为试运行
    """
    folder = Path(folder_path)

    # 查找所有PDF文件
    pdf_files = list(folder.glob("*.pdf"))

    # 过滤掉已重命名的文件（以MMDD-开头的）
    import re
    pdf_files = [f for f in pdf_files if not re.match(r'\d{4}-2026', f.name)]

    if not pdf_files:
        print("❌ 没有找到需要处理的PDF文件")
        return

    print(f"\n找到 {len(pdf_files)} 个需要处理的PDF文件")
    print(f"开始日期: {start_date}")
    print(f"模式: {'试运行' if dry_run else '正式处理'}")
    print(f"跳过周末: 是")

    # 解析开始日期
    current_date = datetime.strptime(start_date, "%m%d")
    if current_date.year == 1900:
        current_date = current_date.replace(year=datetime.now().year)

    success_count = 0

    for i, pdf_file in enumerate(pdf_files):
        # 生成当前PDF的日期字符串
        date_str = current_date.strftime("%m%d")

        # 处理PDF
        if process_pdf(str(pdf_file), date_str, i + 1, len(pdf_files), dry_run):
            success_count += 1

        # 递增到下一个工作日
        current_date = _next_workday(current_date)

    print(f"\n{'='*60}")
    print(f"批量处理完成!")
    print(f"成功: {success_count}/{len(pdf_files)}")
    print(f"模式: {'试运行（未实际修改）' if dry_run else '正式处理'}")
    print(f"{'='*60}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='批量处理PDF文件')
    parser.add_argument('folder', help='PDF文件夹路径')
    parser.add_argument('--date', required=True, help='开始日期 (MMDD格式)')
    parser.add_argument('--dry-run', action='store_true', help='试运行模式')

    args = parser.parse_args()

    batch_process_pdfs(args.folder, args.date, args.dry_run)

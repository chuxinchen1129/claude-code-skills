#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书调研技能 - 主入口脚本
"""

import argparse
import sys
import os
from pathlib import Path

# 添加scripts目录到Python路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from crawler import XHSCrawler
from processor import DataProcessor
from reporter import ReportGenerator
from datetime import datetime


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="小红书调研技能 - 自动采集小红书数据并生成分析报告",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-k', '--keywords', type=str, nargs='+', required=True,
                       help='搜索关键词（必填，可指定多个，如：-k 天然茯苓 真茯苓）')
    parser.add_argument('-c', '--count', type=int, default=30,
                       help='每个关键词的采集数量（默认：30）')
    parser.add_argument('-d', '--date', type=str, default=datetime.now().strftime('%Y-%m-%d'),
                       help='任务日期，格式：YYYY-MM-DD（默认：当天）')
    parser.add_argument('--clear-cache', action='store_true',
                       help='清空MediaCrawler缓存后采集')

    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()

    keywords = args.keywords
    count = args.count
    date_str = args.date
    clear_cache = args.clear_cache

    # 生成输出目录名（使用多个关键词的组合）
    keywords_str = '_'.join(keywords)
    output_dir = Path(f"/Users/echochen/Desktop/DMS/00.每日工作/{date_str}_小红书调研_{keywords_str}")

    print("=" * 60)
    print("小红书调研技能")
    print("=" * 60)
    print()
    print(f"关键词: {', '.join(keywords)}")
    print(f"采集数量: {count} (每个关键词)")
    print(f"任务日期: {date_str}")
    print(f"清空缓存: {'是' if clear_cache else '否'}")
    print()

    # 创建输出目录
    data_dir = output_dir / "data"
    reports_dir = output_dir / "reports"
    temp_dir = output_dir / "temp"

    # 创建输出目录
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    print(f"输出目录: {output_dir}")
    print()

    try:
        # 1. 清空缓存（如果需要）
        if clear_cache:
            print("正在清空MediaCrawler缓存...")
            crawler = XHSCrawler()
            crawler.clear_cache()
            print("✅ 缓存已清空")
            print()

        # 2. 采集数据
        print("正在采集数据...")
        crawler = XHSCrawler()
        json_data = crawler.crawl(keywords, count)
        print(f"✅ 采集完成，共 {len(json_data)} 条")
        print()

        # 3. 处理数据
        print("正在处理数据...")
        processor = DataProcessor()
        top_notes, media_files = processor.process(json_data, keywords, temp_dir)
        print(f"✅ 处理完成，TOP {len(top_notes)} 条")
        print()

        # 4. 生成Excel报告
        excel_filename = f"{date_str}_小红书调研_{keywords_str}数据.xlsx"
        excel_path = data_dir / excel_filename
        print("正在生成Excel数据表...")
        processor.generate_excel(top_notes, excel_path, media_files)
        print(f"✅ Excel已生成: {excel_path}")
        print()

        # 5. 生成MD分析报告
        report_filename = f"{date_str}_小红书调研_{keywords_str}报告.md"
        report_path = reports_dir / report_filename
        print("正在生成分析报告...")
        reporter = ReportGenerator()
        reporter.generate_report(top_notes, keywords, report_path)
        print(f"✅ 报告已生成: {report_path}")
        print()

        # 6. 清理临时文件
        print("正在清理临时文件...")
        import shutil
        # 清理champ文件
        for champ_file in Path(temp_dir).rglob("champ_*.pyc"):
            champ_file.unlink()
        # 清理__pycache__
        pycache_dir = Path(temp_dir) / "__pycache__"
        if pycache_dir.exists():
            shutil.rmtree(pycache_dir)
        # 清理temp目录本身（可选，保留媒体文件在data/）
        # temp_dir.rmtree()
        print("✅ 临时文件已清理")

    except KeyboardInterrupt:
        print("\n\n任务已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("任务完成！")
    print(f"输出目录: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书科普图文生成器 - CLI 入口

支持功能：
1. 日期范围批量生成 (batch)
2. 单篇内容生成 (single)

Usage:
    python main.py batch --node "常规投放" --days 7
    python main.py single --topic "深睡" --audience "职场人士"
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 导入生成器模块
from generator import (
    generate_content_structure,
    generate_content_batch,
    save_contents_to_csv
)

# ==================== 配置 ====================

DEFAULT_OUTPUT_DIR = Path("./output")
PROJECT_ROOT = Path(__file__).parent.parent


# ==================== 辅助函数 ====================

def load_science_concepts(wiki_path: Path) -> list:
    """
    加载科学概念库

    参数:
        wiki_path: Wiki JSON文件路径

    返回:
        概念列表
    """
    if not wiki_path.exists():
        print(f"⚠️  Wiki文件不存在: {wiki_path}")
        print("使用默认概念库")
        return [
            {"name": "Deep Sleep", "pain_point": "深睡不足", "solution": "深睡质量提升"},
            {"name": "Sleep Pressure", "pain_point": "入睡困难", "solution": "科学助眠"},
            {"name": "Circadian Rhythm", "pain_point": "作息紊乱", "solution": "规律作息"}
        ]

    with open(wiki_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get("concepts", [])


def load_marketing_calendar(calendar_path: Path) -> dict:
    """
    加载营销日历

    参数:
        calendar_path: CSV文件路径

    返回:
        营销日历数据
    """
    if not calendar_path.exists():
        return {}

    df = pd.read_csv(calendar_path)
    calendar = {}

    for _, row in df.iterrows():
        date_str = row.get("日期", "")
        node = row.get("营销节点", "常规投放")
        if date_str:
            calendar[date_str] = node

    return calendar


# ==================== CLI 命令 ====================

def cmd_batch(args):
    """
    批量生成内容（日期范围）
    """
    print(f"\n{'='*60}")
    print(f"小红书科普图文 - 批量生成")
    print(f"{'='*60}")
    print(f"营销节点: {args.node}")
    print(f"日期范围: {args.start_date} 到 {args.end_date}")

    # 加载科学概念库
    wiki_path = PROJECT_ROOT / "../../03_WUXIN_CONTENT/05_Sleep_Science_Wiki/sleep_science.json"
    concepts = load_science_concepts(wiki_path)
    print(f"科学概念: {len(concepts)}个")

    # 生成内容
    contents = generate_content_batch(
        marketing_node=args.node,
        start_date=args.start_date,
        end_date=args.end_date,
        science_concepts=concepts
    )

    print(f"\n✅ 生成完成: {len(contents)}篇内容")

    # 保存
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    filename = f"Content_{args.start_date}_to_{args.end_date}.csv"
    csv_path = save_contents_to_csv(contents, output_dir, filename)

    print(f"\n📁 已保存: {csv_path}")

    # 统计
    total_words = sum(c["字数统计"] for c in contents)
    avg_words = total_words / len(contents) if contents else 0

    print(f"\n📊 统计:")
    print(f"  - 总篇数: {len(contents)}")
    print(f"  - 总字数: {total_words}")
    print(f"  - 平均字数: {avg_words:.0f}")

    return contents


def cmd_single(args):
    """
    单篇内容生成
    """
    print(f"\n{'='*60}")
    print(f"小红书科普图文 - 单篇生成")
    print(f"{'='*60}")
    print(f"主题: {args.topic}")
    print(f"受众: {args.audience}")
    print(f"痛点: {args.pain_point}")
    print(f"切入角度: {args.angle}")

    # 生成内容
    content = generate_content_structure(
        topic=args.topic,
        audience=args.audience,
        pain_point=args.pain_point,
        angle=args.angle,
        science_concept=args.concept or args.topic
    )

    print(f"\n✅ 生成完成")
    print(f"  标题: {content['笔记标题']}")
    print(f"  字数: {content['字数统计']}")

    # 保存
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"Content_{today}_{args.topic}.csv"

    df = pd.DataFrame([content])
    csv_path = output_dir / filename
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    print(f"\n📁 已保存: {csv_path}")

    # 显示内容预览
    print(f"\n📝 内容预览:")
    print(f"  封面大字: {content['封面大字']}")
    print(f"  板块1: {content['板块1标题']}")
    print(f"  板块2: {content['板块2标题']}")
    print(f"  板块3: {content['板块3标题']}")

    return content


# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(
        description="小红书科普图文生成器 v1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 批量生成（本周）
  python main.py batch --node "常规投放" --days 7

  # 批量生成（日期范围）
  python main.py batch --node "常规投放" --start-date 2026-02-26 --end-date 2026-03-05

  # 单篇生成
  python main.py single --topic "深睡" --audience "职场人士" --pain-point "睡够8小时还是累" --angle "深睡质量提升"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ---------- batch ----------
    parser_batch = subparsers.add_parser("batch", help="批量生成内容（日期范围）")
    parser_batch.add_argument("--node", default="常规投放", help="营销节点")
    parser_batch.add_argument("--days", type=int, help="生成天数（从今天开始）")
    parser_batch.add_argument("--start-date", help="开始日期（YYYY-MM-DD）")
    parser_batch.add_argument("--end-date", help="结束日期（YYYY-MM-DD）")
    parser_batch.add_argument("--output", "-o", help="输出目录")

    # ---------- single ----------
    parser_single = subparsers.add_parser("single", help="单篇内容生成")
    parser_single.add_argument("--topic", required=True, help="内容主题")
    parser_single.add_argument("--audience", default="职场人士", help="目标受众")
    parser_single.add_argument("--pain-point", required=True, help="核心痛点")
    parser_single.add_argument("--angle", required=True, help="营销切入角度")
    parser_single.add_argument("--concept", help="科学概念（默认使用topic）")
    parser_single.add_argument("--output", "-o", help="输出目录")

    args = parser.parse_args()

    # 处理默认日期范围
    if args.command == "batch":
        if not args.start_date and not args.end_date and args.days:
            today = datetime.now()
            args.start_date = today.strftime("%Y-%m-%d")
            args.end_date = (today + timedelta(days=args.days - 1)).strftime("%Y-%m-%d")
        elif not args.start_date or not args.end_date:
            parser.error("batch 需要指定 --days 或 --start-date + --end-date")

    # 执行命令
    if args.command == "batch":
        cmd_batch(args)
    elif args.command == "single":
        cmd_single(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

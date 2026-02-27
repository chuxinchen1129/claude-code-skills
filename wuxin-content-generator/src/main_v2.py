#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
悟昕内容生成器 - CLI 入口 v2.0

支持功能：
1. 话题池生成 (topic-pool)
2. 话题评分 (rate)
3. 脚本生成 (scripts)
4. 完整流程 (full-pipeline)

Usage:
    python main.py full-pipeline --node "常规投放" --target-count 18
    python main.py topic-pool --node "常规投放"
    python main.py rate --input "常规投放_话题池.xlsx" --target-count 18
    python main.py scripts --input "常规投放_Top18选题.xlsx"
"""

import argparse
import sys
from pathlib import Path

# 导入模块
from topic_pool import generate_topic_pool, save_topic_pool
from topic_rater import rate_all_topics, save_rating_result
from script_gen import generate_scripts_from_topics, save_scripts_to_excel

# ==================== 配置 ====================

DEFAULT_OUTPUT_DIR = Path("./output")
PROJECT_ROOT = Path(__file__).parent.parent


# ==================== CLI 命令 ====================

def cmd_topic_pool(args):
    """
    生成话题池
    """
    print(f"\n{'='*60}")
    print(f"话题池生成")
    print(f"{'='*60}")
    print(f"营销节点: {args.node}")
    print(f"基础选题数: {args.base_topics}")
    print(f"裂变维度数: {args.fission}")

    # 生成话题池
    pool = generate_topic_pool(
        node=args.node,
        base_topics_count=args.base_topics,
        fission_per_topic=args.fission
    )

    print(f"\n✅ 生成完成: {pool['total_topics']}个选题")

    # 保存
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    json_path, excel_path = save_topic_pool(pool, output_dir, args.node)

    print(f"\n📁 已保存:")
    print(f"  - {json_path}")
    print(f"  - {excel_path}")

    return pool


def cmd_rate(args):
    """
    话题评分
    """
    print(f"\n{'='*60}")
    print(f"话题评分筛选")
    print(f"{'='*60}")

    # 读取输入文件
    import pandas as pd
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"❌ 文件不存在: {input_path}")
        sys.exit(1)

    df = pd.read_excel(input_path)

    # 转换为话题列表
    topics = []
    for _, row in df.iterrows():
        topics.append({
            "id": str(row.get("选题ID", "")),
            "scene_category": row.get("场景分类", ""),
            "target_audience": row.get("目标人群", ""),
            "core_pain_point": row.get("核心痛点", ""),
            "marketing_angle": row.get("营销切入角度", ""),
            "title": row.get("选题标题", "")
        })

    print(f"候选选题: {len(topics)}个")
    print(f"及格分数线: {args.passing_line}分")
    print(f"目标数量: {args.target_count}个")
    print(f"爆款导向: {'是' if args.focus_viral else '否'}")

    # 评分
    result = rate_all_topics(
        topics=topics,
        node=args.node or "常规投放",
        target_count=args.target_count,
        passing_line=args.passing_line,
        focus_viral=args.focus_viral
    )

    print(f"\n✅ 评分完成:")
    print(f"  - 总数: {result['summary']['total_count']}个")
    print(f"  - 及格: {result['summary']['passed_count']}个")
    print(f"  - 推荐: {result['summary']['recommended_count']}个")
    print(f"  - 优秀: {result['summary']['excellent_count']}个")

    # 保存
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    json_path, excel_path = save_rating_result(result, output_dir, args.node or "常规投放")

    print(f"\n📁 已保存:")
    print(f"  - {json_path}")
    print(f"  - {excel_path}")

    return result


def cmd_scripts(args):
    """
    生成脚本
    """
    print(f"\n{'='*60}")
    print(f"视频脚本生成")
    print(f"{'='*60}")

    # 读取输入文件
    import pandas as pd
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"❌ 文件不存在: {input_path}")
        sys.exit(1)

    df = pd.read_excel(input_path)

    # 转换为话题列表
    topics = []
    for _, row in df.iterrows():
        topics.append({
            "id": str(row.get("选题ID", "")),
            "scene_category": row.get("场景分类", ""),
            "target_audience": row.get("目标人群", ""),
            "core_pain_point": row.get("核心痛点", ""),
            "marketing_angle": row.get("营销切入角度", ""),
            "title": row.get("选题标题", "")
        })

    print(f"输入选题: {len(topics)}个")
    print(f"品牌植入: {args.brand_integration}")

    # 生成脚本
    scripts = generate_scripts_from_topics(
        topics=topics,
        brand_integration=args.brand_integration
    )

    print(f"\n✅ 生成完成: {len(scripts)}个脚本")

    # 保存
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    filename = f"{args.node or '常规投放'}_Top{len(scripts)}脚本_标准格式版.xlsx"
    excel_path = save_scripts_to_excel(scripts, output_dir, filename)

    print(f"\n📁 已保存: {excel_path}")

    return scripts


def cmd_full_pipeline(args):
    """
    完整流程：话题池 → 评分 → 脚本生成
    """
    print(f"\n{'='*60}")
    print(f"悟昕内容生成器 - 完整流程")
    print(f"{'='*60}")
    print(f"营销节点: {args.node}")
    print(f"目标数量: {args.target_count}")

    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR

    # ========== 步骤1: 生成话题池 ==========
    print(f"\n[步骤1/3] 生成话题池...")
    pool = generate_topic_pool(
        node=args.node,
        base_topics_count=args.base_topics,
        fission_per_topic=args.fission
    )
    print(f"  ✅ 生成 {pool['total_topics']}个候选选题")

    json_path, excel_path = save_topic_pool(pool, output_dir, args.node)
    print(f"  📁 {excel_path.name}")

    # ========== 步骤2: 评分筛选 ==========
    print(f"\n[步骤2/3] 评分筛选...")
    rating = rate_all_topics(
        topics=pool["topics"],
        node=args.node,
        target_count=args.target_count,
        passing_line=args.passing_line,
        focus_viral=args.focus_viral
    )
    print(f"  ✅ 筛选 {len(rating['recommended'])}个高质量选题")

    _, excel_path = save_rating_result(rating, output_dir, args.node)
    print(f"  📁 {excel_path.name}")

    # ========== 步骤3: 生成脚本 ==========
    print(f"\n[步骤3/3] 生成脚本...")
    scripts = generate_scripts_from_topics(
        topics=rating["recommended"],
        brand_integration=args.brand_integration
    )
    print(f"  ✅ 生成 {len(scripts)}个视频脚本")

    filename = f"{args.node}_Top{len(scripts)}脚本_标准格式版.xlsx"
    excel_path = save_scripts_to_excel(scripts, output_dir, filename)
    print(f"  📁 {excel_path.name}")

    # ========== 完成 ==========
    print(f"\n{'='*60}")
    print(f"✅ 完整流程执行完成！")
    print(f"{'='*60}")
    print(f"\n📊 生成统计:")
    print(f"  - 候选选题: {pool['total_topics']}个")
    print(f"  - 高质量选题: {len(rating['recommended'])}个")
    print(f"  - 视频脚本: {len(scripts)}个")
    print(f"\n📁 输出目录: {output_dir}")

    return {
        "pool": pool,
        "rating": rating,
        "scripts": scripts
    }


# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(
        description="悟昕内容生成器 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完整流程（推荐）
  python main.py full-pipeline --node "常规投放" --target-count 18

  # 分步执行
  python main.py topic-pool --node "常规投放"
  python main.py rate --input "常规投放_话题池.xlsx" --target-count 18
  python main.py scripts --input "常规投放_Top18选题.xlsx"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ---------- topic-pool ----------
    parser_pool = subparsers.add_parser("topic-pool", help="生成话题池")
    parser_pool.add_argument("--node", required=True, help="营销节点（如'常规投放'、'春节送礼'）")
    parser_pool.add_argument("--base-topics", type=int, default=10, help="基础选题数量（默认10）")
    parser_pool.add_argument("--fission", type=int, default=5, help="每个选题裂变数（默认5）")
    parser_pool.add_argument("--output", "-o", help="输出目录")

    # ---------- rate ----------
    parser_rate = subparsers.add_parser("rate", help="话题评分筛选")
    parser_rate.add_argument("--input", "-i", required=True, help="输入文件路径（话题池Excel）")
    parser_rate.add_argument("--node", help="营销节点")
    parser_rate.add_argument("--target-count", type=int, default=18, help="目标数量（默认18）")
    parser_rate.add_argument("--passing-line", type=int, default=25, help="及格分数线（默认25）")
    parser_rate.add_argument("--focus-viral", action="store_true", help="优先爆款潜力")
    parser_rate.add_argument("--output", "-o", help="输出目录")

    # ---------- scripts ----------
    parser_scripts = subparsers.add_parser("scripts", help="生成视频脚本")
    parser_scripts.add_argument("--input", "-i", required=True, help="输入文件路径（评分结果Excel）")
    parser_scripts.add_argument("--node", help="营销节点")
    parser_scripts.add_argument("--brand-integration", choices=["soft", "medium", "hard"], default="soft", help="品牌植入程度")
    parser_scripts.add_argument("--output", "-o", help="输出目录")

    # ---------- full-pipeline ----------
    parser_full = subparsers.add_parser("full-pipeline", help="完整流程（一键执行）")
    parser_full.add_argument("--node", required=True, help="营销节点（如'常规投放'、'春节送礼'）")
    parser_full.add_argument("--base-topics", type=int, default=10, help="基础选题数量（默认10）")
    parser_full.add_argument("--fission", type=int, default=5, help="每个选题裂变数（默认5）")
    parser_full.add_argument("--target-count", type=int, default=18, help="目标数量（默认18）")
    parser_full.add_argument("--passing-line", type=int, default=25, help="及格分数线（默认25）")
    parser_full.add_argument("--focus-viral", action="store_true", help="优先爆款潜力")
    parser_full.add_argument("--brand-integration", choices=["soft", "medium", "hard"], default="soft", help="品牌植入程度")
    parser_full.add_argument("--output", "-o", help="输出目录")

    args = parser.parse_args()

    # 执行命令
    if args.command == "topic-pool":
        cmd_topic_pool(args)
    elif args.command == "rate":
        cmd_rate(args)
    elif args.command == "scripts":
        cmd_scripts(args)
    elif args.command == "full-pipeline":
        cmd_full_pipeline(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

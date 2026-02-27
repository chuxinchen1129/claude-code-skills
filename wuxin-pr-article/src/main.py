#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
悟昕公关文章生成器 - CLI 入口

支持功能：
1. 品牌背书文 (brand-story)
2. 行业洞察文 (industry-insight)
3. 用户故事文 (user-story)
4. 媒体稿件 (media-release)

Usage:
    python main.py brand-story
    python main.py industry-insight --topic "睡眠科技趋势"
    python main.py user-story --audience "职场人士"
    python main.py media-release --event "新品发布"
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# 导入生成器模块
from generator import (
    generate_brand_story,
    generate_industry_insight,
    generate_user_story,
    generate_media_release,
    save_article_to_markdown
)

# ==================== 配置 ====================

DEFAULT_OUTPUT_DIR = Path("./output")
PROJECT_ROOT = Path(__file__).parent.parent


# ==================== CLI 命令 ====================

def cmd_brand_story(args):
    """
    生成品牌背书文
    """
    print(f"\n{'='*60}")
    print(f"公关文章 - 品牌背书文")
    print(f"{'='*60}")

    article = generate_brand_story()

    print(f"\n✅ 生成完成")
    print(f"  字数: {len(article)}")
    print(f"  标题: 悟昕 Zenoasis：重新定义科学睡眠管理")

    # 保存
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"brand_story_{today}.md"
    md_path = save_article_to_markdown(article, output_dir, filename)

    print(f"\n📁 已保存: {md_path}")

    return article


def cmd_industry_insight(args):
    """
    生成行业洞察文
    """
    print(f"\n{'='*60}")
    print(f"公关文章 - 行业洞察文")
    print(f"{'='*60}")
    print(f"主题: {args.topic}")

    article = generate_industry_insight(args.topic)

    print(f"\n✅ 生成完成")
    print(f"  字数: {len(article)}")
    print(f"  标题: 睡眠科技新纪元：数据驱动的睡眠管理革命")

    # 保存
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    today = datetime.now().strftime("%Y-%m-%d")
    topic_safe = args.topic.replace(" ", "_").replace("/", "_")
    filename = f"industry_insight_{topic_safe}_{today}.md"
    md_path = save_article_to_markdown(article, output_dir, filename)

    print(f"\n📁 已保存: {md_path}")

    return article


def cmd_user_story(args):
    """
    生成用户故事文
    """
    print(f"\n{'='*60}")
    print(f"公关文章 - 用户故事文")
    print(f"{'='*60}")
    print(f"目标受众: {args.audience}")

    article = generate_user_story(args.audience)

    print(f"\n✅ 生成完成")
    print(f"  字数: {len(article)}")
    print(f"  标题: 从凌晨3点的焦虑到一夜好眠")

    # 保存
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    today = datetime.now().strftime("%Y-%m-%d")
    audience_safe = args.audience.replace(" ", "_")
    filename = f"user_story_{audience_safe}_{today}.md"
    md_path = save_article_to_markdown(article, output_dir, filename)

    print(f"\n📁 已保存: {md_path}")

    return article


def cmd_media_release(args):
    """
    生成媒体稿件
    """
    print(f"\n{'='*60}")
    print(f"公关文章 - 媒体稿件")
    print(f"{'='*60}")
    print(f"事件: {args.event}")

    article = generate_media_release(args.event, args.angle)

    print(f"\n✅ 生成完成")
    print(f"  字数: {len(article)}")

    # 保存
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    today = datetime.now().strftime("%Y-%m-%d")
    event_safe = args.event.replace(" ", "_").replace("/", "_")
    filename = f"media_release_{event_safe}_{today}.md"
    md_path = save_article_to_markdown(article, output_dir, filename)

    print(f"\n📁 已保存: {md_path}")

    return article


# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(
        description="悟昕公关文章生成器 v1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成品牌背书文
  python main.py brand-story

  # 生成行业洞察文
  python main.py industry-insight --topic "睡眠科技趋势"

  # 生成用户故事文
  python main.py user-story --audience "职场人士"

  # 生成媒体稿件
  python main.py media-release --event "新品发布" --angle "推出新款睡眠监测设备"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ---------- brand-story ----------
    parser_brand = subparsers.add_parser("brand-story", help="生成品牌背书文")
    parser_brand.add_argument("--output", "-o", help="输出目录")

    # ---------- industry-insight ----------
    parser_insight = subparsers.add_parser("industry-insight", help="生成行业洞察文")
    parser_insight.add_argument("--topic", default="睡眠科技趋势", help="文章主题")
    parser_insight.add_argument("--output", "-o", help="输出目录")

    # ---------- user-story ----------
    parser_user = subparsers.add_parser("user-story", help="生成用户故事文")
    parser_user.add_argument("--audience", default="职场人士", help="目标受众")
    parser_user.add_argument("--output", "-o", help="输出目录")

    # ---------- media-release ----------
    parser_media = subparsers.add_parser("media-release", help="生成媒体稿件")
    parser_media.add_argument("--event", required=True, help="新闻事件")
    parser_media.add_argument("--angle", help="品牌角度/立场")
    parser_media.add_argument("--output", "-o", help="输出目录")

    args = parser.parse_args()

    # 执行命令
    if args.command == "brand-story":
        cmd_brand_story(args)
    elif args.command == "industry-insight":
        cmd_industry_insight(args)
    elif args.command == "user-story":
        cmd_user_story(args)
    elif args.command == "media-release":
        cmd_media_release(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

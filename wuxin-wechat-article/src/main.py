#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
悟昕公众号文章生成器 - CLI 入口

支持功能：
1. 科普长文 (science-article)
2. 故事型文章 (story-article)
3. 清单型文章 (list-article)
4. 问答型文章 (qna-article)

Usage:
    python main.py science-article --topic "深睡" --depth 2000
    python main.py story-article --scene "失眠" --persona "职场人士"
    python main.py list-article --topic "睡眠误区" --count 10
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# 导入生成器模块
from generator import (
    generate_science_article,
    generate_story_article,
    generate_list_article,
    save_article_to_markdown
)

# ==================== 配置 ====================

DEFAULT_OUTPUT_DIR = Path("./output")
PROJECT_ROOT = Path(__file__).parent.parent


# ==================== CLI 命令 ====================

def cmd_science_article(args):
    """
    生成科普长文
    """
    print(f"\n{'='*60}")
    print(f"公众号文章 - 科普长文")
    print(f"{'='*60}")
    print(f"主题: {args.topic}")
    print(f"目标字数: {args.depth}")

    article = generate_science_article(args.topic, args.depth)

    print(f"\n✅ 生成完成")
    print(f"  字数: {len(article)}")
    print(f"  标题: {args.topic}的秘密：90%的人都不知道的睡眠真相")

    # 保存
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    today = datetime.now().strftime("%Y-%m-%d")
    topic_safe = args.topic.replace(" ", "_")
    filename = f"science_article_{topic_safe}_{today}.md"
    md_path = save_article_to_markdown(article, output_dir, filename)

    print(f"\n📁 已保存: {md_path}")

    return article


def cmd_story_article(args):
    """
    生成故事型文章
    """
    print(f"\n{'='*60}")
    print(f"公众号文章 - 故事型文章")
    print(f"{'='*60}")
    print(f"场景: {args.scene}")
    print(f"人物设定: {args.persona}")

    article = generate_story_article(args.scene, args.persona)

    print(f"\n✅ 生成完成")
    print(f"  字数: {len(article)}")
    print(f"  标题: 凌晨3点的朋友圈，藏着多少成年人的崩溃与自救")

    # 保存
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    today = datetime.now().strftime("%Y-%m-%d")
    scene_safe = args.scene.replace(" ", "_")
    filename = f"story_article_{scene_safe}_{today}.md"
    md_path = save_article_to_markdown(article, output_dir, filename)

    print(f"\n📁 已保存: {md_path}")

    return article


def cmd_list_article(args):
    """
    生成清单型文章
    """
    print(f"\n{'='*60}")
    print(f"公众号文章 - 清单型文章")
    print(f"{'='*60}")
    print(f"主题: {args.topic}")
    print(f"清单数量: {args.count}")

    article = generate_list_article(args.topic, args.count)

    print(f"\n✅ 生成完成")
    print(f"  字数: {len(article)}")
    print(f"  标题: {args.count}个睡眠误区，90%的人还在信！")

    # 保存
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    today = datetime.now().strftime("%Y-%m-%d")
    topic_safe = args.topic.replace(" ", "_")
    filename = f"list_article_{topic_safe}_{today}.md"
    md_path = save_article_to_markdown(article, output_dir, filename)

    print(f"\n📁 已保存: {md_path}")

    return article


# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(
        description="悟昕公众号文章生成器 v1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成科普长文
  python main.py science-article --topic "深睡" --depth 2000

  # 生成故事型文章
  python main.py story-article --scene "失眠" --persona "职场人士"

  # 生成清单型文章
  python main.py list-article --topic "睡眠误区" --count 10
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ---------- science-article ----------
    parser_science = subparsers.add_parser("science-article", help="生成科普长文")
    parser_science.add_argument("--topic", default="深睡", help="文章主题（深睡/失眠）")
    parser_science.add_argument("--depth", type=int, default=2000, help="目标字数")
    parser_science.add_argument("--output", "-o", help="输出目录")

    # ---------- story-article ----------
    parser_story = subparsers.add_parser("story-article", help="生成故事型文章")
    parser_story.add_argument("--scene", default="失眠", help="故事场景")
    parser_story.add_argument("--persona", default="职场人士", help="人物设定")
    parser_story.add_argument("--output", "-o", help="输出目录")

    # ---------- list-article ----------
    parser_list = subparsers.add_parser("list-article", help="生成清单型文章")
    parser_list.add_argument("--topic", default="睡眠误区", help="清单主题")
    parser_list.add_argument("--count", type=int, default=10, help="清单数量")
    parser_list.add_argument("--output", "-o", help="输出目录")

    args = parser.parse_args()

    # 执行命令
    if args.command == "science-article":
        cmd_science_article(args)
    elif args.command == "story-article":
        cmd_story_article(args)
    elif args.command == "list-article":
        cmd_list_article(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

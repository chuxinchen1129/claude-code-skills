#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
悟昕内容生成套件 - 统一CLI入口

支持4种内容类型的快速生成：
- 视频脚本 (script)
- 科普图文 (xhs)
- 公关文章 (pr)
- 公众号文章 (wechat)

Usage:
    python cli.py generate --type script --node "常规投放" --count 18
    python cli.py generate --type xhs --days 7
    python cli.py generate --type pr --article-type brand-story
    python cli.py generate --type wechat --topic "深睡"
"""

import argparse
import sys
from pathlib import Path
import subprocess
import os


# ==================== 配置 ====================

SCRIPTS_BASE = Path(__file__).parent.parent
DEFAULT_OUTPUT = Path("./output")


# ==================== 子技能路径 ====================

SUB_SKILLS = {
    "script": {
        "name": "视频脚本生成器",
        "path": SCRIPTS_BASE / "wuxin-script-generator",
        "main": "src/main.py"
    },
    "xhs": {
        "name": "科普图文生成器",
        "path": SCRIPTS_BASE / "wuxin-xhs-content",
        "main": "src/main.py"
    },
    "pr": {
        "name": "公关文章生成器",
        "path": SCRIPTS_BASE / "wuxin-pr-article",
        "main": "src/main.py"
    },
    "wechat": {
        "name": "公众号文章生成器",
        "path": SCRIPTS_BASE / "wuxin-wechat-article",
        "main": "src/main.py"
    }
}


# ==================== 生成函数 ====================

def generate_script(args):
    """
    生成视频脚本
    """
    skill = SUB_SKILLS["script"]
    main_py = skill["path"] / skill["main"]

    if not main_py.exists():
        print(f"❌ 找不到生成器: {main_py}")
        return None

    # 构建命令
    cmd = [
        sys.executable,
        str(main_py),
        "full-pipeline",
        "--node", args.node,
        "--target-count", str(args.count)
    ]

    if args.output:
        cmd.extend(["--output", args.output])

    print(f"\n{'='*60}")
    print(f"调用: {skill['name']}")
    print(f"{'='*60}")
    print(f"营销节点: {args.node}")
    print(f"目标数量: {args.count}")
    print(f"\n执行命令:")
    print(f"  {' '.join(cmd)}\n")

    # 执行
    result = subprocess.run(cmd, cwd=skill["path"])
    return result.returncode == 0


def generate_xhs(args):
    """
    生成科普图文
    """
    skill = SUB_SKILLS["xhs"]
    main_py = skill["path"] / skill["main"]

    if not main_py.exists():
        print(f"❌ 找不到生成器: {main_py}")
        return None

    # 计算日期范围
    from datetime import datetime, timedelta
    end = datetime.now()
    start = end - timedelta(days=args.days)

    # 构建命令
    cmd = [
        sys.executable,
        str(main_py),
        "batch",
        "--node", args.node,
        "--start-date", start.strftime("%Y-%m-%d"),
        "--end-date", end.strftime("%Y-%m-%d")
    ]

    if args.output:
        cmd.extend(["--output", args.output])

    print(f"\n{'='*60}")
    print(f"调用: {skill['name']}")
    print(f"{'='*60}")
    print(f"营销节点: {args.node}")
    print(f"日期范围: {args.days}天")
    print(f"\n执行命令:")
    print(f"  {' '.join(cmd)}\n")

    # 执行
    result = subprocess.run(cmd, cwd=skill["path"])
    return result.returncode == 0


def generate_pr(args):
    """
    生成公关文章
    """
    skill = SUB_SKILLS["pr"]
    main_py = skill["path"] / skill["main"]

    if not main_py.exists():
        print(f"❌ 找不到生成器: {main_py}")
        return None

    # 构建命令
    cmd = [sys.executable, str(main_py), args.article_type]

    if args.output:
        cmd.extend(["--output", args.output])

    # 根据文章类型添加参数
    if args.article_type == "industry-insight" and args.topic:
        cmd.extend(["--topic", args.topic])
    elif args.article_type == "user-story" and args.audience:
        cmd.extend(["--audience", args.audience])
    elif args.article_type == "media-release" and args.event:
        cmd.extend(["--event", args.event])
        if args.angle:
            cmd.extend(["--angle", args.angle])

    print(f"\n{'='*60}")
    print(f"调用: {skill['name']}")
    print(f"{'='*60}")
    print(f"文章类型: {args.article_type}")
    print(f"\n执行命令:")
    print(f"  {' '.join(cmd)}\n")

    # 执行
    result = subprocess.run(cmd, cwd=skill["path"])
    return result.returncode == 0


def generate_wechat(args):
    """
    生成公众号文章
    """
    skill = SUB_SKILLS["wechat"]
    main_py = skill["path"] / skill["main"]

    if not main_py.exists():
        print(f"❌ 找不到生成器: {main_py}")
        return None

    # 构建命令
    cmd = [sys.executable, str(main_py), args.article_type]

    if args.output:
        cmd.extend(["--output", args.output])

    # 根据文章类型添加参数
    if args.article_type == "science-article" and args.topic:
        cmd.extend(["--topic", args.topic])
        if args.depth:
            cmd.extend(["--depth", str(args.depth)])
    elif args.article_type == "story-article":
        if args.scene:
            cmd.extend(["--scene", args.scene])
        if args.persona:
            cmd.extend(["--persona", args.persona])
    elif args.article_type == "list-article":
        if args.topic:
            cmd.extend(["--topic", args.topic])
        if args.count:
            cmd.extend(["--count", str(args.count)])

    print(f"\n{'='*60}")
    print(f"调用: {skill['name']}")
    print(f"{'='*60}")
    print(f"文章类型: {args.article_type}")
    print(f"\n执行命令:")
    print(f"  {' '.join(cmd)}\n")

    # 执行
    result = subprocess.run(cmd, cwd=skill["path"])
    return result.returncode == 0


# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(
        description="悟昕内容生成套件 v1.0 - 统一入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
内容类型:
  script    视频脚本生成器（30秒4段式，Excel输出）
  xhs       科普图文生成器（小红书风格，CSV输出）
  pr        公关文章生成器（正式公文，Markdown输出）
  wechat    公众号文章生成器（长文深度，Markdown输出）

示例:
  # 生成视频脚本
  python cli.py generate --type script --node "常规投放" --count 18

  # 生成科普图文
  python cli.py generate --type xhs --node "常规投放" --days 7

  # 生成公关文章
  python cli.py generate --type pr --article-type brand-story

  # 生成公众号文章
  python cli.py generate --type wechat --article-type science-article --topic "深睡"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ---------- generate ----------
    parser_gen = subparsers.add_parser("generate", help="生成内容")

    # 通用参数
    parser_gen.add_argument("--type", required=True,
                          choices=["script", "xhs", "pr", "wechat"],
                          help="内容类型")
    parser_gen.add_argument("--output", "-o", help="输出目录")

    # 视频脚本参数
    parser_gen.add_argument("--node", help="营销节点（用于script和xhs）")
    parser_gen.add_argument("--count", type=int, default=18, help="脚本数量（用于script）")

    # 科普图文参数
    parser_gen.add_argument("--days", type=int, default=7, help="生成天数（用于xhs）")

    # 公关文章参数
    parser_gen.add_argument("--article-type",
                          choices=["brand-story", "industry-insight", "user-story", "media-release"],
                          help="文章类型（用于pr和wechat）")
    parser_gen.add_argument("--topic", help="文章主题")
    parser_gen.add_argument("--audience", help="目标受众（用于user-story）")
    parser_gen.add_argument("--event", help="新闻事件（用于media-release）")
    parser_gen.add_argument("--angle", help="品牌角度（用于media-release）")
    parser_gen.add_argument("--scene", help="故事场景（用于story-article）")
    parser_gen.add_argument("--persona", help="人物设定（用于story-article）")
    parser_gen.add_argument("--depth", type=int, help="目标字数（用于science-article）")
    parser_gen.add_argument("--count-list", type=int, help="清单数量（用于list-article）")

    # ---------- info ----------
    parser_info = subparsers.add_parser("info", help="显示套件信息")

    args = parser.parse_args()

    # 执行命令
    if args.command == "generate":
        if args.type == "script":
            return generate_script(args)
        elif args.type == "xhs":
            return generate_xhs(args)
        elif args.type == "pr":
            return generate_pr(args)
        elif args.type == "wechat":
            return generate_wechat(args)
    elif args.command == "info":
        print(f"\n{'='*60}")
        print(f"悟昕内容生成套件 v1.0")
        print(f"{'='*60}\n")
        print(f"支持的内容类型:\n")
        for key, skill in SUB_SKILLS.items():
            print(f"  {key:8} - {skill['name']}")
            print(f"           路径: {skill['path']}")
        print(f"\n共享资源: 03_WUXIN_CONTENT/assets/")
        print(f"\n使用 'python cli.py generate --type <type> --help' 查看具体参数\n")
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main() if main() is not None else 1)

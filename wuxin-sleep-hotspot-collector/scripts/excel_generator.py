#!/usr/bin/env python3
"""
Excel 报告生成器

功能：
1. 读取 JSON 数据
2. 生成格式化的 Excel 表格
3. 包含多个工作表（数据、分析、统计）

依赖：
- openpyxl
- xlsxwrite（可选）

作者：大秘书系统
版本：v1.0.0
创建时间：2026-02-10
"""

import json
import os
from datetime import datetime
from pathlib import Path
import argparse
from collections import Counter


class ExcelGenerator:
    """Excel 报告生成器"""

    def __init__(self, output_dir=None):
        """初始化生成器

        Args:
            output_dir: 输出目录
        """
        self.skill_dir = Path(__file__).parent.parent
        self.data_dir = self.skill_dir / "data"

        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = self.data_dir / "weekly_reports" / datetime.now().strftime("%Y-%m-%d")

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_posts(self):
        """加载采集的笔记数据

        Returns:
            list: 笔记列表
        """
        all_posts = []

        # 从小红书采集目录加载
        xhs_dir = self.data_dir / "xiaohongshu_collection"
        if xhs_dir.exists():
            for date_dir in xhs_dir.iterdir():
                if date_dir.is_dir():
                    raw_data_file = date_dir / "raw_data" / "posts.json"
                    if raw_data_file.exists():
                        with open(raw_data_file, "r", encoding="utf-8") as f:
                            posts = json.load(f)
                            all_posts.extend(posts)

        # 从飞书输入目录加载
        input_dir = self.data_dir / "feishu_input"
        if input_dir.exists():
            for session_dir in input_dir.iterdir():
                if session_dir.is_dir():
                    for content_file in session_dir.glob("content/*.json"):
                        with open(content_file, "r", encoding="utf-8") as f:
                            post = json.load(f)
                            all_posts.append(post)

        return all_posts

    def generate_csv_data(self, posts):
        """生成 CSV 格式数据

        Args:
            posts: 笔记列表

        Returns:
            str: CSV 格式字符串
        """
        # CSV 表头
        headers = [
            "ID", "标题", "作者", "点赞数", "评论数", "收藏数",
            "类型", "发布时间", "来源关键词", "笔记链接"
        ]

        # 生成 CSV 行
        csv_lines = [",".join(headers)]

        for post in posts:
            # 处理标题中的引号
            title = post.get("title", "").replace('"', '""')
            row = [
                post.get("id", ""),
                f'"{title}"',  # 处理引号
                post.get("author", ""),
                str(post.get("likes", 0)),
                str(post.get("comments", 0)),
                str(post.get("collects", 0)),
                post.get("type", ""),
                post.get("time", ""),
                post.get("source_keyword", ""),
                post.get("note_url", ""),
            ]
            csv_lines.append(",".join(row))

        return "\n".join(csv_lines)

    def generate_analysis_data(self, posts):
        """生成分析数据

        Args:
            posts: 笔记列表

        Returns:
            dict: 分析数据
        """
        # 统计数据
        total_likes = sum(p.get("likes", 0) for p in posts)
        total_comments = sum(p.get("comments", 0) for p in posts)
        total_collects = sum(p.get("collects", 0) for p in posts)

        # 类型分布
        type_dist = Counter(p.get("type", "unknown") for p in posts)

        # 爆款笔记（>1000赞）
        trending = [p for p in posts if p.get("likes", 0) > 1000]

        # TOP10
        top10 = sorted(
            posts,
            key=lambda x: x.get("likes", 0) + x.get("comments", 0) + x.get("collects", 0),
            reverse=True
        )[:10]

        return {
            "total_posts": len(posts),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_collects": total_collects,
            "avg_likes": total_likes // len(posts) if posts else 0,
            "avg_comments": total_comments // len(posts) if posts else 0,
            "avg_collects": total_collects // len(posts) if posts else 0,
            "trending_count": len(trending),
            "type_distribution": dict(type_dist),
            "top10": top10,
        }

    def generate_excel_csv(self, posts):
        """生成 Excel（CSV 格式）

        由于直接生成 xlsx 需要 openpyxl 库，这里先生成 CSV 格式
        可以用 Excel 打开

        Args:
            posts: 笔记列表

        Returns:
            str: 生成的文件路径
        """
        # 1. 生成主数据表
        csv_data = self.generate_csv_data(posts)
        data_file = self.output_dir / "小红书数据表.csv"
        with open(data_file, "w", encoding="utf-8-sig") as f:
            f.write(csv_data)
        print(f"✓ 数据表已生成: {data_file}")

        # 2. 生成分析数据
        analysis = self.generate_analysis_data(posts)

        # 分析数据 CSV
        analysis_headers = ["指标", "数值"]
        analysis_rows = [
            ["总笔记数", analysis["total_posts"]],
            ["总点赞数", analysis["total_likes"]],
            ["总评论数", analysis["total_comments"]],
            ["总收藏数", analysis["total_collects"]],
            ["平均点赞数", analysis["avg_likes"]],
            ["平均评论数", analysis["avg_comments"]],
            ["平均收藏数", analysis["avg_collects"]],
            ["爆款笔记数（>1000赞）", analysis["trending_count"]],
        ]

        analysis_csv = "\n".join([
            ",".join(analysis_headers),
            *[f"{row[0]},{row[1]}" for row in analysis_rows]
        ])

        analysis_file = self.output_dir / "数据分析.csv"
        with open(analysis_file, "w", encoding="utf-8-sig") as f:
            f.write(analysis_csv)
        print(f"✓ 分析数据已生成: {analysis_file}")

        # 3. 生成 TOP10 表
        top10_headers = ["排名", "标题", "作者", "点赞数", "评论数", "收藏数", "总互动"]
        top10_rows = []
        for i, post in enumerate(analysis["top10"], 1):
            total = post.get("likes", 0) + post.get("comments", 0) + post.get("collects", 0)
            # 处理标题中的引号
            title = post.get("title", "").replace('"', '""')
            top10_rows.append([
                str(i),
                f'"{title}"',
                post.get("author", ""),
                str(post.get("likes", 0)),
                str(post.get("comments", 0)),
                str(post.get("collects", 0)),
                str(total),
            ])

        top10_csv = "\n".join([
            ",".join(top10_headers),
            *[",".join(row) for row in top10_rows]
        ])

        top10_file = self.output_dir / "TOP10爆款笔记.csv"
        with open(top10_file, "w", encoding="utf-8-sig") as f:
            f.write(top10_csv)
        print(f"✓ TOP10 数据已生成: {top10_file}")

        return str(data_file)

    def generate_markdown_table(self, posts):
        """生成 Markdown 表格

        Args:
            posts: 笔记列表

        Returns:
            str: Markdown 表格字符串
        """
        analysis = self.generate_analysis_data(posts)

        # 数据概览表
        overview_table = """### 📊 数据概览

| 指标 | 数值 |
|------|------|
| 总笔记数 | {total_posts} |
| 总点赞数 | {total_likes:,} |
| 总评论数 | {total_comments:,} |
| 总收藏数 | {total_collects:,} |
| 平均点赞数 | {avg_likes:,} |
| 平均评论数 | {avg_comments:,} |
| 平均收藏数 | {avg_collects:,} |
| 爆款笔记数（>1000赞） | {trending_count} |

""".format(**analysis)

        # TOP10 表
        top10_table = "### 🔥 TOP10 爆款笔记\n\n"
        top10_table += "| 排名 | 标题 | 作者 | 点赞 | 评论 | 收藏 | 总互动 |\n"
        top10_table += "|------|------|------|------|------|------|--------|\n"

        for i, post in enumerate(analysis["top10"], 1):
            title = post.get("title", "")[:30] + "..." if len(post.get("title", "")) > 30 else post.get("title", "")
            total = post.get("likes", 0) + post.get("comments", 0) + post.get("collects", 0)
            top10_table += f"| {i} | {title} | {post.get('author', '')} | {post.get('likes', 0):,} | {post.get('comments', 0):,} | {post.get('collects', 0):,} | {total:,} |\n"

        return overview_table + top10_table

    def generate(self, input_file=None):
        """生成 Excel 报告

        Args:
            input_file: 输入 JSON 文件路径（可选）

        Returns:
            str: 生成的文件路径
        """
        print("开始生成 Excel 报告...")

        # 加载数据
        if input_file:
            with open(input_file, "r", encoding="utf-8") as f:
                posts = json.load(f)
        else:
            posts = self.load_posts()

        if not posts:
            print("⚠️  没有数据")
            return None

        print(f"✓ 加载了 {len(posts)} 条笔记")

        # 生成 CSV 格式
        csv_file = self.generate_excel_csv(posts)

        # 生成 Markdown 表格（附加到报告）
        md_table = self.generate_markdown_table(posts)

        # 保存 Markdown 表格
        md_file = self.output_dir / "数据表格.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_table)
        print(f"✓ Markdown 表格已生成: {md_file}")

        print(f"\n✓ 报告生成完成！")
        print(f"✓ 输出目录: {self.output_dir}")

        return csv_file


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Excel 报告生成器")
    parser.add_argument("--input", help="输入 JSON 文件路径")
    parser.add_argument("--output", help="输出目录路径")

    args = parser.parse_args()

    generator = ExcelGenerator(output_dir=args.output)
    generator.generate(input_file=args.input)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
本地搜索工具

用于在本地文件系统中搜索品牌资料、范文、模板等资源。
支持按关键词、文件类型、目录范围进行搜索。

Usage:
    python local_search.py [keyword] [options]
"""

import os
import re
from pathlib import Path
from datetime import datetime
import argparse


def search_files(keyword, directory=None, file_pattern="*.md", case_sensitive=False):
    """
    搜索包含关键词的文件

    Args:
        keyword: 搜索关键词
        directory: 搜索目录（默认为技能根目录）
        file_pattern: 文件匹配模式（默认 *.md）
        case_sensitive: 是否区分大小写

    Returns:
        匹配的文件列表，包含文件路径和匹配行
    """
    if directory is None:
        # 默认搜索技能目录
        script_dir = Path(__file__).parent.parent
        directory = script_dir
    else:
        directory = Path(directory)

    results = []
    flags = 0 if case_sensitive else re.IGNORECASE

    # 递归搜索文件
    for file_path in directory.rglob(file_pattern):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            matches = []
            for line_num, line in enumerate(lines, 1):
                if re.search(keyword, line, flags):
                    matches.append({
                        'line_num': line_num,
                        'content': line.strip(),
                        'keyword_found': True
                    })

            if matches:
                results.append({
                    'file_path': str(file_path.relative_to(directory)),
                    'absolute_path': str(file_path),
                    'matches': matches,
                    'match_count': len(matches)
                })
        except Exception as e:
            # 跳过无法读取的文件（如二进制文件）
            continue

    return results


def search_brand_profiles(brand_name=None):
    """
    搜索品牌档案

    Args:
        brand_name: 品牌名称（可选）

    Returns:
        品牌档案列表
    """
    script_dir = Path(__file__).parent.parent
    brand_dir = script_dir / "assets" / "brand_profiles"

    if not brand_dir.exists():
        return []

    results = []
    for file_path in brand_dir.glob("*.md"):
        if file_path.name.startswith("_"):
            continue

        if brand_name and brand_name.lower() not in file_path.name.lower():
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取关键信息
            info = {
                'file_name': file_path.name,
                'file_path': str(file_path),
                'brand_name': file_path.stem,
                'size': len(content),
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime)
            }

            # 尝试提取品牌名称和描述
            name_match = re.search(r'品牌名称[：:]\s*(.+)', content)
            if name_match:
                info['brand_cn_name'] = name_match.group(1).strip()

            desc_match = re.search(r'品牌定位[：:]\s*(.+)', content)
            if desc_match:
                info['positioning'] = desc_match.group(1).strip()

            results.append(info)
        except Exception:
            continue

    return results


def search_samples(category=None):
    """
    搜索范文

    Args:
        category: 类别（brand_story, science_popular等）

    Returns:
        范文列表
    """
    script_dir = Path(__file__).parent.parent
    samples_dir = script_dir / "assets" / "samples"

    if not samples_dir.exists():
        return []

    results = []
    for file_path in samples_dir.glob("*.md"):
        if file_path.name.startswith("_"):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            info = {
                'file_name': file_path.name,
                'file_path': str(file_path),
                'size': len(content),
                'title': file_path.stem
            }

            # 提取标题
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                info['title'] = title_match.group(1).strip()

            # 分类
            if 'brand_story' in file_path.name or '品牌故事' in content:
                info['category'] = '品牌故事'
            elif 'science' in file_path.name or '科普' in content:
                info['category'] = '科普文章'
            elif 'business' in file_path.name or '商业' in content:
                info['category'] = '商业分析'

            results.append(info)
        except Exception:
            continue

    return results


def generate_search_report(results, keyword, output_format="text"):
    """
    生成搜索报告

    Args:
        results: 搜索结果
        keyword: 搜索关键词
        output_format: 输出格式（text/markdown）

    Returns:
        格式化的报告
    """
    if output_format == "markdown":
        return generate_markdown_report(results, keyword)
    else:
        return generate_text_report(results, keyword)


def generate_text_report(results, keyword):
    """生成文本格式报告"""
    report = []
    report.append("=" * 80)
    report.append(f"本地搜索结果报告")
    report.append(f"搜索关键词: {keyword}")
    report.append(f"搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"找到 {len(results)} 个匹配文件")
    report.append("=" * 80)
    report.append("")

    for idx, result in enumerate(results, 1):
        report.append(f"[{idx}] {result['file_path']}")
        report.append(f"    匹配数: {result['match_count']}")
        report.append("")

        for match in result['matches'][:5]:  # 只显示前5个匹配
            report.append(f"    行{match['line_num']}: {match['content'][:100]}")

        if result['match_count'] > 5:
            report.append(f"    ... 还有 {result['match_count'] - 5} 个匹配")

        report.append("")

    return "\n".join(report)


def generate_markdown_report(results, keyword):
    """生成Markdown格式报告"""
    lines = []
    lines.append("# 本地搜索结果报告\n")
    lines.append(f"**搜索关键词**: {keyword}\n")
    lines.append(f"**搜索时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**匹配文件数**: {len(results)}\n")
    lines.append("---\n")

    for idx, result in enumerate(results, 1):
        lines.append(f"## {idx}. {result['file_path']}\n")
        lines.append(f"**匹配数**: {result['match_count']}\n")
        lines.append(f"**绝对路径**: `{result['absolute_path']}`\n")
        lines.append("\n### 匹配内容\n")

        for match in result['matches'][:5]:
            lines.append(f"**行{match['line_num']}**: {match['content']}")

        if result['match_count'] > 5:
            lines.append(f"\n*... 还有 {result['match_count'] - 5} 个匹配*")

        lines.append("\n---\n")

    return "\n".join(lines)


def save_report(content, output_dir=None, filename=None):
    """保存报告到文件"""
    if output_dir is None:
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / "assets" / "output" / "research"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"local_search_{timestamp}.md"

    filepath = output_dir / filename
    filepath.write_text(content, encoding='utf-8')

    return filepath


def main():
    """命令行交互式使用"""
    parser = argparse.ArgumentParser(description='本地搜索工具')
    parser.add_argument('keyword', nargs='?', help='搜索关键词')
    parser.add_argument('-d', '--directory', help='搜索目录')
    parser.add_argument('-p', '--pattern', default='*.md', help='文件模式（默认 *.md）')
    parser.add_argument('-c', '--case-sensitive', action='store_true', help='区分大小写')
    parser.add_argument('-o', '--output', help='输出文件')
    parser.add_argument('-f', '--format', choices=['text', 'markdown'], default='markdown', help='输出格式')
    parser.add_argument('--brand', help='搜索品牌档案')
    parser.add_argument('--samples', action='store_true', help='搜索范文')
    parser.add_argument('--interactive', action='store_true', help='交互式模式')

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if args.brand:
        # 搜索品牌档案
        results = search_brand_profiles(args.brand)
        print(f"\n找到 {len(results)} 个品牌档案:\n")
        for info in results:
            print(f"📁 {info['file_name']}")
            if 'brand_cn_name' in info:
                print(f"   名称: {info['brand_cn_name']}")
            if 'positioning' in info:
                print(f"   定位: {info['positioning']}")
            print(f"   路径: {info['file_path']}")
            print()

    elif args.samples:
        # 搜索范文
        results = search_samples()
        print(f"\n找到 {len(results)} 个范文:\n")
        for info in results:
            print(f"📄 {info['file_name']}")
            print(f"   标题: {info['title']}")
            if 'category' in info:
                print(f"   分类: {info['category']}")
            print()

    elif args.keyword:
        # 关键词搜索
        print(f"\n正在搜索 '{args.keyword}'...\n")
        results = search_files(args.keyword, args.directory, args.pattern, args.case_sensitive)

        if not results:
            print("❌ 未找到匹配内容")
            return

        report = generate_search_report(results, args.keyword, args.format)
        print(report)

        if args.output:
            filepath = save_report(report, filename=args.output)
            print(f"\n✅ 报告已保存到: {filepath}")
        else:
            filepath = save_report(report)
            print(f"\n✅ 报告已自动保存到: {filepath}")

    else:
        parser.print_help()


def interactive_mode():
    """交互式搜索模式"""
    print("=" * 80)
    print("本地搜索工具 - 交互式模式")
    print("=" * 80)
    print()

    print("请选择搜索类型:")
    print("1. 关键词搜索")
    print("2. 品牌档案搜索")
    print("3. 范文搜索")
    print()

    choice = input("请输入选项 (1/2/3): ").strip()

    if choice == "1":
        keyword = input("请输入搜索关键词: ").strip()
        directory = input("搜索目录（留空表示当前技能目录）: ").strip() or None

        print(f"\n正在搜索 '{keyword}'...\n")
        results = search_files(keyword, directory)

        if results:
            report = generate_search_report(results, keyword, "markdown")
            print(report)
            filepath = save_report(report)
            print(f"\n✅ 报告已保存到: {filepath}")
        else:
            print("❌ 未找到匹配内容")

    elif choice == "2":
        brand_name = input("品牌名称（留空显示所有）: ").strip() or None
        results = search_brand_profiles(brand_name)

        print(f"\n找到 {len(results)} 个品牌档案:\n")
        for info in results:
            print(f"📁 {info['file_name']}")
            if 'brand_cn_name' in info:
                print(f"   名称: {info['brand_cn_name']}")
            if 'positioning' in info:
                print(f"   定位: {info['positioning']}")
            print()

    elif choice == "3":
        results = search_samples()

        print(f"\n找到 {len(results)} 个范文:\n")
        for info in results:
            print(f"📄 {info['file_name']}")
            print(f"   标题: {info['title']}")
            if 'category' in info:
                print(f"   分类: {info['category']}")
            print()

    else:
        print("❌ 无效选项")


if __name__ == "__main__":
    main()

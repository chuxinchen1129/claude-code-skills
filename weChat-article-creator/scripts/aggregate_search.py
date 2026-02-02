#!/usr/bin/env python3
"""
搜索结果聚合工具

将网络搜索结果格式化为结构化文档，
保存到 assets/output/research/ 目录。

Usage:
    python aggregate_search.py
"""

import json
import re
from pathlib import Path
from datetime import datetime


def format_search_result(query, search_results):
    """
    格式化搜索结果为结构化文档

    Args:
        query: 搜索关键词
        search_results: 搜索结果列表

    Returns:
        格式化后的 markdown 文档
    """
    md_content = f"# 搜索结果聚合报告\n\n"
    md_content += f"**搜索时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    md_content += f"**搜索关键词**: {query}\n\n"
    md_content += "---\n\n"

    # 按类别组织搜索结果
    categories = {
        "数据": [],
        "案例": [],
        "观点": [],
        "趋势": [],
        "其他": []
    }

    # 分类搜索结果
    for result in search_results:
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        url = result.get("url", "")

        # 根据标题和摘要判断类别
        category = categorize_result(title, snippet)
        categories[category].append({
            "title": title,
            "snippet": snippet,
            "url": url
        })

    # 生成各类别内容
    for category, items in categories.items():
        if items:
            md_content += f"## {category}\n\n"
            for idx, item in enumerate(items, 1):
                md_content += f"### {idx}. {item['title']}\n\n"
                md_content += f"{item['snippet']}\n\n"
                md_content += f"**来源**: {item['url']}\n\n"
                md_content += "---\n\n"

    return md_content


def categorize_result(title, snippet):
    """
    根据标题和摘要对搜索结果进行分类

    Args:
        title: 结果标题
        snippet: 结果摘要

    Returns:
        类别名称
    """
    content = (title + " " + snippet).lower()

    # 数据相关关键词
    data_keywords = ["报告", "研究", "数据", "调查", "统计", "%", "率", "亿", "万"]
    if any(kw in content for kw in data_keywords):
        return "数据"

    # 案例相关关键词
    case_keywords = ["案例", "故事", "经历", "分享", "我是", "如何", "怎么", "真实"]
    if any(kw in content for kw in case_keywords):
        return "案例"

    # 观点相关关键词
    opinion_keywords = ["专家", "教授", "分析", "认为", "观点", "看法", "建议"]
    if any(kw in content for kw in opinion_keywords):
        return "观点"

    # 趋势相关关键词
    trend_keywords = ["趋势", "未来", "发展", "新兴", "热点", "流行"]
    if any(kw in content for kw in trend_keywords):
        return "趋势"

    return "其他"


def save_research_report(content, output_dir=None):
    """
    保存研究报告到文件

    Args:
        content: markdown 内容
        output_dir: 输出目录路径

    Returns:
        保存的文件路径
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "assets" / "output" / "research"
    else:
        output_dir = Path(output_dir)

    # 确保目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件名（带时间戳）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"research_{timestamp}.md"
    filepath = output_dir / filename

    # 写入文件
    filepath.write_text(content, encoding='utf-8')

    return filepath


def extract_key_points(markdown_content):
    """
    从搜索结果中提取关键信息点

    Args:
        markdown_content: markdown 格式的搜索结果

    Returns:
        关键信息点列表
    """
    key_points = []

    # 按行分割
    lines = markdown_content.split('\n')

    for line in lines:
        line = line.strip()

        # 提取包含数字的行（通常包含数据）
        if re.search(r'\d+%|\d+万|\d+亿|\d+个|\d+种', line):
            if line and not line.startswith('#') and not line.startswith('*'):
                key_points.append(("数据", line))

        # 提取包含"认为"、"建议"等的专家观点
        if any(kw in line for kw in ["认为", "建议", "指出", "分析"]):
            if line and not line.startswith('#'):
                key_points.append(("观点", line))

    return key_points


def main():
    """
    主函数：命令行交互式使用
    """
    print("=== 搜索结果聚合工具 ===\n")

    # 获取搜索关键词
    query = input("请输入搜索关键词: ").strip()

    if not query:
        print("❌ 搜索关键词不能为空")
        return

    print(f"\n请从网络搜索结果中复制相关信息...")
    print("提示：粘贴搜索结果的标题、摘要和链接（一行一个结果，用空行分隔）\n")

    # 获取搜索结果
    print("请输入搜索结果（输入完成后输入 'END' 结束）:")

    search_results = []
    current_result = {}

    for line in input():
        line = line.strip()

        if line == 'END':
            if current_result:
                search_results.append(current_result)
            break

        if not line:
            if current_result:
                search_results.append(current_result)
                current_result = {}
            continue

        # 解析行内容
        if line.startswith('http'):
            current_result['url'] = line
        elif 'title' not in current_result:
            current_result['title'] = line
        else:
            current_result['snippet'] = line

    if not search_results:
        print("❌ 未输入搜索结果")
        return

    # 格式化搜索结果
    md_content = format_search_result(query, search_results)

    # 保存到文件
    filepath = save_research_report(md_content)

    print(f"\n✅ 搜索结果已保存到: {filepath}")

    # 提取并显示关键信息点
    key_points = extract_key_points(md_content)
    if key_points:
        print("\n=== 提取的关键信息点 ===")
        for category, point in key_points[:10]:  # 只显示前10个
            print(f"[{category}] {point[:80]}...")


if __name__ == "__main__":
    main()

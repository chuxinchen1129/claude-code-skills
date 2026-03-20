#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书批量内容生成模块

功能：基于营销日历和日期范围批量生成小红书科普图文
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional


# ==================== 营销日历 ====================

def load_marketing_calendar(calendar_path: Path) -> dict:
    """
    加载营销日历

    参数:
        calendar_path: CSV文件路径

    返回:
        营销日历数据 {日期: 营销节点}
    """
    if not calendar_path.exists():
        print(f"⚠️  营销日历不存在: {calendar_path}")
        print("使用默认营销节点: 常规投放")
        return {}

    df = pd.read_csv(calendar_path)
    calendar = {}

    for _, row in df.iterrows():
        date_str = row.get("日期", "")
        node = row.get("营销节点", "常规投放")
        if date_str:
            calendar[date_str] = node

    print(f"✅ 已加载营销日历: {len(calendar)}个节点")
    return calendar


def get_publishable_dates(
    start_date: str,
    end_date: str,
    publish_days: List[int] = None
) -> List[str]:
    """
    获取可发布日期（周一到周四）

    参数:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        publish_days: 发布日列表（1=周一, ..., 7=周日）

    返回:
        日期列表
    """
    if publish_days is None:
        publish_days = [1, 2, 3, 4]  # 周一到周四

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    dates = []
    current = start

    while current <= end:
        if current.weekday() + 1 in publish_days:  # datetime.weekday() 返回 0-6 (周一到周日)
            dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates


# ==================== 内容生成 ====================

def generate_xhs_content_for_date(
    date: str,
    marketing_node: str,
    science_concepts: List[Dict]
) -> Optional[Dict]:
    """
    为指定日期生成小红书内容

    参数:
        date: 发布日期
        marketing_node: 营销节点
        science_concepts: 科学概念库

    返回:
        内容字典或None
    """
    if not science_concepts:
        return None

    # 随机选择一个科学概念
    concept = science_concepts[len(date) % len(science_concepts)]

    # 基础内容结构（与单篇生成相同）
    from generator import generate_content_structure

    content = generate_content_structure(
        topic=concept.get("name", "睡眠质量"),
        audience="职场人士",
        pain_point=concept.get("pain_point", "睡眠不足"),
        angle=concept.get("solution", "改善睡眠"),
        science_concept=concept.get("name", "Sleep Quality")
    )

    # 添加日期和营销节点信息
    content["发布日期"] = date
    content["营销节点"] = marketing_node

    return content


def generate_xhs_batch(
    start_date: str,
    end_date: str,
    marketing_node: str = "常规投放",
    calendar_path: Optional[Path] = None,
    wiki_path: Optional[Path] = None
) -> List[Dict]:
    """
    批量生成小红书内容

    参数:
        start_date: 开始日期
        end_date: 结束日期
        marketing_node: 默认营销节点
        calendar_path: 营销日历路径
        wiki_path: 科学概念库路径

    返回:
        内容列表
    """
    # 加载营销日历
    calendar = {}
    if calendar_path:
        calendar = load_marketing_calendar(calendar_path)

    # 加载科学概念库
    concepts = []
    if wiki_path and wiki_path.exists():
        import json
        with open(wiki_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            concepts = data.get("concepts", [])

    if not concepts:
        # 默认概念库
        concepts = [
            {"name": "Deep Sleep", "pain_point": "深睡不足", "solution": "深睡质量提升"},
            {"name": "Sleep Pressure", "pain_point": "入睡困难", "solution": "科学助眠"},
            {"name": "Circadian Rhythm", "pain_point": "作息紊乱", "solution": "规律作息"}
        ]

    print(f"科学概念: {len(concepts)}个")

    # 获取发布日期
    dates = get_publishable_dates(start_date, end_date)
    print(f"发布日期: {len(dates)}个")

    # 为每个日期生成内容
    contents = []
    for date in dates:
        # 查找该日期的营销节点
        node = calendar.get(date, marketing_node)

        content = generate_xhs_content_for_date(
            date=date,
            marketing_node=node,
            science_concepts=concepts
        )

        if content:
            contents.append(content)

    return contents


def save_xhs_batch_to_csv(
    contents: List[Dict],
    output_dir: Path,
    filename: str
) -> Path:
    """
    保存批量内容到CSV

    参数:
        contents: 内容列表
        output_dir: 输出目录
        filename: 文件名

    返回:
        CSV文件路径
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / filename

    df = pd.DataFrame(contents)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    return csv_path

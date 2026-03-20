#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书科普图文生成模块

功能：基于睡眠科学 Wiki 生成小红书科普图文内容
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random


# ==================== 品牌规范 ====================

BRAND_TONE = [
    "温暖治愈",
    "科学循证",
    "优雅克制"
]

FORBIDDEN_WORDS = [
    "家人们", "绝绝子", "根治", "第一", "必需"
]

CORE_SELLING_POINTS = [
    "AI智能睡眠管理师",
    "医疗级EEG脑电监测",
    "监测-干预-反馈闭环",
    "FDA认证CES技术",
    "80%医疗级准确率",
    "缩短30%入睡时间",
    "睡眠质量改善75%以上"
]

# ==================== 内容结构 ====================

def generate_content_structure(
    topic: str,
    audience: str,
    pain_point: str,
    angle: str,
    science_concept: str
) -> Dict:
    """
    生成小红书科普图文的完整内容结构

    返回13字段标准格式
    """
    # 1. 生成SEO标题（15-20字）
    title = generate_seo_title(pain_point, angle)

    # 2. 生成封面大字（10-18字）
    cover_text = generate_cover_text(pain_point, angle)

    # 3. 生成开篇引入（30-50字）
    intro = generate_intro(pain_point, audience)

    # 4. 生成三个板块
    sections = generate_sections(pain_point, angle, science_concept)

    # 5. 生成产品植入（50-80字）
    product_cta = generate_product_cta(angle)

    # 6. 组装完整正文
    content_body = assemble_content(intro, sections, product_cta)

    return {
        "笔记标题": title,
        "封面大字": cover_text,
        "目标人群": audience,
        "核心痛点": pain_point,
        "营销切入角度": angle,
        "科学概念": science_concept,
        "板块1标题": sections[0]["title"],
        "板块1内容": sections[0]["content"],
        "板块2标题": sections[1]["title"],
        "板块2内容": sections[1]["content"],
        "板块3标题": sections[2]["title"],
        "板块3内容": sections[2]["content"],
        "完整正文": content_body,
        "字数统计": len(content_body)
    }


def generate_seo_title(pain_point: str, angle: str) -> str:
    """
    生成SEO优化的标题（15-20字）
    """
    templates = [
        f"{pain_point[:8]}？{angle[:8]}",
        f"原来{pain_point[:8]}是这么回事",
        f"{pain_point[:8]}？终于找到了",
        f"{angle[:10]}拯救了我的睡眠",
        f"90%的人都不知道的{pain_point[:6]}"
    ]
    title = random.choice(templates)
    return title[:20]


def generate_cover_text(pain_point: str, angle: str) -> str:
    """
    生成封面大字（10-18字）
    """
    templates = [
        f"{pain_point[:8]}？",
        f"{angle[:8]}有救了",
        f"你的{pain_point[:6]}还好吗？",
        f"科学{angle[:6]}指南",
        f"告别{pain_point[:6]}"
    ]
    cover = random.choice(templates)
    return cover[:18]


def generate_intro(pain_point: str, audience: str) -> str:
    """
    生成开篇引入（30-50字）
    """
    templates = [
        f"{audience}注意！{pain_point}真的太影响生活质量了😩",
        f"你是不是也有{pain_point}的困扰？{audience}看过来👋",
        f"{pain_point}？不是你的问题，是方法不对💡",
        f"作为{audience}，{pain_point}真的太常见了😔"
    ]
    return random.choice(templates)


def generate_sections(pain_point: str, angle: str, science_concept: str) -> List[Dict]:
    """
    生成三个内容板块

    每个板块：小标题（4-8字）+ 内容（150字）
    """
    # 板块主题选择
    themes = [
        {
            "title": f"{pain_point[:4]}真相",
            "content": f"很多人{pain_point}，其实是误解了睡眠原理。{science_concept}告诉我们，睡眠不是简单的休息，而是复杂的生理过程。大脑需要经历不同的睡眠阶段才能完成修复。"
        },
        {
            "title": f"{angle[:4]}方法",
            "content": f"科学研究表明，{angle}的关键在于建立规律作息。固定时间上床和起床，避免睡前蓝光刺激，创造舒适睡眠环境。这些小改变能显著提升睡眠质量。"
        },
        {
            "title": "效果看得见",
            "content": f"坚持{angle}2-3周，你会发现入睡时间缩短，深睡比例增加，白天精神状态明显改善。睡眠质量提升后，免疫力、情绪、专注力都会跟着变好。"
        }
    ]

    return themes


def generate_product_cta(angle: str) -> str:
    """
    生成产品植入（50-80字，超软性）
    """
    cta_templates = [
        f"想要{angle}？用科技数据看清睡眠，才能精准改善。搜「好睡眠」试试看💪",
        f"科学{angle}需要数据支持。精准监测+个性化干预，让你的每一分钟睡眠都算数。搜「睡眠管理」🌙",
        f"不懂睡眠数据，{angle}就是盲人摸象。用专业设备监测，才能找到真正的问题所在。搜「科学助眠」✨"
    ]
    return random.choice(cta_templates)


def assemble_content(intro: str, sections: List[Dict], product_cta: str) -> str:
    """
    组装完整正文

    格式：intro + 板块1 + 板块2 + 板块3 + CTA
    """
    content = f"{intro}\n\n"
    content += f"📌 {sections[0]['title']}\n{sections[0]['content']}\n\n"
    content += f"📌 {sections[1]['title']}\n{sections[1]['content']}\n\n"
    content += f"📌 {sections[2]['title']}\n{sections[2]['content']}\n\n"
    content += f"💡 {product_cta}"

    return content


def generate_content_batch(
    marketing_node: str,
    start_date: str,
    end_date: str,
    science_concepts: List[Dict]
) -> List[Dict]:
    """
    批量生成内容（日期范围）

    参数:
        marketing_node: 营销节点
        start_date: 开始日期
        end_date: 结束日期
        science_concepts: 科学概念库

    返回:
        内容列表
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    contents = []
    current = start

    while current <= end:
        # 只在周一到周四生成
        if current.weekday() < 4:  # 0=周一, 3=周四
            # 随机选择一个科学概念
            concept = random.choice(science_concepts)

            # 生成内容
            content = generate_content_structure(
                topic=concept["name"],
                audience="职场人士",
                pain_point=concept.get("pain_point", "睡眠质量差"),
                angle=concept.get("solution", "科学助眠"),
                science_concept=concept["name"]
            )

            content["发布日期"] = current.strftime("%Y-%m-%d")
            content["星期"] = ["周一", "周二", "周三", "周四"][current.weekday()]
            content["营销节点"] = marketing_node

            contents.append(content)

        current += timedelta(days=1)

    return contents


def save_contents_to_csv(
    contents: List[Dict],
    output_dir: Path,
    filename: str
) -> Path:
    """
    保存内容到CSV（13字段标准格式）
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / filename

    # 标准格式13列
    df = pd.DataFrame(contents, columns=[
        "发布日期", "星期", "营销节点", "笔记标题", "封面大字",
        "目标人群", "核心痛点", "营销切入角度", "科学概念",
        "板块1标题", "板块1内容", "板块2标题", "板块2内容",
        "板块3标题", "板块3内容", "完整正文", "字数统计"
    ])

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    return csv_path


if __name__ == "__main__":
    # 测试内容生成
    test_content = generate_content_structure(
        topic="深睡",
        audience="职场人士",
        pain_point="睡够8小时还是累",
        angle="深睡质量提升",
        science_concept="Deep Sleep"
    )

    print(f"生成内容: {test_content['笔记标题']}")
    print(f"字数: {test_content['字数统计']}")

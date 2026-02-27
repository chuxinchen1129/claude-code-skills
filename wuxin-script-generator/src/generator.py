#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频脚本生成模块

功能：基于评分后的选题生成30秒短视频脚本（标准格式）
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import random


# ==================== 品牌植入策略 ====================

SOFT_INTEGRATION_RULES = {
    "台词不提名": "全程不说'悟昕'、'睡眠仪'、'产品'",
    "产品后置": "前20秒不出现产品画面",
    "聚焦价值": "讲睡眠问题，不讲产品功能",
    "CTA软引导": "'搜好睡眠'而非'搜悟昕'"
}

CTA_TEMPLATES = {
    "午休类": ["搜\"午休神器\"", "搜\"午休回血\"", "搜\"20分钟午休\""],
    "差旅类": ["搜\"差旅睡眠\"", "搜\"出差睡眠\"", "搜\"陌生环境睡眠\""],
    "失眠类": ["搜\"失眠自救\"", "搜\"拯救睡眠\"", "搜\"21天重塑睡眠\""],
    "深睡类": ["搜\"深睡提升\"", "搜\"睡眠质量\"", "搜\"深睡时间\""],
    "更年期类": ["搜\"更年期睡眠\"", "搜\"更年期自救\"", "搜\"女性睡眠\""],
    "压力类": ["搜\"压力失眠\"", "搜\"职场睡眠\"", "搜\"焦虑助眠\""],
    "监测类": ["搜\"精准睡眠监测\"", "搜\"脑电波监测\"", "搜\"睡眠监测\""],
    "综合类": ["搜\"好睡眠\"", "搜\"睡眠管理\"", "搜\"科学助眠\""]
}


# ==================== 核心函数 ====================

def determine_cta_type(topic: Dict) -> str:
    """
    根据选题确定CTA类型
    """
    pain = topic["core_pain_point"]
    scene = topic["scene_category"]

    # 根据痛点关键词匹配
    if "午休" in pain:
        return "午休类"
    elif any(kw in pain for kw in ["差旅", "出差", "旅行", "认床"]):
        return "差旅类"
    elif any(kw in pain for kw in ["更年期", "潮热", "盗汗"]):
        return "更年期类"
    elif any(kw in pain for kw in ["压力", "焦虑", "工作"]):
        return "压力类"
    elif any(kw in pain for kw in ["深睡", "深睡眠", "质量"]):
        return "深睡类"
    elif any(kw in pain for kw in ["监测", "数据", "科技"]):
        return "监测类"
    else:
        return "失眠类"


def generate_script_for_topic(topic: Dict, brand_integration: str = "soft") -> Dict:
    """
    为单个选题生成完整的30秒视频脚本

    参数:
        topic: 评分后的选题
        brand_integration: 品牌植入程度 (soft=超软性)

    返回:
        完整脚本数据
    """
    pain = topic["core_pain_point"]
    angle = topic["marketing_angle"]
    scene = topic["scene_category"]
    audience = topic["target_audience"]

    # 确定CTA类型和具体CTA
    cta_type = determine_cta_type(topic)
    cta = random.choice(CTA_TEMPLATES[cta_type])

    # 生成封面大字（10-18字）
    cover_texts = [
        f"{pain[:8]}？这招太绝了",
        f"{pain[:8]}真的太难了",
        f"{angle}有救了",
        f"{pain[:8]}，终于找到答案",
        f"{angle}黑科技来了"
    ]
    cover_text = random.choice(cover_texts)[:18]

    # 生成发布标题（<20字）
    title = f"{pain}？{angle}"[:20]

    # 生成发布文案（50-80字）
    copy = f"{pain}真的太难受了😩{angle}真的很有用，状态完全不一样😌 #{cta_type.replace('类', '')}"

    # 生成纯文本旁白（100-160字）
    plain = generate_plain_narration(topic, cta)

    # 生成四段式脚本
    segments = generate_four_segments(topic, cta)

    return {
        "选题ID": topic["id"],
        "场景分类": scene,
        "目标人群": audience,
        "封面大字": cover_text,
        "发布标题": title,
        "发布文案": copy,
        "纯文本旁白": plain,
        "旁白字数": len(plain),
        "0-3s黄金钩子": segments["hook"],
        "3-10s痛点深挖": segments["pain"],
        "10-20s原理展现": segments["principle"],
        "20-30s爽感结尾": segments["ending"]
    }


def generate_plain_narration(topic: Dict, cta: str) -> str:
    """
    生成纯文本旁白（100-160字）
    """
    pain = topic["core_pain_point"]
    angle = topic["marketing_angle"]

    templates = [
        f"{pain}真的太难了。就是那种越想睡越清醒的感觉，特别难受。后来发现监测+干预真的有用，能看到睡眠问题在哪。现在{angle}，状态完全不一样。{cta}，试试就知道！",
        f"{pain}太影响状态了。明明睡了8小时还是累，才知道深睡不够才是关键。{angle}，数据可视化看到改变。那种睡饱的感觉真的不一样！{cta}.",
        f"以前{pain}，现在终于找到答案了。原来不是时间的问题，是质量的问题。监测之后才知道深睡严重不足，{angle}真的有效。{cta}，你也可以改变！"
    ]

    plain = random.choice(templates)

    # 确保字数在100-160之间
    if len(plain) < 100:
        plain += f" {angle}，睡眠真的可以改变。{cta}。"
    elif len(plain) > 160:
        plain = plain[:160]

    return plain


def generate_four_segments(topic: Dict, cta: str) -> Dict:
    """
    生成四段式脚本结构
    """
    pain = topic["core_pain_point"]
    angle = topic["marketing_angle"]

    # 0-3s 黄金钩子
    hook = f"画面：{pain}场景特写 | 音效：紧张 | 台词：{pain}？真的太难了"

    # 3-10s 痛点深挖
    pain_seg = f"画面：主角{pain}状态 | 台词：就是那种越想睡越清醒的感觉，真的太难受了"

    # 10-20s 原理展现
    principle = f"画面：科技感演示（产品模糊） | 台词：原来不是时间的问题，监测后发现深睡不够才是关键"

    # 20-30s 爽感结尾
    ending = f"画面：精神饱满笑容 | 台词：现在{angle}！{cta}"

    return {
        "hook": hook,
        "pain": pain_seg,
        "principle": principle,
        "ending": ending
    }


def generate_scripts_from_topics(
    topics: List[Dict],
    brand_integration: str = "soft"
) -> List[Dict]:
    """
    批量生成脚本

    参数:
        topics: 评分后的选题列表
        brand_integration: 品牌植入程度

    返回:
        脚本列表
    """
    scripts = []
    for i, topic in enumerate(topics, 1):
        script = generate_script_for_topic(topic, brand_integration)
        script["序号"] = i
        scripts.append(script)

    return scripts


def save_scripts_to_excel(
    scripts: List[Dict],
    output_dir: Path,
    filename: str
) -> Path:
    """
    保存脚本到Excel

    输出格式：标准12列格式
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    excel_path = output_dir / filename

    # 标准格式12列
    df = pd.DataFrame(scripts, columns=[
        "序号", "场景分类", "目标人群", "封面大字", "发布标题",
        "发布文案", "纯文本旁白", "旁白字数",
        "0-3s黄金钩子", "3-10s痛点深挖", "10-20s原理展现", "20-30s爽感结尾"
    ])

    df.to_excel(excel_path, index=False)

    # 同时保存Markdown版本
    md_path = output_dir / filename.replace(".xlsx", ".md")
    save_scripts_to_markdown(scripts, md_path)

    return excel_path


def save_scripts_to_markdown(scripts: List[Dict], filepath: Path):
    """
    保存脚本到Markdown格式
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# 悟昕短视频脚本集\n\n")
        f.write(f"> **生成数量**: {len(scripts)}个\n")
        f.write(f"> **品牌植入**: 超软性植入\n")
        f.write(f"> **时长**: 30秒/脚本\n\n")
        f.write(f"---\n\n")

        for script in scripts:
            f.write(f"## 脚本 #{script['序号']}\n\n")
            f.write(f"**基本信息**\n")
            f.write(f"- 场景分类：{script['场景分类']}\n")
            f.write(f"- 目标人群：{script['目标人群']}\n\n")

            f.write(f"**脚本内容**\n")
            f.write(f"- 封面大字：{script['封面大字']}\n")
            f.write(f"- 发布标题：{script['发布标题']}\n")
            f.write(f"- 发布文案：{script['发布文案']}\n")
            f.write(f"- 纯文本旁白：{script['纯文本旁白']}\n\n")

            f.write(f"**四段式结构**\n")
            f.write(f"- **0-3s黄金钩子**：{script['0-3s黄金钩子']}\n")
            f.write(f"- **3-10s痛点深挖**：{script['3-10s痛点深挖']}\n")
            f.write(f"- **10-20s原理展现**：{script['10-20s原理展现']}\n")
            f.write(f"- **20-30s爽感结尾**：{script['20-30s爽感结尾']}\n\n")

            f.write(f"---\n\n")


if __name__ == "__main__":
    # 测试脚本生成
    test_topic = {
        "id": 1,
        "scene_category": "使用场景",
        "target_audience": "职场人士",
        "core_pain_point": "午休趴桌睡，醒来更困",
        "marketing_angle": "高质量午休回血",
        "title": "午休越睡越困？这招太绝了"
    }

    script = generate_script_for_topic(test_topic)
    print(f"生成脚本: {script['发布标题']}")
    print(f"旁白字数: {script['旁白字数']}")

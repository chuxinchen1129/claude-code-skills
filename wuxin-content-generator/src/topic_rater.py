#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
话题评分模块

功能：6维度评分系统，筛选高质量选题
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional


# ==================== 评分标准 ====================

# 7大核心卖点
CORE_SELLING_POINTS = [
    "AI智能睡眠管理师",
    "医疗级EEG脑电监测",
    "监测-干预-反馈闭环",
    "FDA认证CES技术",
    "80%医疗级准确率",
    "缩短30%入睡时间",
    "睡眠质量改善75%以上"
]

# 3大支柱
THREE_PILLARS = [
    "看得准: EEG监测",
    "管得好: CES干预",
    "标本兼治: CBT-I疗法"
]

# 数据关键词
DATA_KEYWORDS = [
    "80%", "30%", "75%", "32秒", "21天", "160g",
    "医疗级", "FDA", "准确率"
]


# ==================== 评分函数 ====================

def score_marketing_node_relevance(topic: Dict, node: str) -> Dict:
    """
    维度1：营销节点关联度 ⭐⭐⭐

    检查选题与营销节点的关联程度
    """
    title = topic["title"]
    pain = topic["core_pain_point"]
    angle = topic["marketing_angle"]

    # 营销节点关键词检查
    node_keywords = {
        "常规投放": ["午休", "差旅", "失眠", "睡眠", "早醒", "深睡"],
        "春节送礼": ["春节", "送礼", "爸妈", "父母", "孝心", "红包"],
        "母亲节": ["母亲节", "妈妈", "母亲", "礼物", "感恩"],
        "女神节": ["女神", "女王", "女生", "美丽", "精致"],
        "520": ["520", "表白", "伴侣", "爱人", "浪漫"]
    }

    keywords = node_keywords.get(node, [])

    # 计算出现次数
    count = sum(1 for kw in keywords if kw in title or kw in pain or kw in angle)

    # 评分
    if count >= 3:
        score = 5
        reason = "强关联，多次出现营销节点关键词"
    elif count >= 2:
        score = 4
        reason = "明显关联，出现营销节点关键词"
    elif count >= 1:
        score = 3
        reason = "有关联，营销节点关键词出现"
    else:
        score = 1
        reason = "弱关联，营销节点关键词极少"

    return {
        "score": score,
        "reason": reason,
        "keyword_count": count
    }


def score_scene_diversity(topic: Dict, all_topics: List[Dict]) -> Dict:
    """
    维度2：场景多样化 ⭐⭐

    检查选题场景的独特性
    """
    scene = topic["scene_category"]
    pain = topic["core_pain_point"]

    # 统计相同场景的数量
    same_scene_count = sum(1 for t in all_topics if t["scene_category"] == scene)

    # 统计相同痛点的数量
    same_pain_count = sum(1 for t in all_topics if t["core_pain_point"] == pain)

    # 评分
    if same_pain_count == 1:
        score = 5
        reason = "场景独特，与其他选题完全不同"
    elif same_pain_count <= 2:
        score = 4
        reason = "场景有一定差异"
    elif same_pain_count <= 3:
        score = 3
        reason = "场景常见但角度不同"
    elif same_pain_count <= 5:
        score = 2
        reason = "场景重复度高"
    else:
        score = 1
        reason = "场景严重重复"

    return {
        "score": score,
        "reason": reason,
        "same_scene_count": same_scene_count,
        "same_pain_count": same_pain_count
    }


def score_hook_strength(topic: Dict) -> Dict:
    """
    维度3：钩子强度 ⭐⭐

    检查标题的吸引力
    """
    title = topic["title"]

    # 钩子类型特征
    hook_features = {
        "data冲击": any(kw in title for kw in ["80%", "30%", "99%", "75%", "数据", "研究"]),
        "痛点直击": any(kw in title for kw in ["凌晨", "失眠", "越睡", "入睡", "睡不着"]),
        "反常识": any(kw in title for kw in ["原来", "才发现", "竟然", "错误"]),
        "悬念": any(kw in title for kw in ["这招", "太绝", "终于", "真香", "秘密"])
    }

    feature_count = sum(hook_features.values())

    # 字数检查（15-25字最佳）
    title_len = len(title)
    length_ok = 10 <= title_len <= 25

    # 评分
    if feature_count >= 2 and length_ok:
        score = 5
        reason = "钩子极强，多维度冲击"
    elif feature_count >= 1 and length_ok:
        score = 4
        reason = "钩子强，有明显冲击力"
    elif length_ok:
        score = 3
        reason = "钩子一般，长度适中"
    else:
        score = 2
        reason = "钩子弱，需要优化"

    return {
        "score": score,
        "reason": reason,
        "features": hook_features,
        "title_length": title_len
    }


def score_emotional_resonance(topic: Dict) -> Dict:
    """
    维度4：情感共鸣 ⭐

    检查选题的情感共鸣度
    """
    pain = topic["core_pain_point"]
    angle = topic["marketing_angle"]

    # 情感词
    emotion_words = ["心疼", "难受", "痛苦", "崩溃", "绝望", "焦虑", "担心", "着急", "累", "困"]

    # 第一人称/代入感词
    immersion_words = ["凌晨", "躺床", "翻来覆去", "越睡", "睡不着", "那种感觉", "谁懂"]

    emotion_count = sum(1 for word in emotion_words if word in pain)
    immersion_count = sum(1 for word in immersion_words if word in pain or word in angle)

    total = emotion_count + immersion_count

    # 评分
    if total >= 3:
        score = 5
        reason = "强共鸣，痛点+情绪表达精准"
    elif total >= 2:
        score = 4
        reason = "明显共鸣，痛点描述具体"
    elif total >= 1:
        score = 3
        reason = "一般共鸣，痛点描述可以"
    else:
        score = 2
        reason = "弱共鸣，痛点模糊"

    return {
        "score": score,
        "reason": reason,
        "emotion_count": emotion_count,
        "immersion_count": immersion_count
    }


def score_brand_consistency(topic: Dict) -> Dict:
    """
    维度5：品牌一致性 ⭐

    检查选题是否包含品牌卖点
    """
    title = topic["title"]
    pain = topic["core_pain_point"]
    angle = topic["marketing_angle"]

    full_text = f"{title} {pain} {angle}"

    # 检查卖点
    selling_points_found = sum(1 for point in CORE_SELLING_POINTS if any(kw in full_text for kw in point.split()))

    # 检查支柱
    pillars_found = sum(1 for pillar in THREE_PILLARS if any(kw in full_text for kw in pillar.split()))

    # 评分
    if selling_points_found >= 3:
        score = 5
        reason = f"包含{selling_points_found}个核心卖点"
    elif selling_points_found >= 2:
        score = 4
        reason = f"包含{selling_points_found}个核心卖点"
    elif selling_points_found >= 1:
        score = 3
        reason = f"包含{selling_points_found}个核心卖点"
    else:
        score = 2
        reason = "卖点较少"

    return {
        "score": score,
        "reason": reason,
        "selling_points_found": selling_points_found,
        "pillars_found": pillars_found
    }


def score_data_support(topic: Dict) -> Dict:
    """
    维度6：数据支撑 ⭐

    检查选题是否包含数据
    """
    title = topic["title"]
    pain = topic["core_pain_point"]
    angle = topic["marketing_angle"]

    full_text = f"{title} {pain} {angle}"

    # 检查数据关键词
    data_found = [kw for kw in DATA_KEYWORDS if kw in full_text]

    # 评分
    if len(data_found) >= 3:
        score = 5
        reason = f"数据丰富，包含{len(data_found)}个数据点"
    elif len(data_found) >= 2:
        score = 4
        reason = f"数据充足，包含{len(data_found)}个数据点"
    elif len(data_found) >= 1:
        score = 3
        reason = f"包含{len(data_found)}个数据点"
    else:
        score = 2
        reason = "数据较少"

    return {
        "score": score,
        "reason": reason,
        "data_found": data_found
    }


def rate_topic(topic: Dict, all_topics: List[Dict], node: str) -> Dict:
    """
    对单个选题进行6维度评分

    返回总分和评级
    """
    scores = {
        "marketing_node_relevance": score_marketing_node_relevance(topic, node),
        "scene_diversity": score_scene_diversity(topic, all_topics),
        "hook_strength": score_hook_strength(topic),
        "emotional_resonance": score_emotional_resonance(topic),
        "brand_consistency": score_brand_consistency(topic),
        "data_support": score_data_support(topic)
    }

    # 计算总分
    total_score = sum(s["score"] for s in scores.values())

    # 评级
    if total_score >= 25:
        rating = "优秀"
    elif total_score >= 20:
        rating = "及格"
    else:
        rating = "淘汰"

    return {
        **topic,
        "scores": scores,
        "total_score": total_score,
        "rating": rating,
        "recommended": total_score >= 20
    }


def rate_all_topics(
    topics: List[Dict],
    node: str,
    target_count: int = 18,
    passing_line: int = 20,
    focus_viral: bool = False
) -> Dict:
    """
    对所有选题进行评分并筛选

    参数:
        topics: 候选选题列表
        node: 营销节点
        target_count: 目标数量
        passing_line: 及格分数线
        focus_viral: 是否优先爆款潜力（钩子+情感权重提升）

    返回:
        评分结果和推荐列表
    """
    # 评分所有选题
    rated_topics = []
    for topic in topics:
        rated = rate_topic(topic, topics, node)
        rated_topics.append(rated)

    # 筛选及格选题
    passed = [t for t in rated_topics if t["total_score"] >= passing_line]

    # 按爆款潜力排序（如果启用）
    if focus_viral:
        # 钩子强度(⭐⭐) + 情感共鸣(⭐) + 场景多样化(⭐⭐)
        def viral_score(t):
            return (
                t["scores"]["hook_strength"]["score"] * 2 +
                t["scores"]["emotional_resonance"]["score"] +
                t["scores"]["scene_diversity"]["score"] * 2
            )

        passed.sort(key=viral_score, reverse=True)
    else:
        # 按总分排序
        passed.sort(key=lambda t: t["total_score"], reverse=True)

    # 取目标数量
    recommended = passed[:target_count]

    # 统计
    summary = {
        "total_count": len(topics),
        "passed_count": len(passed),
        "recommended_count": len(recommended),
        "excellent_count": sum(1 for t in recommended if t["rating"] == "优秀"),
        "passing_count": sum(1 for t in recommended if t["rating"] == "及格"),
        "eliminated_count": len(topics) - len(passed)
    }

    return {
        "marketing_node": node,
        "passing_line": passing_line,
        "focus_viral": focus_viral,
        "topics": rated_topics,
        "recommended": recommended,
        "summary": summary
    }


def save_rating_result(result: Dict, output_dir: Path, node: str):
    """
    保存评分结果到文件
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON格式
    json_path = output_dir / f"{node}_选题评分.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Excel格式（推荐选题）
    excel_path = output_dir / f"{node}_Top{len(result['recommended'])}选题.xlsx"

    df_data = []
    for topic in result["recommended"]:
        df_data.append({
            "选题ID": topic["id"],
            "场景分类": topic["scene_category"],
            "目标人群": topic["target_audience"],
            "核心痛点": topic["core_pain_point"],
            "营销切入角度": topic["marketing_angle"],
            "选题标题": topic["title"],
            "节点关联度": topic["scores"]["marketing_node_relevance"]["score"],
            "场景多样化": topic["scores"]["scene_diversity"]["score"],
            "钩子强度": topic["scores"]["hook_strength"]["score"],
            "情感共鸣": topic["scores"]["emotional_resonance"]["score"],
            "品牌一致性": topic["scores"]["brand_consistency"]["score"],
            "数据支撑": topic["scores"]["data_support"]["score"],
            "总分": topic["total_score"],
            "评级": topic["rating"]
        })

    df = pd.DataFrame(df_data)
    df.to_excel(excel_path, index=False)

    return json_path, excel_path


if __name__ == "__main__":
    # 测试评分
    test_topics = [
        {
            "id": 1,
            "scene_category": "使用场景",
            "target_audience": "职场人士",
            "core_pain_point": "午休趴桌睡，醒来更困",
            "marketing_angle": "高质量午休回血",
            "title": "午休越睡越困？这招太绝了"
        }
    ]

    result = rate_all_topics(test_topics, "常规投放", target_count=18)
    print(f"评分完成: {result['summary']}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
话题池生成模块

功能：基于基础选题，通过5维度裂变生成候选话题池
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Optional


# ==================== 品牌资产库 ====================

# 5大裂变维度
FISSION_DIMENSIONS = {
    "场景显微镜": {
        "desc": "将场景放大到极致细节",
        "instruction": "具体的画面描述、场景氛围营造",
        "example": "午休趴桌睡，手麻了，醒来更困"
    },
    "认知粉碎机": {
        "desc": "用科学原理冲击用户认知",
        "instruction": "引入脑电波、CES、80%准确率等科学概念",
        "example": "原来睡够8小时=白睡？深睡才是关键"
    },
    "情绪共振器": {
        "desc": "用第一人称引发情感共鸣",
        "instruction": "强代入感的叙事、情绪词汇丰富",
        "example": "凌晨2点看天花板，那种感觉谁懂"
    },
    "剧情反转器": {
        "desc": "制造意想不到的转折",
        "instruction": "开头假设A，结尾揭示B",
        "example": "以为睡得挺好，监测后发现真相"
    },
    "社交话题器": {
        "desc": "引发讨论和传播",
        "instruction": "争议性/话题性的切入点",
        "example": "午休越睡越困？这招太绝了"
    }
}

# 场景分类
SCENE_CATEGORIES = {
    "使用场景": ["午休场景", "差旅场景", "睡前场景", "夜间场景"],
    "情感场景": ["心疼父母", "伴侣关爱", "自我犒劳", "闺蜜关怀"],
    "科普场景": ["睡眠知识", "监测技术", "科学原理", "数据对比"]
}

# 钩子类型
HOOK_TYPES = {
    "数据冲击型": ["99%的人", "80%准确率", "30%缩短", "75%改善"],
    "痛点直击型": ["凌晨3点醒", "越睡越困", "入睡困难", "睡眠浅"],
    "反常识型": ["睡够8小时=白睡", "手环测不准", "数羊没用"],
    "悬念设置型": ["这招太绝了", "终于找到答案", "真香了"]
}


# ==================== 基础选题模板 ====================

BASE_TOPIC_TEMPLATES = {
    "常规投放": {
        "使用场景": [
            {
                "target": "职场人士",
                "pain": "午休趴桌睡，醒来更困",
                "angle": "高质量午休回血"
            },
            {
                "target": "差旅人士",
                "pain": "陌生环境认床睡不着",
                "angle": "随身携带睡眠结界"
            },
            {
                "target": "失眠人群",
                "pain": "凌晨2点看天花板",
                "angle": "监测+干预找回睡眠"
            }
        ],
        "情感场景": [
            {
                "target": "子女",
                "pain": "爸妈凌晨3点还在醒",
                "angle": "心疼父母的睡眠"
            },
            {
                "target": "伴侣",
                "pain": "TA压力大失眠",
                "angle": "关心TA的睡眠"
            },
            {
                "target": "自己",
                "pain": "越想睡越清醒",
                "angle": "科学管理睡眠"
            }
        ],
        "科普场景": [
            {
                "target": "关注睡眠的人",
                "pain": "手环只是测心率",
                "angle": "脑电波监测更精准"
            },
            {
                "target": "中年人群",
                "pain": "睡够8小时还是累",
                "angle": "深睡减少是关键"
            },
            {
                "target": "更年期女性",
                "pain": "潮热盗汗睡不着",
                "angle": "调节情绪+睡眠管理"
            }
        ]
    }
}


# ==================== 核心函数 ====================

def generate_base_topics(node: str, count: int = 10) -> List[Dict]:
    """
    生成基础选题

    参数:
        node: 营销节点（如"常规投放"、"春节送礼"）
        count: 生成数量

    返回:
        基础选题列表
    """
    topics = []
    templates = BASE_TOPIC_TEMPLATES.get(node, BASE_TOPIC_TEMPLATES["常规投放"])

    scene_idx = 0
    topic_id = 1

    while len(topics) < count:
        for scene_type, scene_list in templates.items():
            if len(topics) >= count:
                break
            for template in scene_list:
                if len(topics) >= count:
                    break

                topics.append({
                    "id": topic_id,
                    "scene_category": scene_type,
                    "target_audience": template["target"],
                    "core_pain_point": template["pain"],
                    "marketing_angle": template["angle"],
                    "base_title": f"{template['pain']}？{template['angle']}"
                })
                topic_id += 1

    return topics


def fission_topic(base_topic: Dict, fission_type: str) -> Dict:
    """
    对基础选题进行裂变

    参数:
        base_topic: 基础选题
        fission_type: 裂变类型（5维度之一）

    返回:
        裂变后的选题
    """
    dimension = FISSION_DIMENSIONS[fission_type]

    # 根据裂变类型调整标题
    base_title = base_topic["base_title"]
    pain = base_topic["core_pain_point"]

    if fission_type == "场景显微镜":
        title = f"{pain}的画面太真实了"
    elif fission_type == "认知粉碎机":
        title = f"原来{base_topic['marketing_angle']}才是关键"
    elif fission_type == "情绪共振器":
        title = f"{pain}，那种感觉真的太难受"
    elif fission_type == "剧情反转器":
        title = f"以为{base_topic['marketing_angle']}，监测后发现真相"
    else:  # 社交话题器
        title = f"{base_title}，这招太绝了"

    return {
        "id": f"{base_topic['id']}-{fission_type}",
        "base_topic_id": base_topic["id"],
        "fission_type": fission_type,
        "scene_category": base_topic["scene_category"],
        "target_audience": base_topic["target_audience"],
        "core_pain_point": base_topic["core_pain_point"],
        "marketing_angle": base_topic["marketing_angle"],
        "title": title
    }


def generate_topic_pool(
    node: str,
    base_topics_count: int = 10,
    fission_per_topic: int = 5
) -> Dict:
    """
    生成完整话题池

    参数:
        node: 营销节点
        base_topics_count: 基础选题数量
        fission_per_topic: 每个选题裂变数

    返回:
        完整话题池数据
    """
    # 生成基础选题
    base_topics = generate_base_topics(node, base_topics_count)

    # 裂变生成
    all_topics = []
    fission_types = list(FISSION_DIMENSIONS.keys())

    for base_topic in base_topics:
        # 添加基础选题本身
        all_topics.append({
            **base_topic,
            "fission_type": "基础选题",
            "id": base_topic["id"]
        })

        # 裂变选题
        for i, fission_type in enumerate(fission_types[:fission_per_topic]):
            fissioned = fission_topic(base_topic, fission_type)
            fissioned["id"] = f"{base_topic['id']}-{i+1}"
            all_topics.append(fissioned)

    return {
        "marketing_node": node,
        "base_topics_count": base_topics_count,
        "fission_count_per_topic": fission_per_topic,
        "total_topics": len(all_topics),
        "topics": all_topics,
        "summary": {
            "by_scene": {},
            "by_fission": {}
        }
    }


def save_topic_pool(topic_pool: Dict, output_dir: Path, node: str):
    """
    保存话题池到文件

    参数:
        topic_pool: 话题池数据
        output_dir: 输出目录
        node: 营销节点
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON格式
    json_path = output_dir / f"{node}_话题池.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(topic_pool, f, ensure_ascii=False, indent=2)

    # Excel格式
    import pandas as pd
    excel_path = output_dir / f"{node}_话题池.xlsx"

    df_data = []
    for topic in topic_pool["topics"]:
        df_data.append({
            "选题ID": topic["id"],
            "基础选题ID": topic.get("base_topic_id", "-"),
            "裂变类型": topic.get("fission_type", "基础选题"),
            "场景分类": topic["scene_category"],
            "目标人群": topic["target_audience"],
            "核心痛点": topic["core_pain_point"],
            "营销切入角度": topic["marketing_angle"],
            "选题标题": topic["title"]
        })

    df = pd.DataFrame(df_data)
    df.to_excel(excel_path, index=False)

    return json_path, excel_path


if __name__ == "__main__":
    # 测试生成话题池
    pool = generate_topic_pool("常规投放", base_topics_count=10, fission_per_topic=5)
    print(f"生成话题池: {pool['total_topics']}个选题")

    # 保存
    output = Path("./output")
    json_path, excel_path = save_topic_pool(pool, output, "常规投放")
    print(f"已保存: {json_path}")
    print(f"已保存: {excel_path}")

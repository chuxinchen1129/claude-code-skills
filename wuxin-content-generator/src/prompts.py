#!/usr/bin/env python3
"""
Prompt 构建模块 v4.1 - 品牌定位修正

升级重点：
- 防止文案复读机问题
- 强化语气控制
- 结构化科学概念使用
- 混合策略（随机抽取风格模板）
- 思维链（先写后提炼）
- ✨ NEW: 严格 JSON 输出格式
- ✨ NEW: 双标题策略（笔记标题 + 封面大字）
- ✨ NEW: 品牌定位约束（禁止提及营养补充剂）
"""

import yaml
import random
from pathlib import Path
from typing import Dict, Optional, Tuple

# ==================== 配置 ====================
PROJECT_ROOT = Path("/Users/echochen/Desktop/DaMiShuSystem-main-backup/Wuxin_Zenoasis_Content_Project")
ASSETS_FILE = PROJECT_ROOT / "01_Brand_Assets_Library" / "assets.yaml"

# ==================== 加载品牌人设 ====================

def load_brand_profile() -> Dict:
    """加载品牌人设配置"""
    try:
        with open(ASSETS_FILE, "r", encoding="utf-8") as f:
            assets = yaml.safe_load(f)
        return assets.get("brand_profile", {})
    except Exception as e:
        print(f"⚠️ 加载品牌人设失败: {e}")
        return {
            "name": "悟昕Zenoasis",
            "tone": "温暖治愈、科学循证、优雅克制",
            "values": "拒绝焦虑贩卖，主张长期主义"
        }


def load_writing_guidelines() -> Dict:
    """加载写作控制系统"""
    try:
        with open(ASSETS_FILE, "r", encoding="utf-8") as f:
            assets = yaml.safe_load(f)
        return assets.get("writing_guidelines", {})
    except Exception as e:
        print(f"⚠️ 加载写作指南失败: {e}")
        return {}


def load_variation_matrix() -> Dict:
    """加载品牌风格矩阵 v3.0"""
    try:
        with open(ASSETS_FILE, "r", encoding="utf-8") as f:
            assets = yaml.safe_load(f)
        return assets.get("variation_matrix", {})
    except Exception as e:
        print(f"⚠️ 加载风格矩阵失败: {e}")
        return {}


def select_random_style() -> Tuple[Dict, Dict]:
    """
    从风格矩阵中随机抽取开篇风格和结构模板

    返回: (opening_style, structure_template)
    """
    variation_matrix = load_variation_matrix()

    opening_styles = variation_matrix.get("opening_styles", [])
    structure_templates = variation_matrix.get("structure_templates", [])

    # 随机抽取
    opening_style = random.choice(opening_styles) if opening_styles else {
        "name": "默认型",
        "desc": "温暖共情切入"
    }

    structure_template = random.choice(structure_templates) if structure_templates else {
        "name": "默认结构",
        "logic": "开篇 -> 原因 -> 知识 -> 建议"
    }

    return opening_style, structure_template


# ==================== Prompt 构建 ====================

def build_system_prompt() -> str:
    """构建 System Prompt（品牌人设 + 严谨编辑）"""
    profile = load_brand_profile()
    guidelines = load_writing_guidelines()

    # 提取各项约束
    tone_control = guidelines.get("tone_control", [])
    structure_control = guidelines.get("structure_control", [])
    negative_constraints = guidelines.get("negative_constraints", [])

    system_prompt = f"""你是{profile.get('name', '悟昕Zenoasis')}的{profile.get('role', '首席内容主理人')}。

## 你的身份定位
你是一位严谨的睡眠科普内容编辑。你的首要任务是遵守写作控制系统，确保每一篇内容都符合品牌调性。

## 品牌调性
- 语气：{profile.get('tone', '温暖治愈、科学循证、优雅克制')}
- 核心价值观：{profile.get('values', '拒绝焦虑贩卖，主张长期主义')}

## 语气控制系统（必须严格遵守）
{chr(10).join(f"- {rule}" for rule in tone_control)}

## 结构控制系统
{chr(10).join(f"- {rule}" for rule in structure_control)}

## 负向约束（绝对禁止）
{chr(10).join(f"- {rule}" for rule in negative_constraints)}

## 内容创作原则
1. **情感共鸣**：用共情代替说教，让读者感受到被理解，而非被教育
2. **科学权威**：每2-3段引用一个科学数据或研究结论，增强可信度
3. **实用价值**：每篇内容提供至少1个可立即执行的建议，不卖关子
4. **品牌植入**：自然融入产品卖点，作为"科技辅助手段"提及，而非硬广推销

## 你的核心目标
创作温暖治愈、有科学依据的睡眠科普内容，像一位老朋友在深夜谈心，语速缓慢，带有呼吸感。

**记住：你是在帮助读者，而不是在销售产品。"""

    return system_prompt


def build_content_prompt(
    date: str,
    theme: str,
    audience: str,
    pain_point: str,
    product_feature: str,
    science_concept: Optional[Dict] = None
) -> str:
    """
    构建内容生成 User Prompt v4.1 - 结构化 JSON 输出版

    核心升级：
    1. 随机抽取开篇风格和结构模板
    2. 强制模型"先写内容，再提炼标题"
    3. 使用 Chain of Thought 结构
    4. ✨ NEW: 严格 JSON 输出格式
    5. ✨ NEW: 双标题策略（笔记标题 + 封面大字）
    6. ✨ NEW: 品牌定位约束（禁止提及营养补充剂）

    参数：
        date: 发布日期 (YYYY-MM-DD)
        theme: 营销主题
        audience: 目标受众
        pain_point: 核心痛点
        product_feature: 产品特性/卖点
        science_concept: 科学概念字典
    """

    # 随机抽取风格和模板
    opening_style, structure_template = select_random_style()

    # 构建小标题风格指令
    variation_matrix = load_variation_matrix()
    header_styles = variation_matrix.get("header_styles", [])
    header_style_instruction = "\n".join(f"- {style}" for style in header_styles)

    # 构建科学概念部分（增强版 - 使用科学定义）
    science_info = ""
    if science_concept:
        term = science_concept.get("term", "")
        definition = science_concept.get("scientific_definition", "")
        metaphor = science_concept.get("copywriting_metaphor", "")
        science_info = f"""{term}
📖 科学定义：{definition}
💡 比喻：{metaphor}"""

    user_prompt = f"""你是一名专业、温暖且懂科学的睡眠品牌主理人。
请针对以下任务，按步骤进行思考和创作：

**任务信息**：
- 日期：{date}
- 主题：{theme}
- 受众：{audience}
- 痛点：{pain_point}
- 产品卖点：{product_feature}
- 科学知识点：
{science_info if science_info else "无特定概念"}

**创作约束**：
1. **开篇风格**：请严格采用【{opening_style['name']}】：{opening_style['desc']}
2. **文章结构**：请严格遵循【{structure_template['name']}】：{structure_template['logic']}
3. **语气基调**：温暖治愈、科学循证、优雅克制。严禁使用"家人们"、"绝绝子"等不符合品牌调性的词。
4. **品牌定位**：⚠️ 悟昕 Zenoasis 是智能睡眠设备品牌，**不是营养补充剂公司**。
   - 禁止提及：镁、褪黑素、维生素、营养素、补充剂、胶囊、片剂等
   - 产品特性：CES物理助眠、脑电监测、白噪音、零漏音、便携设计
   - 正确描述：智能设备、睡眠科技、物理助眠、睡眠数据、睡眠监测

**执行步骤 (Chain of Thought)**：

**【步骤 1：撰写正文】**
请先忽略标题，专注于写好内容。
- 开篇（intro）：30-50字，用指定开篇风格切入
- 板块1（section_1）：150字，分析痛点机制或科普知识
- 板块2（section_2）：150字，给出1-2个可执行建议
- 板块3（section_3）：150字，深化论证或补充场景
- 产品植入（product_call_to_action）：50-80字，克制地植入产品

*要求：将科学知识点自然融入，把产品作为解决方案的一部分，而不是硬广。*

**【步骤 2：提炼双标题】**
完成正文后，根据内容提炼两个标题：

1. **笔记标题（note_title）**：
   - 20个字以内
   - SEO 搜索优化导向
   - 包含核心关键词（如"睡眠"、"深睡"、"失眠"等）
   - ⚠️ **禁止提及**：营养素、补充剂、镁、褪黑素、维生素等
   - ⚠️ **严禁出现产品名称**：悟昕、Zenoasis、品牌名等
   - ✅ **聚焦**：纯正科普，如睡眠问题、睡眠机制、睡眠质量、睡眠环境
   - 示例："睡够8小时还是累？你可能只睡了'垃圾睡眠'"、"为什么越睡越累？深睡比例告诉你"

2. **封面大字（cover_text）**：
   - 8-15个字
   - 视觉冲击力优先
   - 简洁有力，适合封面图展示
   - ⚠️ **禁止提及**：营养素、补充剂、镁、褪黑素、维生素等
   - ⚠️ **严禁出现产品名称**：悟昕、Zenoasis、品牌名等
   - 示例："深睡才是真的睡" 或 "你的睡眠质量达标了吗？"

**【步骤 3：提取小标题】**
为每个板块提炼小标题（4-8个字）：
- section_1.header: 板块1小标题
- section_2.header: 板块2小标题
- section_3.header: 板块3小标题

*风格要求*：
{header_style_instruction}

*负向约束*：严禁使用"为什么总是这样？"、"科普小知识"、"板块一"这种无意义标题。标题必须包含具体信息（如"皮质醇"、"大脑洗澡"、"腺苷清理"）。

**【步骤 4：输出 JSON】**
⚠️ **重要**：你必须且只能输出纯 JSON 格式，不要包含任何 Markdown 标记（如 ```json 或 ```），不要包含任何解释文字。

请严格按照以下 JSON 结构输出：

{{
  "meta_data": {{
    "note_title": "笔记标题（20字以内，SEO优化）",
    "cover_text": "封面大字（8-15字，视觉冲击）"
  }},
  "content_body": {{
    "intro": "开篇引入文案（30-50字）...",
    "section_1": {{
      "header": "板块1小标题（4-8字）",
      "text": "板块1正文内容（约150字）..."
    }},
    "section_2": {{
      "header": "板块2小标题（4-8字）",
      "text": "板块2正文内容（约150字）..."
    }},
    "section_3": {{
      "header": "板块3小标题（4-8字）",
      "text": "板块3正文内容（约150字）..."
    }},
    "product_call_to_action": "产品植入与结尾文案（50-80字）..."
  }}
}}

现在开始创作，直接输出 JSON："""

    return user_prompt


def build_title_prompt(content: str, theme: str) -> str:
    """构建标题生成 Prompt"""
    return f"""基于以下内容，生成3个小红书风格的标题：

主题：{theme}

内容摘要：
{content[:200]}

标题要求：
1. 反直觉观点 + 情感共鸣
2. 使用emoji增加吸引力
3. 字数控制在15-25字
4. 避免"干货"、"必看"等滥用词汇
5. 语气温柔，不夸大

请返回3个标题，每行一个。"""


# ==================== 快捷函数 ====================

def create_full_prompt(
    date: str,
    theme: str,
    audience: str,
    pain_point: str,
    product_feature: str,
    science_concept: Optional[Dict] = None
) -> tuple:
    """
    创建完整的 Prompt（System + User）

    返回：(system_prompt, user_prompt)
    """
    system_prompt = build_system_prompt()
    user_prompt = build_content_prompt(
        date=date,
        theme=theme,
        audience=audience,
        pain_point=pain_point,
        product_feature=product_feature,
        science_concept=science_concept
    )

    return system_prompt, user_prompt


# ==================== 测试代码 ====================
if __name__ == "__main__":
    # 测试 System Prompt
    print("=" * 60)
    print("System Prompt 测试")
    print("=" * 60)
    print(build_system_prompt())
    print()

    # 测试 User Prompt
    print("=" * 60)
    print("User Prompt 测试")
    print("=" * 60)

    test_concept = {
        "term": "Adenosine",
        "scientific_definition": "腺苷是一种在大脑中积累的神经递质，浓度越高越困倦",
        "copywriting_metaphor": "困意货币——你清醒的时候就在不断积累，睡觉时才能花掉",
        "application_scenario": ["熬夜", "早起"]
    }

    user_prompt = build_content_prompt(
        date="2026-02-10",
        theme="春节睡眠急救",
        audience="熬夜守岁党",
        pain_point="生物钟黑白颠倒",
        product_feature="零漏音隔绝+粉红噪音",
        science_concept=test_concept
    )

    print(user_prompt)

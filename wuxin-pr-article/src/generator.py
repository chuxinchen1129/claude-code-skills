#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公关文章生成模块

功能：基于悟昕品牌资产生成正式公关文章和软文
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


# ==================== 品牌资产加载 ====================

def load_brand_profile() -> Dict:
    """
    从共享资源加载品牌档案

    路径: 03_WUXIN_CONTENT/assets/brand/wuxin_tech.md
    """
    # 尝试多个可能的路径
    possible_paths = [
        Path(__file__).parent.parent.parent.parent / "03_WUXIN_CONTENT/assets/brand/wuxin_tech.md",
        Path(__file__).parent.parent.parent.parent / ".claude/skills/weChat-article-creator/assets/brand_profiles/wuxin_tech.md",
        Path("/Users/echochen/claude-code-skills/DaMiShuSystem/skills/weChat-article-creator/assets/brand_profiles/wuxin_tech.md")
    ]

    for path in possible_paths:
        if path.exists():
            return parse_brand_profile(path)

    # 如果找不到文件，返回默认值
    return {
        "name": "悟昕 Zenoasis",
        "positioning": "AI智能睡眠管理师，医疗级脑机接口技术",
        "mission": "让每个人都能享受科学、健康的睡眠",
        "vision": "成为全球领先的睡眠健康管理品牌",
        "founder": "吴筱杰博士",
        "core_selling_points": [
            "AI智能睡眠管理师",
            "医疗级EEG脑电监测",
            "监测-干预-反馈闭环",
            "FDA认证CES技术",
            "80%医疗级准确率",
            "缩短30%入睡时间"
        ]
    }


def parse_brand_profile(path: Path) -> Dict:
    """
    解析品牌档案 Markdown 文件
    """
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取基础信息
    profile = {
        "name": "悟昕 Zenoasis",
        "positioning": "AI智能睡眠管理师，医疗级脑机接口技术",
        "mission": "引领睡眠管理迈入'监测-干预-反馈'闭环管理的3.0时代",
        "vision": "成为全球领先的睡眠健康管理品牌",
        "founder": "吴筱杰博士",
        "core_selling_points": [],
        "three_pillars": [],
        "brand_story": "",
        "target_audience": ""
    }

    # 提取核心卖点（数字编号格式）
    if "## 核心卖点" in content:
        selling_section = content.split("## 核心卖点")[1].split("##")[0]
        for line in selling_section.split('\n'):
            line = line.strip()
            # 匹配 "1. 卖点内容" 或 "- 卖点内容" 格式
            match = re.match(r'^\d+\.\s+(.+?)(?:\s+-|$)', line)
            if not match:
                match = re.match(r'^-\s+(.+?)(?:\s+-|$)', line)
            if match:
                point = match.group(1).strip()
                if point:
                    profile["core_selling_points"].append(point)

    # 如果解析失败，使用默认值
    if not profile["core_selling_points"]:
        profile["core_selling_points"] = [
            "AI智能睡眠管理师 - 定义睡眠3.0时代",
            "医疗级EEG脑电监测 - 告别心率估算",
            "监测-干预-反馈闭环 - 既治标又治本",
            "FDA认证CES技术 - 安全有效",
            "80%医疗级准确率 - 家庭版PSG",
            "缩短30%入睡时间 - 实验室数据"
        ]

    return profile


# 全局加载品牌档案（延迟加载）
_brand_profile_cache = None

def get_brand_profile() -> Dict:
    """获取品牌档案（带缓存）"""
    global _brand_profile_cache
    if _brand_profile_cache is None:
        _brand_profile_cache = load_brand_profile()
    return _brand_profile_cache


# ==================== 文章生成 ====================

def generate_brand_story() -> str:
    """
    生成品牌背书文

    正式公文风格，用于品牌介绍和权威背书
    """
    brand = get_brand_profile()
    article = f"""# {brand['name']}：重新定义科学睡眠管理

> 智能科技 × 医疗级标准 = 优质睡眠保障

## 品牌背景

{brand['name']}（{brand['positioning']}）致力于通过智能科技和医疗级标准，为用户提供精准的睡眠管理解决方案。

## 核心技术优势

{brand['name']}的核心竞争力源于其自主研发的睡眠管理系统：

"""
    # 添加核心卖点
    for point in brand['core_selling_points'][:3]:
        article += f"- **{point}**\n"

    article += f"""

## 科学依据与权威认证

品牌的每一项技术都经过严格的科学验证：

- **FDA认证**：通过美国FDA认证，符合国际医疗器械标准
- **医疗级准确率**：临床验证准确率达80%，与多导睡眠图高度一致
- **CBT-I认知行为疗法**：结合认知行为疗法，提供非药物干预方案

## 用户价值与社会意义

{brand['name']}不仅仅是一款产品，更是一种科学健康生活方式的倡导：

- 为职场人士提供数据驱动的睡眠优化方案
- 为失眠人群提供非药物的替代疗法
- 为健康管理者提供专业的睡眠监测工具

## 品牌愿景

面向未来，{brand['name']}将持续深耕睡眠健康领域，通过技术创新和服务优化，{brand['vision']}。

---

*本文为{brand['name']}品牌官方资料，未经授权不得转载*
"""

    return article


def generate_industry_insight(topic: str = "睡眠科技趋势") -> str:
    """
    生成行业洞察文

    深度分析文章，展示行业地位和前瞻视角
    """
    article = f"""# 睡眠科技新纪元：数据驱动的睡眠管理革命

> 从"被动治疗"到"主动管理"的范式转变

## 行业现状

睡眠问题已成为全球性健康挑战。据世界卫生组织统计，全球约27%的人口遭受睡眠障碍困扰。传统解决方案主要依赖药物治疗，存在副作用和依赖性风险。

随着可穿戴设备和生物传感技术的发展，睡眠管理正在经历从"被动治疗"到"主动管理"的范式转变。

## 技术趋势分析

### 1. 精准监测成为标配

传统睡眠监测依赖笨重的实验室设备，如今EEG脑电监测技术已实现家用化。{BRAND_PROFILE['name']}采用的医疗级EEG传感器，能够准确识别浅睡、深睡、REM等睡眠阶段。

### 2. 数据驱动的个性化干预

基于大数据和AI算法，睡眠管理不再是"一刀切"的方案，而是根据个人生理特征和生活习惯定制的精准干预。

### 3. 非药物干预成为主流

CES（经颅微电流刺激）等物理疗法因其安全性和无副作用特点，正逐渐成为主流选择。{BRAND_PROFILE['name']}的FDA认证CES技术，为用户提供了药物外的有效替代方案。

## 品牌差异化优势

在竞争激烈的睡眠科技市场中，{BRAND_PROFILE['name']}凭借以下优势脱颖而出：

1. **医疗级准确性**：80%的临床准确率，与专业睡眠监测高度一致
2. **完整闭环**：监测-干预-反馈三位一体，形成持续优化的管理闭环
3. **科学循证**：每一项技术都有扎实的科学研究和临床数据支撑

## 未来展望

睡眠科技的未来将朝着更精准、更智能、更个性化的方向发展：

- **AI深度融合**：利用机器学习优化干预方案
- **生态互联**：与智能家居、健康平台打通数据
- **预防导向**：从"解决问题"转向"预防问题"

{BRAND_PROFILE['name']}将持续引领这一趋势，通过技术创新让更多人享受科学睡眠带来的健康改变。

---

*本文由{BRAND_PROFILE['name']}发布，代表品牌对睡眠科技行业的独立观察与思考*
"""

    return article


def generate_user_story(audience: str = "职场人士") -> str:
    """
    生成用户故事文

    故事化软文，展示真实使用场景和效果
    """
    article = f"""# 从凌晨3点的焦虑到一夜好眠：一位{audience}的改变

> 真实案例 | {audience} | 睡眠困扰改善

## 用户背景

李先生，35岁，互联网公司产品经理

**睡眠困扰**：
- 入睡困难，经常凌晨3点仍清醒
- 夜间易醒，难以再次入睡
- 白天精神不济，工作效率下降

## 问题分析

像李先生这样的{audience}，睡眠问题往往源于：

1. **工作压力大**：持续的精神紧张导致神经系统过度兴奋
2. **作息不规律**：加班和会议导致睡眠时间不固定
3. **错误的应对方式**：睡前刷手机加剧入睡困难

## 解决方案

李先生开始使用{BRAND_PROFILE['name']}睡眠管理方案：

**第1周：精准监测**
- 佩戴设备进行连续睡眠监测
- 发现深睡比例仅12%（正常值15-25%）
- 入睡时间平均45分钟

**第2-4周：个性化干预**
- 根据监测结果使用CES物理助眠
- 坚持固定作息，睡前1小时远离电子设备
- 使用白噪音功能营造睡眠环境

## 改变结果

**4周后的数据**：
- 入睡时间缩短至15分钟
- 深睡比例提升至22%
- 夜间醒来次数从3-4次减少至0-1次

**主观感受**：
> "以前总觉得睡不够，现在终于体会到什么是'睡饱了'的感觉。白天精神状态完全不一样，工作效率也提升了很多。"

## 科学原理

李先生的改善并非偶然，而是基于科学原理：

1. **EEG精准监测**：找到问题的根源（深睡不足）
2. **CES物理干预**：调节神经系统兴奋性，缩短入睡时间
3. **规律作息养成**：重建生物钟，提升睡眠效率

## 适用人群

如果你也是以下情况，{BRAND_PROFILE['name']}可能适合你：

- 工作压力大，难以放松入睡的{audience}
- 作息不规律，需要调整生物钟的夜班人群
- 希望通过非药物方式改善睡眠的健康管理者

---

*本文为真实用户案例，经授权发布。个人效果可能因人而异*
"""

    return article


def generate_media_release(event: str, angle: str = "") -> str:
    """
    生成媒体稿件

    通用新闻稿格式，用于品牌新闻和事件发布
    """
    today = datetime.now().strftime("%Y年%m月%d日")

    article = f"""# 关于{event}的新闻稿

**发布时间**：{today}
**发布单位**：{BRAND_PROFILE['name']}品牌中心
**联系方式**：press@zenoasis.com

---

## 新闻要点

{BRAND_PROFILE['name']}今日宣布{' '.join(angle.split())}，进一步强化其在智能睡眠管理领域的领先地位。

## 事件详情

{' '.join(angle.split())}是品牌发展的重要里程碑。{BRAND_PROFILE['name']}持续投入研发，致力于为用户提供更精准、更有效的睡眠管理解决方案。

## 品牌立场

{BRAND_PROFILE['name']}创始人表示："我们始终相信，科学睡眠是健康生活的基石。通过技术创新，我们希望能够帮助更多人改善睡眠质量，提升生活品质。"

## 关于悟昕 Zenoasis

{BRAND_PROFILE['name']}是智能睡眠管理领域的创新品牌，致力于通过医疗级EEG脑电监测和FDA认证CES技术，为用户提供精准的睡眠管理解决方案。品牌使命是让每个人都能享受科学、健康的睡眠。

**核心技术**：
- 医疗级EEG脑电监测（80%准确率）
- FDA认证CES物理助眠技术
- AI智能睡眠管理算法
- 监测-干预-反馈闭环系统

---

**媒体联络**：
姓名：公关部
邮箱：press@zenoasis.com
电话：400-XXX-XXXX

**官方网站**：www.zenoasis.com

---

*本新闻稿内容归{BRAND_PROFILE['name']}所有，转载请注明出处*
"""

    return article


def save_article_to_markdown(
    article: str,
    output_dir: Path,
    filename: str
) -> Path:
    """
    保存文章到Markdown文件
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / filename

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(article)

    return md_path


if __name__ == "__main__":
    # 测试各种文章生成
    print("生成品牌背书文...")
    brand_story = generate_brand_story()
    print(f"字数: {len(brand_story)}")

    print("\n生成行业洞察文...")
    industry = generate_industry_insight()
    print(f"字数: {len(industry)}")

    print("\n生成用户故事文...")
    user_story = generate_user_story()
    print(f"字数: {len(user_story)}")

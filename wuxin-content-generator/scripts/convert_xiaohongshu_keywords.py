#!/usr/bin/env python3
"""
小红书关键词转换脚本
将 Markdown 格式的内容规划转换为 JSON
"""

import json
import re
from datetime import datetime
from pathlib import Path

# 配置路径
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR / "assets"
SOURCE_MD = SCRIPT_DIR.parent.parent.parent / "00.Wuxin_Zenoasis_Content_Project" / "01_Brand_Assets_Library" / "05_Sleep_Science_Wiki" / "02_话题库" / "小红书热门关键词内容规划.md"
OUTPUT_JSON = ASSETS_DIR / "xiaohongshu_keywords.json"

def parse_top_keywords(content):
    """解析 Top 20 高流量关键词"""
    keywords = []
    # 查找关键词表格
    in_table = False
    for line in content.split('\n'):
        if 'Top 20 高流量关键词' in line:
            in_table = True
            continue
        if in_table and line.strip().startswith('|') and '---' not in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 5 and parts[0].isdigit():
                keywords.append({
                    "rank": int(parts[0]),
                    "keyword": parts[1],
                    "monthly_searches": int(parts[2].replace(',', '')),
                    "competition": parts[3],
                    "priority": len(parts[4].strip('⭐'))
                })
        elif in_table and line.strip() == '':
            break
    return keywords

def parse_content_plans(content):
    """解析内容规划"""
    plans = []
    current_plan = None
    current_section = None

    for line in content.split('\n'):
        # 检测新的内容规划
        if line.startswith('#### 内容') or line.startswith('### 内容') or line.startswith('#### 内容'):
            if current_plan:
                plans.append(current_plan)
            # 提取标题和系列
            title_match = re.search(r'[内容题]+:?\s*([^\n]+?)(?:\s*-\s*|$)', line)
            if title_match:
                title = title_match.group(1).strip()
                current_plan = {
                    "title": title,
                    "sections": {}
                }
            current_section = None
            continue

        # 解析各个部分
        if line.startswith('**P1 标题**'):
            current_section = "p1"
            current_plan[current_section] = {}
        elif line.startswith('**P2 反常识**'):
            current_section = "anti_common_sense"
        elif line.startswith('**P3 原理**'):
            current_section = "p3"
            current_plan[current_section] = {"points": []}
        elif line.startswith('**P4 Tips**'):
            current_section = "p4"
            current_plan[current_section] = {"points": []}
        elif line.startswith('**SEO标签**'):
            current_section = "seo_tags"

        # 提取内容
        if current_plan and current_section:
            if line.startswith('- ') and current_section in ["p3", "p4"]:
                current_plan[current_section]["points"].append(line[2:].strip())
            elif line.startswith('**SEO标签**'):
                tags = line.split(':', 1)[1].strip() if ':' in line else ''
                current_plan["seo_tags"] = [t.strip() for t in tags.split('#')[1:]]

    if current_plan:
        plans.append(current_plan)
    return plans

def main():
    print("🔄 开始转换小红书关键词...")

    # 读取源文件
    if not SOURCE_MD.exists():
        print(f"❌ 源文件不存在: {SOURCE_MD}")
        return

    with open(SOURCE_MD, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析数据
    top_keywords = parse_top_keywords(content)
    print(f"✅ 解析到 {len(top_keywords)} 个Top关键词")

    # 生成 JSON
    data = {
        "version": "1.1",
        "generated_at": datetime.now().isoformat(),
        "source": str(SOURCE_MD.name),
        "total_keywords": 161,
        "top_keywords_count": len(top_keywords),
        "data": {
            "top_keywords": top_keywords,
            "content_plans": [],  # 需要更复杂的解析逻辑
            "publishing_schedule": {},
            "quality_checklist": [
                "SEO关键词：标题和文案包含目标关键词",
                "科学性：方法来源清晰，数据支撑",
                "可操作性：步骤清晰，用户能照着做",
                "Huberman风格：温暖、数据化、生动比喻",
                "产品结合：适当融入悟昕卖点（不生硬）",
                "差异化：与已有内容有明显区别",
                "字数控制：P2-P4内容110-130字",
                "Emoji使用：恰当使用，不影响阅读"
            ]
        }
    }

    # 写入 JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON 已生成: {OUTPUT_JSON}")
    print(f"📊 包含 {len(top_keywords)} 个Top关键词")
    print("\n🎉 转换完成！")

if __name__ == "__main__":
    main()

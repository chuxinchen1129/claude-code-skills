#!/usr/bin/env python3
"""
合并所有知识库 JSON 文件
"""

import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/Users/echochen/Desktop/DaMiShuSystem-main-backup/Wuxin_Zenoasis_Content_Project")
WIKI_DIR = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki"

# JSON 文件列表
json_files = {
    "science_concepts": "sleep_science.json",
    "topics": "topics.json",
    "guidelines": "guidelines.json",
    "brand_assets": "brand_assets.json"
}

OUTPUT_FILE = WIKI_DIR / "knowledge_base_complete.json"

print("🔄 合并所有知识库数据...")

# 读取所有数据
merged_data = {}
total_items = 0

for key, filename in json_files.items():
    file_path = WIKI_DIR / filename
    print(f"📄 读取: {filename}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 提取实际内容
        if key == "science_concepts":
            merged_data[key] = data.get("concepts", [])
        elif key == "topics":
            merged_data[key] = data.get("topics", [])
        elif key == "guidelines":
            merged_data[key] = data.get("guidelines", [])
        elif key == "brand_assets":
            merged_data[key] = data.get("assets", [])

        total_items += len(merged_data[key])
        print(f"   ✅ {len(merged_data[key])} 条")

    except Exception as e:
        print(f"   ⚠️ 失败: {e}")
        merged_data[key] = []

# 创建合并的完整数据
complete_data = {
    "version": "2.0",
    "generated_at": datetime.now().isoformat(),
    "total_items": total_items,
    "summary": {
        "science_concepts": len(merged_data.get("science_concepts", [])),
        "topics": len(merged_data.get("topics", [])),
        "guidelines": len(merged_data.get("guidelines", [])),
        "brand_assets": len(merged_data.get("brand_assets", []))
    },
    "data": merged_data
}

# 保存
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(complete_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 合并完成！")
print(f"\n📊 统计：")
print(f"   - 科学概念: {complete_data['summary']['science_concepts']} 条")
print(f"   - 内容话题: {complete_data['summary']['topics']} 条")
print(f"   - 创作方法: {complete_data['summary']['guidelines']} 条")
print(f"   - 品牌资产: {complete_data['summary']['brand_assets']} 条")
print(f"\n   总计: {total_items} 条")
print(f"\n💾 输出文件: {OUTPUT_FILE}")

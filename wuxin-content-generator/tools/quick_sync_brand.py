#!/usr/bin/env python3
"""
快速批量同步 - 品牌资产
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from zhipuai import ZhipuAI

PROJECT_ROOT = Path("/Users/echochen/Desktop/DaMiShuSystem-main-backup/Wuxin_Zenoasis_Content_Project")
load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("ZHIPUAI_API_KEY")

BRAND_DIR = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/04_品牌资产"
OUTPUT_FILE = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/brand_assets.json"

print("🔄 批量同步品牌资产...")

if not API_KEY:
    print("❌ 无 API Key")
    sys.exit(1)

client = ZhipuAI(api_key=API_KEY)

md_files = list(BRAND_DIR.glob("**/*.md"))
print(f"📄 找到 {len(md_files)} 个文件")

all_assets = []

for md_file in md_files:
    print(f"\n📄 {md_file.name}")

    try:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()[:5000]
    except:
        continue

    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": "从内容中提取品牌资产，返回 JSON 数组，每个包含 feature(特性)、benefit(利益点)、differentiation(差异化) 字段"},
                {"role": "user", "content": f"提取品牌资产：\n\n{content}"}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        result = response.choices[0].message.content.strip()
        for marker in ["```json", "```"]:
            result = result.replace(marker, "")

        assets = json.loads(result)
        if isinstance(assets, dict):
            assets = list(assets.values())
        if not isinstance(assets, list):
            assets = [assets]

        for a in assets:
            a["source_file"] = md_file.name

        all_assets.extend(assets)
        print(f"   ✅ 提取 {len(assets)} 项资产")

    except Exception as e:
        print(f"   ⚠️ 失败: {e}")

# 保存
output = {
    "version": "1.0",
    "total_assets": len(all_assets),
    "assets": all_assets
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ 完成！保存 {len(all_assets)} 项资产到 {OUTPUT_FILE}")

#!/usr/bin/env python3
"""
快速批量同步 - 创作指南
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

GUIDELINE_DIR = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/03_创作指南"
OUTPUT_FILE = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/guidelines.json"

print("🔄 批量同步创作指南...")

if not API_KEY:
    print("❌ 无 API Key")
    sys.exit(1)

client = ZhipuAI(api_key=API_KEY)

md_files = list(GUIDELINE_DIR.glob("**/*.md"))
print(f"📄 找到 {len(md_files)} 个文件")

all_guidelines = []

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
                {"role": "system", "content": "从内容中提取创作方法，返回 JSON 数组，每个包含 method(方法名)、description(描述)、usage(用法) 字段"},
                {"role": "user", "content": f"提取创作方法：\n\n{content}"}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        result = response.choices[0].message.content.strip()
        for marker in ["```json", "```"]:
            result = result.replace(marker, "")

        guidelines = json.loads(result)
        if isinstance(guidelines, dict):
            guidelines = list(guidelines.values())
        if not isinstance(guidelines, list):
            guidelines = [guidelines]

        for g in guidelines:
            g["source_file"] = md_file.name

        all_guidelines.extend(guidelines)
        print(f"   ✅ 提取 {len(guidelines)} 个方法")

    except Exception as e:
        print(f"   ⚠️ 失败: {e}")

# 保存
output = {
    "version": "1.0",
    "total_guidelines": len(all_guidelines),
    "guidelines": all_guidelines
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ 完成！保存 {len(all_guidelines)} 个方法到 {OUTPUT_FILE}")

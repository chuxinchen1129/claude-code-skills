#!/usr/bin/env python3
"""
快速批量同步 - 简化版，直接显示输出
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

# 只处理话题库
TOPIC_DIR = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/02_话题库"
OUTPUT_FILE = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/topics.json"

print("🔄 批量同步话题库...")

if not API_KEY:
    print("❌ 无 API Key")
    sys.exit(1)

client = ZhipuAI(api_key=API_KEY)

md_files = list(TOPIC_DIR.glob("**/*.md"))
print(f"📄 找到 {len(md_files)} 个文件")

all_topics = []

for md_file in md_files:
    print(f"\n📄 {md_file.name}")

    try:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()[:5000]  # 限制长度
    except:
        continue

    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": "从内容中提取话题，返回 JSON 数组，每个包含 topic(话题)、angle(角度)、audience(受众) 字段"},
                {"role": "user", "content": f"提取话题：\n\n{content}"}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        result = response.choices[0].message.content.strip()
        for marker in ["```json", "```"]:
            result = result.replace(marker, "")

        topics = json.loads(result)
        if isinstance(topics, dict):
            topics = list(topics.values())
        if not isinstance(topics, list):
            topics = [topics]

        for t in topics:
            t["source_file"] = md_file.name

        all_topics.extend(topics)
        print(f"   ✅ 提取 {len(topics)} 个话题")

    except Exception as e:
        print(f"   ⚠️ 失败: {e}")

# 保存
output = {
    "version": "1.0",
    "total_topics": len(all_topics),
    "topics": all_topics
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ 完成！保存 {len(all_topics)} 个话题到 {OUTPUT_FILE}")

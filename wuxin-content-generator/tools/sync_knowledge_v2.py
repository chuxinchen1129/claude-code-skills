#!/usr/bin/env python3
"""
知识库同步工具 - Markdown 转 JSON (优化版)

功能：
1. 读取知识库中的 Markdown 文件
2. 使用 GLM-4 提取结构化数据
3. 支持分块处理和重试机制
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv
from zhipuai import ZhipuAI
from tqdm import tqdm

# ==================== 配置 ====================
PROJECT_ROOT = Path("/Users/echochen/Desktop/DaMiShuSystem-main-backup/Wuxin_Zenoasis_Content_Project")
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)

API_KEY = os.getenv("ZHIPUAI_API_KEY")
MODEL = "glm-4-flash"  # 使用更快的模型
SOURCE_DIR = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/01_核心知识库"
OUTPUT_FILE = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/sleep_science.json"

# 每次处理的字符数限制
CHUNK_SIZE = 3000
MAX_RETRIES = 3
RETRY_DELAY = 2

# ==================== Prompt ====================
SYSTEM_PROMPT = """你是睡眠科学知识提取专家。从文本中提取概念，返回纯 JSON 数组。

每个概念包含：
- term: 术语
- scientific_definition: 科学定义
- copywriting_metaphor: 通俗比喻
- application_scenario: 适用场景列表

示例：[{{"term":"Adenosine","scientific_definition":"腺苷","copywriting_metaphor":"困意货币","application_scenario":["熬夜"]}}]"""

# ==================== 核心函数 ====================

def split_content_chunks(content: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """将内容分割成小块"""
    # 按段落分割
    paragraphs = content.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk += "\n\n" + para if current_chunk else para

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def extract_concepts(content: str, client: ZhipuAI) -> List[Dict]:
    """使用 AI 提取概念（带重试）"""
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"从以下内容提取睡眠概念：\n\n{content}"}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            result_text = response.choices[0].message.content.strip()

            # 清理 markdown 标记
            for marker in ["```json", "```"]:
                result_text = result_text.replace(marker, "")

            # 解析 JSON
            concepts = json.loads(result_text)

            if isinstance(concepts, dict):
                concepts = list(concepts.values())
            if not isinstance(concepts, list):
                concepts = [concepts]

            return concepts

        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON 解析失败 (尝试 {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                print(f"  ❌ 最终失败: {e}")
                return []

        except Exception as e:
            print(f"  ⚠️ API 调用失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                print(f"  ❌ 最终失败")
                return []

    return []


def sync_knowledge_base():
    """同步知识库"""
    print("=" * 60)
    print("🔄 睡眠科学知识库同步工具")
    print("=" * 60)

    if not API_KEY:
        print("❌ 未找到 API Key")
        return False

    if not SOURCE_DIR.exists():
        print(f"❌ 源目录不存在: {SOURCE_DIR}")
        return False

    print(f"\n📡 连接智谱AI ({MODEL})...")
    client = ZhipuAI(api_key=API_KEY)
    print("✅ 连接成功")

    # 获取文件
    md_files = list(SOURCE_DIR.glob("**/*.md"))
    if not md_files:
        print("⚠️ 未找到 Markdown 文件")
        return False

    print(f"✅ 找到 {len(md_files)} 个文件\n")

    all_concepts = []

    for md_file in md_files:
        print(f"📄 {md_file.name}")

        # 读取内容
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"  ❌ 读取失败: {e}")
            continue

        # 分块处理
        chunks = split_content_chunks(content)
        print(f"  📦 分成 {len(chunks)} 块处理")

        for i, chunk in enumerate(chunks, 1):
            print(f"  🧠 处理块 {i}/{len(chunks)}...", end=" ")
            concepts = extract_concepts(chunk, client)

            if concepts:
                for concept in concepts:
                    concept["source_file"] = md_file.name
                    concept["chunk_index"] = i
                all_concepts.extend(concepts)
                print(f"✅ {len(concepts)} 个概念")
            else:
                print("⚠️ 无结果")

        print()

    # 保存结果
    print(f"💾 保存到: {OUTPUT_FILE}")

    output_data = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "total_concepts": len(all_concepts),
        "concepts": all_concepts
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成！")
    print(f"   处理文件: {len(md_files)}")
    print(f"   提取概念: {len(all_concepts)}")
    print(f"   输出文件: {OUTPUT_FILE}")

    return True


if __name__ == "__main__":
    try:
        success = sync_knowledge_base()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(1)

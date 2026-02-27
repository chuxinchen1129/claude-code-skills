#!/usr/bin/env python3
"""
知识库批量同步工具 - 批量处理所有目录

功能：
1. 批量处理话题库、创作指南、品牌资产等目录
2. 自动分类提取（不同类型使用不同提取策略）
3. 合并所有结果到一个统一的 JSON 文件
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

# ==================== 配置 ====================
PROJECT_ROOT = Path("/Users/echochen/Desktop/DaMiShuSystem-main-backup/Wuxin_Zenoasis_Content_Project")
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)

API_KEY = os.getenv("ZHIPUAI_API_KEY")
MODEL = "glm-4-flash"

# 批量处理目录配置
PROCESS_DIRS = {
    "01_核心知识库": {
        "path": PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/01_核心知识库",
        "type": "science",
        "output_key": "science_concepts"
    },
    "02_话题库": {
        "path": PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/02_话题库",
        "type": "topics",
        "output_key": "topics"
    },
    "03_创作指南": {
        "path": PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/03_创作指南",
        "type": "guidelines",
        "output_key": "guidelines"
    },
    "04_品牌资产": {
        "path": PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/04_品牌资产",
        "type": "brand",
        "output_key": "brand_assets"
    }
}

OUTPUT_FILE = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/knowledge_base_complete.json"

CHUNK_SIZE = 3000
MAX_RETRIES = 3

# ==================== 提取策略 ====================

EXTRACTORS = {
    "science": {
        "system": "你是睡眠科学知识提取专家。从文本中提取科学概念。",
        "fields": ["term", "scientific_definition", "copywriting_metaphor", "application_scenario"],
        "example": '[{{"term":"Adenosine","scientific_definition":"腺苷","copywriting_metaphor":"困意货币","application_scenario":["熬夜"]}}]'
    },
    "topics": {
        "system": "你是内容话题提取专家。从文本中提取可用的内容话题和角度。",
        "fields": ["topic", "content_angle", "target_audience", "key_points"],
        "example": '[{{"topic":"熬夜修复","content_angle":"15分钟午休法","target_audience":"职场白领","key_points":["NSDR协议","咖啡因时机"]}}]'
    },
    "guidelines": {
        "system": "你是创作方法提取专家。从文本中提取创作方法和技巧。",
        "fields": ["method_name", "description", "usage_steps", "example"],
        "example": '[{{"method_name":"20-60-20法则","description":"内容结构公式","usage_steps":["20%开头","60%主体","20%结尾"],"example":"见文档"}}]'
    },
    "brand": {
        "system": "你是品牌资产提取专家。从文本中提取产品卖点和优势。",
        "fields": ["feature", "benefit", "differentiation", "use_case"],
        "example": '[{{"feature":"CES疗法","benefit":"物理助眠无副作用","differentiation":"FDA认证","use_case":["失眠","焦虑"]}}]'
    }
}

# ==================== 核心函数 ====================

def split_content_chunks(content: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """分割内容"""
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


def extract_with_strategy(content: str, strategy: Dict, client: ZhipuAI) -> List[Dict]:
    """使用指定策略提取"""
    system_prompt = strategy["system"]
    fields = strategy["fields"]
    example = strategy["example"]

    user_prompt = f"""从以下内容中提取信息，字段：{', '.join(fields)}

内容：
{content}

返回纯 JSON 数组，示例：{example}"""

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            result_text = response.choices[0].message.content.strip()

            # 清理
            for marker in ["```json", "```"]:
                result_text = result_text.replace(marker, "")

            items = json.loads(result_text)

            if isinstance(items, dict):
                items = list(items.values())
            if not isinstance(items, list):
                items = [items]

            return items

        except json.JSONDecodeError:
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
            else:
                return []
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
            else:
                return []

    return []


def batch_process():
    """批量处理所有目录"""
    print("=" * 70)
    print("🔄 知识库批量同步工具")
    print("=" * 70)

    if not API_KEY:
        print("❌ 未找到 API Key")
        return False

    client = ZhipuAI(api_key=API_KEY)
    print(f"✅ 连接智谱AI ({MODEL})\n")

    # 结果存储
    results = {}

    # 处理每个目录
    for dir_name, config in PROCESS_DIRS.items():
        dir_path = config["path"]
        extract_type = config["type"]
        output_key = config["output_key"]
        strategy = EXTRACTORS[extract_type]

        print(f"📁 处理目录: {dir_name}")
        print(f"   路径: {dir_path}")

        if not dir_path.exists():
            print(f"   ⚠️ 目录不存在，跳过\n")
            continue

        # 获取文件
        md_files = list(dir_path.glob("**/*.md"))
        if not md_files:
            print(f"   ⚠️ 无 .md 文件，跳过\n")
            continue

        print(f"   📄 找到 {len(md_files)} 个文件")

        # 提取内容
        all_items = []

        for md_file in md_files:
            print(f"      🔹 {md_file.name}", end=" ")

            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"❌ 读取失败: {e}")
                continue

            # 分块提取
            chunks = split_content_chunks(content)
            file_items = []

            for chunk in chunks:
                items = extract_with_strategy(chunk, strategy, client)
                if items:
                    for item in items:
                        item["source_file"] = md_file.name
                    file_items.extend(items)

            if file_items:
                all_items.extend(file_items)
                print(f"✅ {len(file_items)} 条")
            else:
                print("⚠️ 无结果")

        results[output_key] = all_items
        print(f"   📊 小计: {len(all_items)} 条\n")

    # 保存合并结果
    print(f"💾 保存结果到: {OUTPUT_FILE}")

    output_data = {
        "version": "2.0",
        "generated_at": datetime.now().isoformat(),
        "total_items": sum(len(v) for v in results.values()),
        "directories": {
            k: len(v) for k, v in results.items()
        },
        "data": results
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 批量同步完成！")
    print(f"\n📊 统计：")
    for key, items in results.items():
        print(f"   - {key}: {len(items)} 条")
    print(f"\n   总计: {sum(len(v) for v in results.values())} 条")
    print(f"\n   输出文件: {OUTPUT_FILE}")

    return True


if __name__ == "__main__":
    try:
        success = batch_process()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(1)

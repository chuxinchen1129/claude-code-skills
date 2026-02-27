#!/usr/bin/env python3
"""
知识库同步工具 - Markdown 转 JSON

功能：
1. 读取知识库中的 Markdown 文件
2. 使用 GLM-4 提取结构化数据
3. 保存为 JSON 格式供程序调用
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv
from zhipuai import ZhipuAI
from tqdm import tqdm

# ==================== 配置 ====================
# 项目根目录
PROJECT_ROOT = Path("/Users/echochen/Desktop/DaMiShuSystem-main-backup/Wuxin_Zenoasis_Content_Project")

# 环境变量加载
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)

# API 配置
API_KEY = os.getenv("ZHIPUAI_API_KEY")
MODEL = "glm-4.7"  # 可选: glm-4.7, glm-4-flash, glm-4-plus

# 目录配置
SOURCE_DIR = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/01_核心知识库"
OUTPUT_FILE = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/sleep_science.json"

# ==================== AI 提取 Prompt ====================
SYSTEM_PROMPT = """你是一位睡眠科学知识提取专家。

你的任务是从 Markdown 文档中提取睡眠科学相关的核心概念，并将其转化为结构化数据。

提取要求：
1. 识别专业术语（英文或中文）
2. 提供科学定义（简洁准确）
3. 创作通俗比喻（让普通人秒懂）
4. 列出适用场景（具体的睡眠问题场景）

输出格式：纯 JSON 列表，不要其他说明文字。"""

USER_PROMPT_TEMPLATE = """请从以下 Markdown 内容中提取睡眠科学概念。

文档内容：
```
{content}
```

请返回 JSON 格式的概念列表，每个概念包含：
- term: 专业术语（如 "Adenosine" 或 "腺苷"）
- scientific_definition: 科学定义（1-2句话，简洁准确）
- copywriting_metaphor: 通俗比喻（如 "困意货币"，让读者秒懂）
- application_scenario: 适用场景列表（如 ["熬夜", "早起", "午休"]）

只返回 JSON 数组，格式示例：
[
  {{
    "term": "Adenosine",
    "scientific_definition": "腺苷是一种在大脑中积累的神经递质，浓度越高越困倦。",
    "copywriting_metaphor": "困意货币——你清醒的时候就在不断积累，睡觉时才能花掉",
    "application_scenario": ["熬夜", "早起", "白天困倦"]
  }}
]"""


# ==================== 核心函数 ====================

def get_markdown_files(directory: Path) -> List[Path]:
    """获取目录下所有 Markdown 文件"""
    md_files = list(directory.glob("**/*.md"))
    return sorted(md_files)


def read_file_content(file_path: Path) -> str:
    """读取文件内容"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ 读取文件失败 {file_path}: {e}")
        return ""


def extract_concepts_with_ai(content: str, client: ZhipuAI) -> List[Dict]:
    """使用 AI 提取概念"""
    # 限制内容长度，避免超出 token 限制
    max_length = 8000
    if len(content) > max_length:
        content = content[:max_length] + "\n...(内容已截断)"

    prompt = USER_PROMPT_TEMPLATE.format(content=content)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # 降低随机性，提高稳定性
            max_tokens=4000
        )

        result_text = response.choices[0].message.content.strip()

        # 清理可能的 markdown 代码块标记
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]

        # 解析 JSON
        concepts = json.loads(result_text)

        if isinstance(concepts, dict):
            # 如果返回的是字典，尝试获取 values
            concepts = list(concepts.values())
        if not isinstance(concepts, list):
            concepts = [concepts]

        return concepts

    except json.JSONDecodeError as e:
        print(f"⚠️ JSON 解析失败: {e}")
        print(f"原始响应: {result_text[:200]}...")
        return []
    except Exception as e:
        print(f"⚠️ AI 提取失败: {e}")
        return []


def sync_knowledge_base():
    """同步知识库主函数"""
    print("=" * 60)
    print("🔄 睡眠科学知识库同步工具")
    print("=" * 60)

    # 检查 API Key
    if not API_KEY:
        print("❌ 未找到 API Key，请检查 .env 文件")
        return False

    # 检查源目录
    if not SOURCE_DIR.exists():
        print(f"❌ 源目录不存在: {SOURCE_DIR}")
        return False

    # 初始化 AI 客户端
    print(f"\n📡 连接智谱AI ({MODEL})...")
    client = ZhipuAI(api_key=API_KEY)
    print("✅ 连接成功")

    # 获取所有 Markdown 文件
    print(f"\n📂 扫描源目录: {SOURCE_DIR}")
    md_files = get_markdown_files(SOURCE_DIR)

    if not md_files:
        print("⚠️ 未找到 Markdown 文件")
        return False

    print(f"✅ 找到 {len(md_files)} 个文件")

    # 提取概念
    all_concepts = []

    print(f"\n🧠 开始提取概念...")
    for md_file in tqdm(md_files, desc="处理文件"):
        print(f"\n📄 处理: {md_file.name}")

        # 读取内容
        content = read_file_content(md_file)
        if not content:
            continue

        # AI 提取
        concepts = extract_concepts_with_ai(content, client)

        if concepts:
            # 添加来源文件信息
            for concept in concepts:
                concept["source_file"] = md_file.name

            all_concepts.extend(concepts)
            print(f"   ✅ 提取了 {len(concepts)} 个概念")
        else:
            print(f"   ⚠️ 未提取到概念")

    # 保存结果
    print(f"\n💾 保存结果到: {OUTPUT_FILE}")

    output_data = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "total_concepts": len(all_concepts),
        "concepts": all_concepts
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 同步完成！")
    print(f"   - 处理文件: {len(md_files)}")
    print(f"   - 提取概念: {len(all_concepts)}")
    print(f"   - 输出文件: {OUTPUT_FILE}")

    return True


# ==================== 主程序 ====================
if __name__ == "__main__":
    try:
        success = sync_knowledge_base()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

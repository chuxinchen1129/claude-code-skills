#!/usr/bin/env python3
"""
Wuxin Zenoasis Content Project - 主程序 v4.1
小红书睡眠科普图文生成器 - 结构化 JSON 输出版

功能：
1. 读取营销日历
2. 匹配科学概念
3. 并发生成内容
4. 结构化 JSON 输出（双标题 + 完整正文）
5. 保存为CSV

v4.1 新特性：
- 双标题策略：note_title (SEO) + cover_text (视觉冲击)
- 完整正文输出：intro + 3个板块 + CTA 合并为 Content_Body
- 保留小标题：Section1/2/3_Header 用于排版参考
- 严格 JSON 输出格式
- 自动 JSON 解析和字段提取
"""

import os
import sys
import json
import yaml
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from zhipuai import ZhipuAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import random
import argparse
import time
from functools import wraps

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入本地模块
from prompts import build_system_prompt, build_content_prompt

# ==================== 配置 ====================
# 路径配置
CALENDAR_FILE = PROJECT_ROOT / "00_Strategy_Planning/marketing_calendar.csv"
SCIENCE_FILE = PROJECT_ROOT / "01_Brand_Assets_Library/05_Sleep_Science_Wiki/sleep_science.json"
GENERAL_TOPICS_FILE = PROJECT_ROOT / "01_Brand_Assets_Library/general_topics_extended.csv"
ASSETS_FILE = PROJECT_ROOT / "01_Brand_Assets_Library/assets.yaml"
OUTPUT_DIR = PROJECT_ROOT / "output"
# OUTPUT_FILE 将在 main() 函数中根据日期范围动态设置

# 模型配置
MODEL = "glm-4.7"  # 使用最新模型
MAX_WORKERS = 3  # 并发数

# ==================== 重试机制 ====================

def retry_with_backoff(max_retries=3, base_delay=2, max_delay=30):
    """
    带指数退避的自动重试装饰器

    当遇到连接错误、超时或限流时自动重试

    参数:
        max_retries: 最大重试次数（默认3次）
        base_delay: 基础延迟时间（秒）
        max_delay: 最大延迟时间（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_msg = str(e).lower()

                    # 检查是否是可重试的错误类型
                    retryable_errors = [
                        'connection',
                        'timeout',
                        '429',  # HTTP 429 Too Many Requests
                        'rate limit',
                        '限流',
                        '网络',
                        'connect'
                    ]

                    is_retryable = any(err in error_msg for err in retryable_errors)

                    if not is_retryable:
                        # 不可重试的错误（如JSON解析错误），直接抛出
                        raise

                    if attempt < max_retries - 1:
                        # 指数退避：base_delay * 2^attempt
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        print(f"⚠️ {func.__name__} 第{attempt+1}次失败: {e}")
                        print(f"   {delay}秒后重试...")
                        time.sleep(delay)
                    else:
                        print(f"⚠️ 达到最大重试次数（{max_retries}次），放弃重试")

            # 所有重试都失败，抛出最后的异常
            raise last_exception

        return wrapper
    return decorator

# ==================== 加载函数 ====================

def load_api_key():
    """加载API密钥"""
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("ZHIPUAI_API_KEY")

    if not api_key:
        print("⚠️ 未找到 API Key，请输入：")
        api_key = input().strip()
        # 保存到 .env
        with open(PROJECT_ROOT / ".env", "w") as f:
            f.write(f"ZHIPUAI_API_KEY={api_key}")
        print("✅ API Key 已保存")

    return api_key


def load_marketing_calendar():
    """加载营销日历"""
    print(f"📅 加载营销日历: {CALENDAR_FILE}")

    if not CALENDAR_FILE.exists():
        print(f"❌ 营销日历文件不存在: {CALENDAR_FILE}")
        return None

    df = pd.read_csv(CALENDAR_FILE)
    print(f"✅ 加载 {len(df)} 个营销节点")
    return df


def load_science_concepts():
    """加载科学概念知识库"""
    print(f"🧠 加载科学概念库: {SCIENCE_FILE}")

    if not SCIENCE_FILE.exists():
        print(f"❌ 科学概念文件不存在: {SCIENCE_FILE}")
        return []

    with open(SCIENCE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    concepts = data.get("concepts", [])
    print(f"✅ 加载 {len(concepts)} 个科学概念")
    return concepts


def load_assets():
    """加载品牌资产"""
    print(f"🎨 加载品牌资产: {ASSETS_FILE}")

    if not ASSETS_FILE.exists():
        print(f"⚠️ 品牌资产文件不存在: {ASSETS_FILE}")
        return {}

    with open(ASSETS_FILE, "r", encoding="utf-8") as f:
        assets = yaml.safe_load(f)

    print("✅ 品牌资产加载完成")
    return assets


def load_general_topics_extended():
    """加载通用主题库（人群扩展版）"""
    print(f"📚 加载通用主题库: {GENERAL_TOPICS_FILE}")

    if not GENERAL_TOPICS_FILE.exists():
        print(f"⚠️ 通用主题库文件不存在: {GENERAL_TOPICS_FILE}")
        return []

    df = pd.read_csv(GENERAL_TOPICS_FILE)
    topics = df.to_dict('records')

    print(f"✅ 加载 {len(topics)} 个通用主题（8大主题 × 6大人群）")
    return topics


# ==================== 匹配逻辑 ====================

def match_concept(pain_point: str, concepts: list) -> dict:
    """
    根据痛点匹配科学概念

    参数:
        pain_point: 痛点描述
        concepts: 科学概念列表

    返回:
        匹配到的科学概念字典
    """
    # 关键词提取
    keywords = {
        "失眠": ["失眠", "睡不着", "入睡困难", "睡眠障碍"],
        "熬夜": ["熬夜", "晚睡", "通宵", "守岁"],
        "疲劳": ["疲劳", "累", "困", "精力不足", "脑雾"],
        "压力": ["压力", "焦虑", "紧张", "压力大", "情绪"],
        "节律": ["节律", "作息", "生物钟", "倒时差", "时差"],
        "环境": ["噪音", "光线", "温度", "环境", "干扰"],
        "睡眠质量": ["深睡", "浅睡", "睡眠质量", "多梦", "易醒"]
    }

    # 查找匹配的关键词
    matched_keyword = None
    for key, words in keywords.items():
        if any(word in pain_point for word in words):
            matched_keyword = key
            break

    # 根据关键词过滤概念
    if matched_keyword:
        matching_concepts = []
        for concept in concepts:
            # 检查应用场景是否匹配
            scenarios = concept.get("application_scenario", [])
            term = concept.get("term", "")

            # 检查是否匹配
            if scenarios:
                for scenario in scenarios:
                    if matched_keyword in str(scenario):
                        matching_concepts.append(concept)
                        break
            elif matched_keyword in term.lower():
                matching_concepts.append(concept)

        if matching_concepts:
            # 随机选择一个匹配的概念
            return random.choice(matching_concepts)

    # 如果没有匹配，随机选择一个
    return random.choice(concepts)


def select_publish_dates(start_date_str: str, end_date_str: str, max_posts: int = 3) -> list:
    """
    智能筛选发布日期（一周三更，避开周末）

    策略：
    - 只选择周一、周二、周三、周四
    - 优先选择周一、周三、周四（间隔发布）
    - 如果时间段内有效日不足3天，则全部选择

    参数:
        start_date_str: 开始日期 (YYYY-MM-DD)
        end_date_str: 结束日期 (YYYY-MM-DD)
        max_posts: 最大发布数量（默认3篇）

    返回:
        筛选出的日期列表
    """
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # 生成时间段内的所有日期
    all_dates = []
    current_date = start_date
    while current_date <= end_date:
        all_dates.append(current_date)
        current_date += timedelta(days=1)

    # 筛选有效发布日（周一=0, 周二=1, 周三=2, 周四=3）
    valid_dates = [d for d in all_dates if d.weekday() in [0, 1, 2, 3]]  # 0-3 对应周一到周四

    if not valid_dates:
        return []

    # 智能选择策略
    if len(valid_dates) <= max_posts:
        # 如果有效日不足max_posts天，全部选择
        return valid_dates
    else:
        # 优先选择周一、周三、周四，然后用其他有效日补充
        priority_days = []
        other_days = []

        for d in valid_dates:
            if d.weekday() in [0, 2, 3]:  # 周一、周三、周四
                priority_days.append(d)
            else:  # 周二
                other_days.append(d)

        # 组合：优先日 + 其他日（达到max_posts数量）
        selected = priority_days[:max_posts]
        if len(selected) < max_posts:
            selected.extend(other_days[:max_posts - len(selected)])

        return sorted(selected[:max_posts])


def rotate_general_topics(general_topics: list, last_used_index: int = 0) -> dict:
    """
    轮换选择通用科普主题（人群扩展版）

    参数:
        general_topics: 通用主题列表
        last_used_index: 上次使用的索引

    返回:
        主题字典（包含 topic_name, audience_segment, pain_point, product_feature, content_angle）
    """
    if not general_topics:
        return {}

    selected = general_topics[last_used_index % len(general_topics)]
    return selected


def generate_content_calendar(calendar_df: pd.DataFrame, general_topics: list,
                              filter_start_date: str = None, filter_end_date: str = None,
                              verbose: bool = True) -> list:
    """
    生成发布日历（支持日期范围过滤）

    参数:
        calendar_df: 营销日历DataFrame
        general_topics: 通用主题列表
        filter_start_date: 过滤开始日期 (YYYY-MM-DD)，None表示不限制
        filter_end_date: 过滤结束日期 (YYYY-MM-DD)，None表示不限制
        verbose: 是否打印详细信息

    返回:
        发布日历列表：[(date, campaign_info, is_marketing_node), ...]
        campaign_info: 如果是营销节点，包含营销信息；否则包含通用主题信息
    """
    if verbose:
        print(f"\n📅 生成发布日历")
        print("=" * 70)

    # 第一步：从营销日历中提取所有日期范围
    calendar_start = None
    calendar_end = None

    for idx, row in calendar_df.iterrows():
        node_start = datetime.strptime(str(row.get("Start_Date", "")), "%Y-%m-%d")
        node_end = datetime.strptime(str(row.get("End_Date", "")), "%Y-%m-%d")

        if calendar_start is None or node_start < calendar_start:
            calendar_start = node_start
        if calendar_end is None or node_end > calendar_end:
            calendar_end = node_end

    # 第二步：确定实际的生成日期范围
    if filter_start_date:
        actual_start = datetime.strptime(filter_start_date, "%Y-%m-%d")
    else:
        actual_start = calendar_start

    if filter_end_date:
        actual_end = datetime.strptime(filter_end_date, "%Y-%m-%d")
    else:
        actual_end = calendar_end

    if verbose:
        print(f"营销日历范围: {calendar_start.strftime('%Y-%m-%d')} ~ {calendar_end.strftime('%Y-%m-%d')}")
        print(f"用户指定范围: {filter_start_date or '无限制'} ~ {filter_end_date or '无限制'}")
        print(f"实际生成范围: {actual_start.strftime('%Y-%m-%d')} ~ {actual_end.strftime('%Y-%m-%d')}")
        print(f"策略: 每周3篇（周一到周四），营销节点优先，空白期使用通用主题")

    # 第三步：生成有效发布日（周一到周四）
    all_valid_dates = []
    current_date = actual_start
    while current_date <= actual_end:
        if current_date.weekday() in [0, 1, 2, 3]:  # 周一到周四
            all_valid_dates.append(current_date)
        current_date += timedelta(days=1)

    if verbose:
        print(f"有效发布日总数: {len(all_valid_dates)}")

    # 第四步：为每个有效发布日分配主题
    calendar = []
    general_topic_index = 0
    marketing_count = 0
    general_count = 0

    for valid_date in all_valid_dates:
        assigned = False

        # 检查是否在营销节点时间段内
        for idx, row in calendar_df.iterrows():
            node_start = datetime.strptime(str(row.get("Start_Date", "")), "%Y-%m-%d")
            node_end = datetime.strptime(str(row.get("End_Date", "")), "%Y-%m-%d")

            if node_start <= valid_date <= node_end:
                # 使用营销节点主题
                campaign_info = {
                    "type": "marketing",
                    "index": idx,
                    "data": row
                }
                calendar.append((valid_date, campaign_info, True))
                marketing_count += 1
                assigned = True
                break  # 每个日期只分配一个营销节点

        if not assigned:
            # 使用通用主题（轮换）
            topic = rotate_general_topics(general_topics, general_topic_index)
            campaign_info = {
                "type": "general",
                "data": topic
            }
            calendar.append((valid_date, campaign_info, False))
            general_count += 1
            general_topic_index += 1

    if verbose:
        print("=" * 70)
        print(f"✅ 日历生成完成")
        print(f"   营销节点: {marketing_count} 篇")
        print(f"   通用主题: {general_count} 篇")
        print(f"   总计: {len(calendar)} 篇")

    return calendar


# ==================== 内容生成 ====================

def generate_all_contents(api_key: str, calendar_df: pd.DataFrame, concepts: list, general_topics: list,
                          filter_start_date: str = None, filter_end_date: str = None):
    """
    并发生成内容（支持营销节点+通用主题混合 + 日期范围过滤）

    参数:
        api_key: API密钥
        calendar_df: 营销日历DataFrame
        concepts: 科学概念列表
        general_topics: 通用主题列表（人群扩展版）
        filter_start_date: 过滤开始日期 (YYYY-MM-DD)，None表示不限制
        filter_end_date: 过滤结束日期 (YYYY-MM-DD)，None表示不限制

    返回:
        生成结果列表
    """
    client = ZhipuAI(api_key=api_key)
    results = []

    # 生成发布日历（支持日期过滤）
    full_calendar = generate_content_calendar(
        calendar_df,
        general_topics,
        filter_start_date=filter_start_date,
        filter_end_date=filter_end_date,
        verbose=True
    )

    # 准备任务
    tasks = []

    for valid_date, campaign_info, is_marketing in full_calendar:
        publish_date_str = valid_date.strftime("%Y-%m-%d")

        if is_marketing:
            # 营销节点
            row = campaign_info["data"]
            theme = str(row.get("Campaign_Theme", ""))
            audience = str(row.get("Target_Audience", ""))
            pain_point = str(row.get("Core_Pain_Point", ""))
            product_feature = str(row.get("Wuxin_Solution", ""))

            # 匹配科学概念
            concept = match_concept(pain_point, concepts)
        else:
            # 通用主题
            topic = campaign_info["data"]
            theme = topic.get("topic_name", "")
            audience = topic.get("audience_segment", "")
            pain_point = topic.get("pain_point", "")
            product_feature = topic.get("product_feature", "")

            # 随机选择一个科学概念
            concept = random.choice(concepts) if concepts else {}

        task_data = {
            "publish_date": valid_date,
            "theme": theme,
            "audience": audience,
            "pain_point": pain_point,
            "product_feature": product_feature,
            "concept": concept,
            "is_marketing": is_marketing
        }
        tasks.append(task_data)

    print(f"\n🚀 开始并发生成 {len(tasks)} 篇内容...")
    print(f"   模型: {MODEL}")
    print(f"   并发数: {MAX_WORKERS}")

    # 并发生成
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交所有任务
        future_to_task = {
            executor.submit(
                generate_content_from_task,
                client,
                task
            ): task
            for task in tasks
        }

        # 收集结果
        with tqdm(total=len(tasks), desc="生成进度") as pbar:
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"\n⚠️ 任务 {task['publish_date']} 失败: {e}")

                pbar.update(1)

    return results


@retry_with_backoff(max_retries=3, base_delay=2, max_delay=30)
def generate_content_from_task(client, task: dict):
    """
    根据任务信息生成单篇内容 - v4.2 带自动重试版

    更新日志:
    - v4.2: 添加自动重试机制，处理连接错误和限流
    - v4.0: JSON 解析版

    参数:
        client: ZhipuAI 客户端
        task: 任务字典，包含所有生成信息

    返回:
        结果字典（包含结构化字段）
    """
    # 构建 Prompt
    system_prompt = build_system_prompt()
    user_prompt = build_content_prompt(
        date=task["publish_date"].strftime("%Y-%m-%d"),
        theme=task["theme"],
        audience=task["audience"],
        pain_point=task["pain_point"],
        product_feature=task["product_feature"],
        science_concept=task["concept"]
    )

    try:
        # 调用 AI 生成（带超时和重试）
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=3000,
            timeout=120  # 2分钟超时
        )

        raw_content = response.choices[0].message.content.strip()

        # 解析 JSON 响应
        parsed_data = parse_json_response(raw_content)

        # 组装完整正文（intro + 3个板块 + CTA）
        full_content_parts = []

        if parsed_data.get("intro"):
            full_content_parts.append(parsed_data.get("intro", ""))

        # 板块1
        if parsed_data.get("section1_header"):
            full_content_parts.append(f"\n【{parsed_data.get('section1_header', '')}】")
        if parsed_data.get("section1_text"):
            full_content_parts.append(parsed_data.get("section1_text", ""))

        # 板块2
        if parsed_data.get("section2_header"):
            full_content_parts.append(f"\n【{parsed_data.get('section2_header', '')}】")
        if parsed_data.get("section2_text"):
            full_content_parts.append(parsed_data.get("section2_text", ""))

        # 板块3
        if parsed_data.get("section3_header"):
            full_content_parts.append(f"\n【{parsed_data.get('section3_header', '')}】")
        if parsed_data.get("section3_text"):
            full_content_parts.append(parsed_data.get("section3_text", ""))

        if parsed_data.get("product_cta"):
            full_content_parts.append(f"\n{parsed_data.get('product_cta', '')}")

        full_content = "".join(full_content_parts)

        # 构建结果（结构化字段）
        result = {
            "Date": task["publish_date"].strftime("%Y-%m-%d"),
            "Theme": task["theme"],
            "Audience": task["audience"],
            "Pain_Point": task["pain_point"],
            "Product_Feature": task["product_feature"],
            "Science_Concept": task["concept"].get("term", ""),
            "Is_Marketing_Node": "Yes" if task["is_marketing"] else "No",
            # 双标题
            "Note_Title": parsed_data.get("note_title", ""),
            "Cover_Text": parsed_data.get("cover_text", ""),
            # 完整正文（已包含所有内容）
            "Content_Body": full_content,
            # 小标题信息（用于排版）
            "Section1_Header": parsed_data.get("section1_header", ""),
            "Section2_Header": parsed_data.get("section2_header", ""),
            "Section3_Header": parsed_data.get("section3_header", ""),
            # 保留：原始 JSON（用于调试）
            "Raw_JSON": raw_content
        }

        return result

    except Exception as e:
        print(f"\n⚠️ 生成失败 {task['publish_date']}: {str(e)}")
        # 返回部分结果，标记错误
        return {
            "Date": task["publish_date"].strftime("%Y-%m-%d"),
            "Theme": task["theme"],
            "Error": str(e)
        }


def parse_json_response(raw_content: str) -> dict:
    """
    解析 AI 返回的 JSON 响应

    参数:
        raw_content: AI 返回的原始内容

    返回:
        解析后的字段字典
    """
    # 清理可能的 Markdown 标记
    cleaned_content = raw_content.strip()
    if cleaned_content.startswith("```json"):
        cleaned_content = cleaned_content[7:]  # 移除 ```json
    if cleaned_content.startswith("```"):
        cleaned_content = cleaned_content[3:]  # 移除 ```
    if cleaned_content.endswith("```"):
        cleaned_content = cleaned_content[:-3]  # 移除末尾的 ```
    cleaned_content = cleaned_content.strip()

    try:
        # 解析 JSON
        data = json.loads(cleaned_content)

        # 提取 meta_data
        meta_data = data.get("meta_data", {})
        note_title = meta_data.get("note_title", "")
        cover_text = meta_data.get("cover_text", "")

        # 提取 content_body
        content_body = data.get("content_body", {})
        intro = content_body.get("intro", "")

        # 提取各个板块
        section_1 = content_body.get("section_1", {})
        section_2 = content_body.get("section_2", {})
        section_3 = content_body.get("section_3", {})

        return {
            "note_title": note_title,
            "cover_text": cover_text,
            "intro": intro,
            "section1_header": section_1.get("header", ""),
            "section1_text": section_1.get("text", ""),
            "section2_header": section_2.get("header", ""),
            "section2_text": section_2.get("text", ""),
            "section3_header": section_3.get("header", ""),
            "section3_text": section_3.get("text", ""),
            "product_cta": content_body.get("product_call_to_action", "")
        }

    except json.JSONDecodeError as e:
        print(f"⚠️ JSON 解析失败: {e}")
        print(f"原始内容: {cleaned_content[:200]}...")
        # 返回空值，让调用者处理
        return {
            "note_title": "",
            "cover_text": "",
            "intro": "",
            "section1_header": "",
            "section1_text": "",
            "section2_header": "",
            "section2_text": "",
            "section3_header": "",
            "section3_text": "",
            "product_cta": ""
        }


# ==================== 保存结果 ====================

def save_results(results: list, start_date: str = None, end_date: str = None):
    """
    保存生成结果为CSV

    参数:
        results: 生成结果列表
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    """
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 转换为DataFrame
    df = pd.DataFrame(results)

    # 生成动态文件名
    if start_date and end_date:
        # 格式化日期：YYYY-MM-DD -> YYYYMMDD
        start_formatted = start_date.replace("-", "")
        end_formatted = end_date.replace("-", "")
        filename = f"Content_{start_formatted}_to_{end_formatted}.csv"
    elif results:
        # 如果没有指定日期范围，使用结果中的第一个和最后一个日期
        first_date = results[0].get("Date", "unknown")
        last_date = results[-1].get("Date", "unknown")
        first_formatted = first_date.replace("-", "")
        last_formatted = last_date.replace("-", "")
        filename = f"Content_{first_formatted}_to_{last_formatted}.csv"
    else:
        filename = "Content_Undated.csv"

    output_file = OUTPUT_DIR / filename

    # 保存
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"\n💾 结果已保存: {output_file}")
    print(f"   总计: {len(results)} 篇内容")

    return output_file


# ==================== 主程序 ====================

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="悟昕睡眠科普内容生成器 - 支持日期范围过滤",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 生成今天之后7天的内容
  python main.py

  # 生成指定日期范围的内容
  python main.py --start_date 2026-02-09 --end_date 2026-02-15

  # 从某个日期开始生成，到营销日历结束
  python main.py --start_date 2026-06-01

  # 生成营销日历中某个日期之前的内容
  python main.py --end_date 2026-03-31
        """
    )

    parser.add_argument(
        "--start_date",
        type=str,
        default=None,
        help="开始日期 (格式: YYYY-MM-DD)。默认为当天日期"
    )

    parser.add_argument(
        "--end_date",
        type=str,
        default=None,
        help="结束日期 (格式: YYYY-MM-DD)。默认为开始日期+7天"
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="生成营销日历中的全部内容（忽略日期范围限制）"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="显示详细输出信息（默认启用）"
    )

    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()

    # 确定日期范围
    today = datetime.now().date()

    if args.full:
        # 生成全部内容
        filter_start_date = None
        filter_end_date = None
        print("📋 模式：生成全部内容（营销日历范围）")
    else:
        # 处理开始日期
        if args.start_date:
            try:
                filter_start_date = args.start_date
            except ValueError:
                print(f"❌ 开始日期格式错误: {args.start_date}")
                print("   请使用格式: YYYY-MM-DD (例如: 2026-02-09)")
                return 1
        else:
            filter_start_date = today.strftime("%Y-%m-%d")

        # 处理结束日期
        if args.end_date:
            try:
                filter_end_date = args.end_date
            except ValueError:
                print(f"❌ 结束日期格式错误: {args.end_date}")
                print("   请使用格式: YYYY-MM-DD (例如: 2026-02-15)")
                return 1
        else:
            # 默认：开始日期 + 7天
            start_dt = datetime.strptime(filter_start_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=7)
            filter_end_date = end_dt.strftime("%Y-%m-%d")

        print(f"📋 日期范围: {filter_start_date} ~ {filter_end_date}")

    print("=" * 70)
    print("🌙 Wuxin Zenoasis Content Project")
    print("小红书睡眠科普图文生成器 v3.1 - 命令行参数版")
    print("=" * 70)

    # 1. 加载API密钥
    api_key = load_api_key()
    print(f"✅ API Key: {api_key[:20]}...{api_key[-10:]}")

    # 2. 加载资产
    calendar_df = load_marketing_calendar()
    if calendar_df is None:
        return 1

    concepts = load_science_concepts()
    if not concepts:
        print("❌ 科学概念库为空，无法继续")
        return 1

    general_topics = load_general_topics_extended()
    if not general_topics:
        print("⚠️ 通用主题库为空，将仅使用营销节点")

    assets = load_assets()

    # 3. 并发生成内容（支持日期过滤）
    results = generate_all_contents(
        api_key,
        calendar_df,
        concepts,
        general_topics,
        filter_start_date=filter_start_date if not args.full else None,
        filter_end_date=filter_end_date if not args.full else None
    )

    # 4. 保存结果（使用动态文件名）
    output_file = save_results(
        results,
        start_date=filter_start_date if not args.full else None,
        end_date=filter_end_date if not args.full else None
    )

    # 5. 统计信息
    if results:
        df = pd.DataFrame(results)
        marketing_count = df[df["Is_Marketing_Node"] == "Yes"].shape[0]
        general_count = df[df["Is_Marketing_Node"] == "No"].shape[0]

        print("\n" + "=" * 70)
        print("📊 内容生成统计")
        print("=" * 70)
        print(f"营销节点: {marketing_count} 篇")
        print(f"通用主题: {general_count} 篇")
        print(f"总计: {len(results)} 篇")

        if general_count > 0:
            print("\n📈 人群分布（通用主题）:")
            general_df = df[df["Is_Marketing_Node"] == "No"]
            audience_counts = general_df["Audience"].value_counts()
            for audience, count in audience_counts.items():
                print(f"   {audience}: {count} 篇")

        print(f"\n📁 输出文件: {output_file}")

    print("\n✅ 全部完成！")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

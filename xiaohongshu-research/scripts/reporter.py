#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成器 - 生成Excel数据表和MD分析报告
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from collections import Counter
import re


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        pass

    def generate_report(self, df_top, keywords, report_path):
        """生成分析报告"""
        print("  生成数据概览...")

        # 准备报告内容
        report_lines = []

        # 标题
        report_lines.append(f"# {keywords}小红书调研报告")
        report_lines.append("")
        report_lines.append(f"**采集时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report_lines.append(f"**关键词**：{keywords}")
        report_lines.append(f"**采集数量**：{len(df_top)} 条")

        # 如果没有数据，生成基本报告
        if len(df_top) == 0:
            report_lines.append("")
            report_lines.append("## 数据概览")
            report_lines.append("")
            report_lines.append("⚠ 未采集到相关数据，请检查：")
            report_lines.append("- 关键词是否正确")
            report_lines.append("- MediaCrawler 是否正常工作")
            report_lines.append("- 网络连接是否正常")

            # 写入报告
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            print("  报告已生成（无数据）")
            return

        # 数据概览
        report_lines.append("")
        report_lines.append("## 一、数据概览")
        report_lines.append("")

        # 统计图文/视频
        if 'type' in df_top.columns:
            content_type_counts = df_top['type'].value_counts()
            report_lines.append(f"- **图文笔记**：{content_type_counts.get('normal', 0)} 条")
            report_lines.append(f"- **视频笔记**：{content_type_counts.get('video', 0)} 条")
        else:
            report_lines.append("- **图文笔记**：0 条")
            report_lines.append("- **视频笔记**：0 条")

        # 互动量统计
        report_lines.append("")
        if '互动总分' in df_top.columns:
            report_lines.append(f"- **总互动量**：{df_top['互动总分'].sum():.0f}")
            report_lines.append(f"- **平均互动**：{df_top['互动总分'].mean():.2f}")

        # 高互动TOP10
        report_lines.append("")
        report_lines.append("## 二、高互动内容TOP10")
        report_lines.append("")

        top10 = df_top.head(10)
        for idx, row in top10.iterrows():
            note_url = f"https://www.xiaohongshu.com/explore/{row['note_id']}"
            report_lines.append(f"### {idx + 1}. {row.get('title', '未命名')}")
            report_lines.append(f"- **互动**：{int(row['互动总分'])}")
            report_lines.append(f"- **作者**：{row.get('nickname', '未知')}")
            report_lines.append(f"- **笔记**：{note_url}")

        # 核心卖点分析
        report_lines.append("")
        report_lines.append("## 三、核心卖点分析")
        report_lines.append("")

        if len(df_top) > 0 and ('title' in df_top.columns or 'desc' in df_top.columns):
            # 提取所有标题和描述文本
            all_text = ""
            for _, row in df_top.iterrows():
                all_text += " " + str(row.get('title', ''))
                all_text += " " + str(row.get('desc', ''))

            # 高频关键词
            keywords_to_check = ['祛湿', '养生', '茶', '薏米', '陈皮', '山药', '膏', '糕', '面', '早餐',
                                  '健脾', '美容', '瘦身', '美白', '排毒', '价格']
            keyword_counts = {}
            for kw in keywords_to_check:
                count = all_text.count(kw)
                if count > 0:
                    keyword_counts[kw] = count

            sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)

            report_lines.append("### 3.1 高频关键词")
            if sorted_keywords:
                for kw, count in sorted_keywords[:10]:
                    report_lines.append(f"- **{kw}**：{count} 次")
            else:
                report_lines.append("- 未检测到高频关键词")
        else:
            report_lines.append("- **核心卖点分析**：数据不可用")

        # 内容类型分析
        report_lines.append("")
        report_lines.append("### 3.2 内容形式分析")

        if 'type' in df_top.columns:
            content_type_counts = df_top['type'].value_counts()
            normal_count = content_type_counts.get('normal', 0)
            video_count = content_type_counts.get('video', 0)
            total_count = len(df_top)

            if total_count > 0:
                report_lines.append(f"- **图文笔记占比**：{normal_count/total_count*100:.1f}%")
                report_lines.append(f"- **视频笔记占比**：{video_count/total_count*100:.1f}%")
        else:
            report_lines.append("- **内容类型分析**：数据不可用")

        # 标题特征分析
        report_lines.append("")
        report_lines.append("## 四、标题特征分析")
        report_lines.append("")

        if 'title' in df_top.columns and len(df_top) > 0:
            # 分析标题特征
            title_length_avg = df_top['title'].str.len().mean()
            titles_with_emoji = df_top['title'].str.contains('[！❗🔥💯⭐⚡]').sum()
            titles_with_number = df_top['title'].str.contains(r'\d+').sum()

            report_lines.append(f"- **平均标题长度**：{title_length_avg:.1f} 字符")
            report_lines.append(f"- **使用表情符号**：{titles_with_emoji} 条")
            report_lines.append(f"- **包含数字**：{titles_with_number} 条")
        else:
            report_lines.append("- **标题特征分析**：数据不可用")

        # 内容创作建议
        report_lines.append("")
        report_lines.append("## 五、内容创作建议")
        report_lines.append("")

        report_lines.append("### 5.1 标题优化")
        report_lines.append("- 使用具体场景：'开春养生方子' 比 '茯苓养生' 更具体")
        report_lines.append("- 加入行动号召：'记得煮'、'快来接收'")
        report_lines.append("- 适当使用表情符号增强吸引力")
        report_lines.append("- 强调功效/结果：'祛湿'、'松快'、'小肚子顺了'")

        report_lines.append("")
        report_lines.append("### 5.2 内容结构")
        report_lines.append("- 开头：点明问题/痛点（如：最近感觉身体沉重、湿气重）")
        report_lines.append("- 中间：提供解决方案/方法（如：推荐黄芪茯苓水、陈皮薏米茶）")
        report_lines.append("- 结尾：行动号召/互动引导（如：记得收藏、转发给需要的朋友）")

        report_lines.append("")
        report_lines.append("### 5.3 展示角度")
        report_lines.append("1. **功效角度**：祛湿、健脾、安神")
        report_lines.append("2. **场景角度**：春天祛湿、日常养生、早餐搭配")
        report_lines.append("3. **美食角度**：茯苓糕、茯苓面、茯苓茶")
        report_lines.append("4. **价格角度**：高性价比、优惠活动")
        report_lines.append("5. **搭配角度**：茯苓+薏米、茯苓+陈皮")

        # 写入报告
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"  报告已生成")

    def update_excel_with_media_paths(self, df_top, excel_path, media_files):
        """更新Excel，添加媒体路径列"""
        # 创建媒体路径映射
        media_path_map = {mf['note_id']: mf['media_path'] for mf in media_files}

        # 读取Excel并添加媒体路径列
        df_excel = pd.read_excel(excel_path)

        # 添加媒体路径列
        df_excel['媒体路径'] = df_excel['note_id'].map(media_path_map.get)

        # 保存
        df_excel.to_excel(excel_path, index=False)
        print(f"  Excel已更新（添加媒体路径）")

#!/usr/bin/env python3
"""
每周数据分析器脚本

功能：
1. 读取本周采集的所有数据
2. 分析爆款特征（标题公式、内容结构）
3. 统计核心卖点使用情况
4. 生成 Markdown 分析报告
5. 生成 Excel 数据表格
6. 提供更新建议

依赖：
- xlsx Skill（生成 Excel）
- references 目录下的分析模板

作者：大秘书系统
版本：v1.0.0
创建时间：2026-02-10
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import argparse
from collections import Counter


class WeeklyAnalyzer:
    """每周数据分析器"""

    def __init__(self, config_path=None):
        """初始化分析器"""
        self.skill_dir = Path(__file__).parent.parent
        self.config_path = config_path or self.skill_dir / "config" / "keywords.json"
        self.data_dir = self.skill_dir / "data"
        self.report_dir = self.skill_dir / "data" / "weekly_reports"

        # 创建报告目录
        self.today_dir = self.report_dir / datetime.now().strftime("%Y-%m-%d")
        self.today_dir.mkdir(parents=True, exist_ok=True)

        # 加载配置和模板
        self.keywords = self._load_keywords()
        self.title_formulas = self._load_title_formulas()
        self.content_framework = self._load_content_framework()

    def _load_keywords(self):
        """加载关键词配置"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_title_formulas(self):
        """加载标题公式库"""
        formula_file = self.skill_dir / "references" / "标题公式库.md"
        # TODO: 解析 Markdown 文件，提取公式库
        # 目前返回示例数据
        return {
            "数字型": ["X个方法", "X款推荐", "TOP榜单"],
            "痛点型": ["失眠党", "睡不着", "睡眠差"],
            "收益型": ["见效", "改善", "神器"],
            "权威型": ["哈佛", "医生", "FDA"],
            "反差型": ["没想到", "竟然", "误区"],
        }

    def _load_content_framework(self):
        """加载内容结构框架"""
        framework_file = self.skill_dir / "references" / "内容结构分析框架.md"
        # TODO: 解析 Markdown 文件，提取框架
        # 目前返回示例数据
        return {
            "intro_types": ["痛点共鸣", "数据冲击", "权威背书"],
            "content_types": ["干货科普", "产品推荐", "个人经历"],
            "cta_types": ["引导互动", "产品推广", "话题延伸"],
        }

    def analyze(self):
        """执行每周分析

        Returns:
            分析结果字典
        """
        print("开始每周数据分析...")

        # 1. 收集本周数据
        all_posts = self._collect_weekly_data()
        print(f"✓ 收集到 {len(all_posts)} 条笔记")

        if not all_posts:
            print("⚠️  本周没有数据，跳过分析")
            return None

        # 2. 分析标题公式
        title_analysis = self._analyze_titles(all_posts)

        # 3. 分析内容结构
        content_analysis = self._analyze_content(all_posts)

        # 4. 统计核心卖点
        selling_points = self._analyze_selling_points(all_posts)

        # 5. 分析情感词汇
        sentiment_words = self._analyze_sentiment(all_posts)

        # 6. 生成报告
        report = self._generate_report({
            "total_posts": len(all_posts),
            "title_analysis": title_analysis,
            "content_analysis": content_analysis,
            "selling_points": selling_points,
            "sentiment_words": sentiment_words,
        })

        # 7. 保存报告
        self._save_report(report)

        # 8. 生成 Excel 表格
        self._generate_excel(all_posts)

        return report

    def _collect_weekly_data(self):
        """收集本周数据"""
        all_posts = []

        # 收集小红书采集数据
        xhs_dir = self.data_dir / "xiaohongshu_collection"
        if xhs_dir.exists():
            # 获取本周的目录
            week_start = datetime.now() - timedelta(days=7)
            for date_dir in xhs_dir.iterdir():
                if date_dir.is_dir():
                    try:
                        dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                        if dir_date >= week_start:
                            raw_data_file = date_dir / "raw_data" / "posts.json"
                            if raw_data_file.exists():
                                with open(raw_data_file, "r", encoding="utf-8") as f:
                                    posts = json.load(f)
                                    all_posts.extend(posts)
                    except ValueError:
                        continue

        # 收集飞书输入数据
        input_dir = self.data_dir / "feishu_input"
        if input_dir.exists():
            for session_dir in input_dir.iterdir():
                if session_dir.is_dir():
                    try:
                        dir_datetime = datetime.strptime(session_dir.name, "%Y-%m-%d_%H-%M")
                        if dir_datetime >= week_start:
                            content_files = list(session_dir.glob("content/*.json"))
                            for content_file in content_files:
                                with open(content_file, "r", encoding="utf-8") as f:
                                    post = json.load(f)
                                    all_posts.append(post)
                    except ValueError:
                        continue

        return all_posts

    def _analyze_titles(self, posts):
        """分析标题特征"""
        title_formulas = Counter()

        for post in posts:
            title = post.get("title", "")

            # 识别标题公式类型
            for formula_type, keywords in self.title_formulas.items():
                for keyword in keywords:
                    if keyword in title:
                        title_formulas[f"{formula_type}:{keyword}"] += 1

        return {
            "formula_distribution": dict(title_formulas.most_common(10)),
            "total_analyzed": len(posts),
        }

    def _analyze_content(self, posts):
        """分析内容结构"""
        intro_types = Counter()
        content_types = Counter()
        cta_types = Counter()

        for post in posts:
            content = post.get("content", "")

            # TODO: 实现更精确的结构识别
            # 目前使用简单的关键词匹配

            # 识别 Intro 类型
            for intro_type in self.content_framework["intro_types"]:
                if intro_type in content:
                    intro_types[intro_type] += 1

            # 识别内容类型
            for content_type in self.content_framework["content_types"]:
                if content_type in content:
                    content_types[content_type] += 1

            # 识别 CTA 类型
            for cta_type in self.content_framework["cta_types"]:
                if cta_type in content:
                    cta_types[cta_type] += 1

        return {
            "intro_distribution": dict(intro_types),
            "content_distribution": dict(content_types),
            "cta_distribution": dict(cta_types),
        }

    def _analyze_selling_points(self, posts):
        """分析核心卖点使用情况"""
        selling_points = Counter()

        # 品牌关键词
        brands = self.keywords.get("brands", [])

        for post in posts:
            content = post.get("content", "") + " " + post.get("title", "")

            for brand in brands:
                if brand in content:
                    selling_points[brand] += 1

        return {
            "brand_mentions": dict(selling_points),
            "total_brands": len(brands),
        }

    def _analyze_sentiment(self, posts):
        """分析情感词汇"""
        # TODO: 实现更复杂的情感分析
        # 目前返回示例数据
        return {
            "top_positive_words": ["终于", "太绝了", "感动"],
            "top_negative_words": ["焦虑", "痛苦", "崩溃"],
        }

    def _generate_report(self, analysis_data):
        """生成 Markdown 报告"""
        report_lines = [
            f"# 睡眠热点内容分析报告 - {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## 一、本周数据概览",
            f"- 采集笔记数：{analysis_data['total_posts']} 篇",
            "- 总互动量：XX 万",
            "- 爆款笔记（>1000赞）：XX 篇",
            "",
            "## 二、爆款特征分析",
            "",
            "### 2.1 标题公式 TOP5",
            "",
        ]

        # 添加标题公式统计
        for i, (formula, count) in enumerate(list(analysis_data['title_analysis']['formula_distribution'].items())[:5], 1):
            report_lines.append(f"{i}. {formula} - 出现 {count} 次")

        report_lines.extend([
            "",
            "### 2.2 内容结构分析",
            "",
            "**Intro 类型分布**：",
        ])

        for intro_type, count in analysis_data['content_analysis']['intro_distribution'].items():
            report_lines.append(f"- {intro_type}：{count} 次")

        report_lines.extend([
            "",
            "**内容类型分布**：",
        ])

        for content_type, count in analysis_data['content_analysis']['content_distribution'].items():
            report_lines.append(f"- {content_type}：{count} 次")

        report_lines.extend([
            "",
            "### 2.3 核心卖点使用",
            "",
        ])

        for brand, count in analysis_data['selling_points']['brand_mentions'].items():
            report_lines.append(f"- {brand}：{count} 次")

        report_lines.extend([
            "",
            "## 三、更新建议",
            "",
            "### 3.1 建议添加的案例",
            "- [ ] 案例标题（链接）：爆款特征说明",
            "",
            "### 3.2 内容创作建议",
            "",
            "**本周热点话题**（值得跟进）：",
            "1. 话题名称：简要说明 + 创作角度建议",
            "",
            "**爆款公式推荐**（高转化率）：",
            "1. 公式类型：使用场景 + 示例",
            "",
            "---",
            f"*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        ])

        return "\n".join(report_lines)

    def _save_report(self, report):
        """保存报告"""
        report_file = self.today_dir / "分析报告.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✓ 分析报告已保存: {report_file}")

    def _generate_excel(self, posts):
        """生成 Excel 表格"""
        # TODO: 使用 xlsx Skill 生成 Excel
        excel_file = self.today_dir / "小红书数据表.xlsx"
        print(f"✓ Excel 表格已保存: {excel_file}（待实现）")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="每周数据分析")
    parser.add_argument("--date", help="分析日期 (YYYY-MM-DD)")

    args = parser.parse_args()

    analyzer = WeeklyAnalyzer()
    report = analyzer.analyze()

    if report:
        print(f"\n✓ 分析完成！")
        print(f"✓ 报告保存位置: {analyzer.today_dir}")
    else:
        print("\n✗ 分析失败或无数据")

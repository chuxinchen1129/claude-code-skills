#!/usr/bin/env python3
"""
小红书自动采集脚本

功能：
1. 使用 MediaCrawler Skill 采集小红书数据
2. 按互动量排序，取 TOP30
3. 下载封面图片和视频
4. 视频转文字（如果有）
5. 保存数据到指定目录

依赖：
- MediaCrawler Skill
- video-scripts-extract Skill

作者：大秘书系统
版本：v1.0.0
创建时间：2026-02-10
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import argparse


class XiaohongshuCollector:
    """小红书数据采集器"""

    def __init__(self, config_path=None):
        """初始化采集器

        Args:
            config_path: 配置文件路径
        """
        self.skill_dir = Path(__file__).parent.parent
        self.config_path = config_path or self.skill_dir / "config" / "platforms.json"
        self.data_dir = self.skill_dir / "data" / "xiaohongshu_collection"

        # 创建数据目录
        self.today_dir = self.data_dir / datetime.now().strftime("%Y-%m-%d")
        self.today_dir.mkdir(parents=True, exist_ok=True)

        # 创建子目录
        (self.today_dir / "raw_data").mkdir(exist_ok=True)
        (self.today_dir / "covers").mkdir(exist_ok=True)
        (self.today_dir / "videos").mkdir(exist_ok=True)
        (self.today_dir / "transcripts").mkdir(exist_ok=True)
        (self.today_dir / "analysis").mkdir(exist_ok=True)

        # 加载配置
        self.config = self._load_config()

    def _load_config(self):
        """加载配置文件"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def collect(self, keywords=None, limit=100, top_n=30):
        """采集小红书数据

        Args:
            keywords: 采集关键词列表
            limit: 采集数量限制
            top_n: 取 TOP N 高互动笔记

        Returns:
            采集到的笔记列表
        """
        # 获取配置中的关键词
        if keywords is None:
            keywords = self._get_keywords()

        print(f"开始采集小红书数据...")
        print(f"关键词: {', '.join(keywords)}")
        print(f"采集限制: {limit}")
        print(f"取 TOP: {top_n}")

        # TODO: 调用 MediaCrawler Skill
        # 这里需要集成 MediaCrawler Skill 的 API
        # 目前返回示例数据

        posts = self._mock_collect_data(keywords, limit)

        # 按互动量排序
        posts.sort(key=lambda x: x.get("likes", 0) + x.get("comments", 0) + x.get("collects", 0), reverse=True)

        # 取 TOP N
        top_posts = posts[:top_n]

        # 保存原始数据
        self._save_raw_data(top_posts)

        # 处理多媒体
        self._process_media(top_posts)

        return top_posts

    def _get_keywords(self):
        """获取配置中的关键词"""
        keywords_path = self.skill_dir / "config" / "keywords.json"
        with open(keywords_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("xiaohongshu", ["睡眠仪", "左点", "睡眠"])

    def _mock_collect_data(self, keywords, limit):
        """模拟采集数据（待替换为真实 MediaCrawler 调用）"""
        # TODO: 替换为真实的 MediaCrawler Skill 调用
        mock_data = []
        for i in range(min(limit, 10)):
            mock_data.append({
                "id": f"mock_{i}",
                "title": f"示例笔记 {i+1}",
                "content": f"示例内容 {i+1}",
                "likes": 1000 - i * 100,
                "comments": 100 - i * 10,
                "collects": 500 - i * 50,
                "author": f"用户{i+1}",
                "cover_url": "",
                "video_url": ""
            })
        return mock_data

    def _save_raw_data(self, posts):
        """保存原始数据"""
        raw_data_path = self.today_dir / "raw_data" / "posts.json"
        with open(raw_data_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"✓ 原始数据已保存: {raw_data_path}")

    def _process_media(self, posts):
        """处理多媒体内容"""
        # TODO: 下载封面图片
        # TODO: 下载视频
        # TODO: 视频转文字
        print("✓ 多媒体处理完成（待实现）")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小红书数据采集")
    parser.add_argument("--keywords", nargs="+", help="采集关键词")
    parser.add_argument("--limit", type=int, default=100, help="采集数量限制")
    parser.add_argument("--top", type=int, default=30, help="取 TOP N")

    args = parser.parse_args()

    collector = XiaohongshuCollector()
    posts = collector.collect(
        keywords=args.keywords,
        limit=args.limit,
        top_n=args.top
    )

    print(f"\n✓ 采集完成！共获取 {len(posts)} 条笔记")
    print(f"✓ 数据保存位置: {collector.today_dir}")


if __name__ == "__main__":
    main()

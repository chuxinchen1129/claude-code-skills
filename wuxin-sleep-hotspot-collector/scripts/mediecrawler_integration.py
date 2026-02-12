#!/usr/bin/env python3
"""
MediaCrawler 集成脚本

功能：
1. 调用 MediaCrawler 采集小红书数据
2. 读取采集的 JSON 数据
3. 转换并保存到 Skill 数据目录
4. 下载视频和封面图片

依赖：
- MediaCrawler（/Users/echochen/MediaCrawler）

作者：大秘书系统
版本：v1.0.0
创建时间：2026-02-10
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import argparse
import re


class MediaCrawlerIntegration:
    """MediaCrawler 集成器"""

    def __init__(self):
        """初始化集成器"""
        self.skill_dir = Path(__file__).parent.parent
        self.mediacrawler_dir = Path("/Users/echochen/MediaCrawler")
        self.mediacrawler_data_dir = self.mediacrawler_dir / "data" / "xhs"

        # 数据目录
        self.data_dir = self.skill_dir / "data" / "xiaohongshu_collection"
        self.today_dir = self.data_dir / datetime.now().strftime("%Y-%m-%d")

        # 创建数据目录
        self.today_dir.mkdir(parents=True, exist_ok=True)
        (self.today_dir / "raw_data").mkdir(exist_ok=True)
        (self.today_dir / "covers").mkdir(exist_ok=True)
        (self.today_dir / "videos").mkdir(exist_ok=True)
        (self.today_dir / "transcripts").mkdir(exist_ok=True)
        (self.today_dir / "analysis").mkdir(exist_ok=True)

        # 配置文件路径
        self.config_file = self.mediacrawler_dir / "config" / "base_config.py"
        self.backup_config = self.mediacrawler_dir / "config" / "base_config.py.backup_wuxin"

    def backup_config(self):
        """备份原始配置"""
        if not self.backup_config.exists():
            shutil.copy2(self.config_file, self.backup_config)
            print(f"✓ 配置文件已备份: {self.backup_config}")
        else:
            print(f"✓ 配置备份已存在")

    def restore_config(self):
        """恢复原始配置"""
        if self.backup_config.exists():
            shutil.copy2(self.backup_config, self.config_file)
            print(f"✓ 配置已恢复")
            # 删除备份
            self.backup_config.unlink()
        else:
            print(f"⚠️  备份文件不存在，跳过恢复")

    def modify_config(self, keywords):
        """修改配置文件

        Args:
            keywords: 关键词列表
        """
        # 读取配置
        with open(self.config_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 修改关键词
        keywords_str = ",".join(keywords)
        content_new = re.sub(
            r'KEYWORDS = ".*?"',
            f'KEYWORDS = "{keywords_str}"',
            content
        )

        # 设置平台为小红书
        content_new = re.sub(
            r'PLATFORM = ".*?"',
            'PLATFORM = "xhs"',
            content_new
        )

        # 设置数据保存类型为 json
        content_new = re.sub(
            r'SAVE_DATA_OPTION = ".*?"',
            'SAVE_DATA_OPTION = "json"',
            content_new
        )

        # 确保开启媒体下载
        content_new = re.sub(
            r'ENABLE_GET_MEIDAS = (True|False)',
            'ENABLE_GET_MEIDAS = True',
            content_new
        )

        # 确保开启评论爬取
        content_new = re.sub(
            r'ENABLE_GET_COMMENTS = (True|False)',
            'ENABLE_GET_COMMENTS = True',
            content_new
        )

        # 设置爬取数量
        content_new = re.sub(
            r'CRAWLER_MAX_NOTES_COUNT = \d+',
            'CRAWLER_MAX_NOTES_COUNT = 50',
            content_new
        )

        # 写回配置
        with open(self.config_file, "w", encoding="utf-8") as f:
            f.write(content_new)

        print(f"✓ 配置已修改:")
        print(f"  - 平台: xhs")
        print(f"  - 关键词: {keywords_str}")
        print(f"  - 爬取数量: 50")
        print(f"  - 媒体下载: 已启用")
        print(f"  - 评论爬取: 已启用")

    def run_crawler(self):
        """运行 MediaCrawler

        Returns:
            bool: 是否成功
        """
        print(f"\n开始运行 MediaCrawler...")

        # 切换到 MediaCrawler 目录
        original_dir = os.getcwd()
        os.chdir(self.mediacrawler_dir)

        try:
            # 运行 MediaCrawler
            result = subprocess.run(
                [sys.executable, "main.py"],
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )

            if result.returncode == 0:
                print("✓ MediaCrawler 运行成功")
                return True
            else:
                print(f"⚠️  MediaCrawler 运行出错:")
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("⚠️  MediaCrawler 运行超时（10分钟）")
            return False
        except Exception as e:
            print(f"⚠️  运行失败: {e}")
            return False
        finally:
            os.chdir(original_dir)

    def read_mediacrawler_data(self):
        """读取 MediaCrawler 采集的数据

        Returns:
            list: 采集的笔记列表
        """
        all_posts = []

        # 查找最新的 JSON 文件
        json_files = list(self.mediacrawler_data_dir.glob("json/search_contents_*.json"))

        if not json_files:
            print("⚠️  未找到采集数据")
            return []

        # 按时间排序，取最新的
        json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        latest_file = json_files[0]

        print(f"✓ 读取数据: {latest_file}")

        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                all_posts = json.load(f)
            print(f"✓ 共读取 {len(all_posts)} 条笔记")
        except Exception as e:
            print(f"✗ 读取数据失败: {e}")

        return all_posts

    def convert_posts(self, posts):
        """转换笔记数据格式

        Args:
            posts: MediaCrawler 格式的笔记列表

        Returns:
            list: 转换后的笔记列表
        """
        converted = []

        for post in posts:
            # 解析点赞数（处理 "5.4万" 这样的格式）
            liked_count = post.get("liked_count", "0")
            if isinstance(liked_count, str):
                if "万" in liked_count:
                    liked_count = float(liked_count.replace("万", "")) * 10000
                else:
                    liked_count = int(liked_count.replace(",", ""))

            # 解析收藏数
            collected_count = post.get("collected_count", "0")
            if isinstance(collected_count, str):
                collected_count = int(collected_count.replace(",", ""))

            # 解析评论数
            comment_count = post.get("comment_count", "0")
            if isinstance(comment_count, str):
                comment_count = int(comment_count.replace(",", ""))

            # 转换时间戳
            time_ms = post.get("time", 0)
            time_str = datetime.fromtimestamp(time_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")

            converted_post = {
                "id": post.get("note_id", ""),
                "title": post.get("title", ""),
                "content": post.get("desc", ""),
                "likes": int(liked_count),
                "comments": int(comment_count),
                "collects": int(collected_count),
                "shares": int(post.get("share_count", "0").replace(",", "")),
                "author": post.get("nickname", ""),
                "author_id": post.get("user_id", ""),
                "avatar": post.get("avatar", ""),
                "type": post.get("type", "normal"),
                "video_url": post.get("video_url", ""),
                "cover_url": post.get("image_list", ""),
                "note_url": post.get("note_url", ""),
                "source_keyword": post.get("source_keyword", ""),
                "ip_location": post.get("ip_location", ""),
                "time": time_str,
                "tags": post.get("tag_list", ""),
            }

            converted.append(converted_post)

        return converted

    def save_posts(self, posts):
        """保存转换后的数据

        Args:
            posts: 转换后的笔记列表
        """
        # 保存原始数据
        raw_data_file = self.today_dir / "raw_data" / "posts.json"
        with open(raw_data_file, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"✓ 数据已保存: {raw_data_file}")

        # 按 TOP N 排序并保存
        posts_sorted = sorted(
            posts,
            key=lambda x: x.get("likes", 0) + x.get("comments", 0) + x.get("collects", 0),
            reverse=True
        )

        top_data_file = self.today_dir / "raw_data" / "posts_top30.json"
        with open(top_data_file, "w", encoding="utf-8") as f:
            json.dump(posts_sorted[:30], f, ensure_ascii=False, indent=2)
        print(f"✓ TOP30 数据已保存: {top_data_file}")

        return posts_sorted

    def collect(self, keywords=None, max_notes=50):
        """执行采集流程

        Args:
            keywords: 关键词列表
            max_notes: 最大采集数量

        Returns:
            list: 采集的笔记列表
        """
        # 获取默认关键词
        if keywords is None:
            keywords_path = self.skill_dir / "config" / "keywords.json"
            with open(keywords_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                keywords = config.get("xiaohongshu", ["睡眠仪", "左点", "睡眠"])

        print("=" * 80)
        print("MediaCrawler 集成采集")
        print("=" * 80)
        print(f"关键词: {', '.join(keywords)}")
        print(f"最大采集数: {max_notes}")
        print()

        # 1. 备份配置
        print("[1/6] 备份配置...")
        self.backup_config()

        # 2. 修改配置
        print("\n[2/6] 修改配置...")
        self.modify_config(keywords)

        # 3. 运行采集
        print("\n[3/6] 运行 MediaCrawler...")
        print("⚠️  请在浏览器中完成登录...")
        success = self.run_crawler()

        if not success:
            print("\n⚠️  采集失败，尝试读取已有数据...")

        # 4. 读取数据
        print("\n[4/6] 读取采集数据...")
        posts = self.read_mediacrawler_data()

        if not posts:
            print("✗ 没有采集到数据")
            self.restore_config()
            return []

        # 5. 转换数据
        print("\n[5/6] 转换数据格式...")
        converted_posts = self.convert_posts(posts)

        # 6. 保存数据
        print("\n[6/6] 保存数据...")
        sorted_posts = self.save_posts(converted_posts)

        # 恢复配置
        print("\n恢复配置...")
        self.restore_config()

        print("\n" + "=" * 80)
        print(f"✓ 采集完成！共获取 {len(converted_posts)} 条笔记")
        print(f"✓ TOP30 平均点赞: {sum(p['likes'] for p in sorted_posts[:30]) // 30}")
        print(f"✓ 数据保存位置: {self.today_dir}")
        print("=" * 80)

        return sorted_posts


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MediaCrawler 集成采集")
    parser.add_argument("--keywords", nargs="+", help="采集关键词")
    parser.add_argument("--max", type=int, default=50, help="最大采集数量")

    args = parser.parse_args()

    integrator = MediaCrawlerIntegration()
    integrator.collect(
        keywords=args.keywords,
        max_notes=args.max
    )


if __name__ == "__main__":
    main()

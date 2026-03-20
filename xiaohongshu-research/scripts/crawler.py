#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediaCrawler 集成 - 采集小红书数据
"""

import json
import os
import subprocess
import time
from pathlib import Path


class XHSCrawler:
    """小红书数据采集器"""

    def __init__(self):
        self.mediacrawler_path = Path.home() / "MediaCrawler"
        self.config_path = self.mediacrawler_path / "config" / "base_config.py"
        self.data_path = Path("/Users/echochen/Desktop/DMS/01_INFO_COLLECT/采集数据/xhs")
        self.json_path = self.data_path / "json"
        self.images_path = self.data_path / "images"
        self.videos_path = self.data_path / "videos"

    def clear_cache(self):
        """清空MediaCrawler缓存"""
        # 删除旧的JSON文件
        for json_file in self.json_path.glob("search_contents_*.json"):
            json_file.unlink()
        # 删除images和videos目录
        if self.images_path.exists():
            import shutil
            shutil.rmtree(self.images_path)
        if self.videos_path.exists():
            import shutil
            shutil.rmtree(self.videos_path)
        # 重新创建目录
        self.images_path.mkdir(parents=True, exist_ok=True)
        self.videos_path.mkdir(parents=True, exist_ok=True)

    def update_config(self, keywords, count):
        """更新MediaCrawler配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 替换关键词
        content = content.replace(
            f'KEYWORDS = ".*?"',
            f'KEYWORDS = "{keywords}"'
        )

        # 替换数量
        content = content.replace(
            r'CRAWLER_MAX_NOTES_COUNT = \d+',
            f'CRAWLER_MAX_NOTES_COUNT = {count}'
        )

        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def crawl(self, keywords, count):
        """执行MediaCrawler采集"""
        # 处理关键词：支持单个字符串或列表
        if isinstance(keywords, str):
            keyword_list = [keywords]
        else:
            keyword_list = keywords

        all_data = []

        # 对每个关键词进行采集
        for kw in keyword_list:
            print(f"  采集关键词: {kw}")

            # 更新配置
            self.update_config(kw, count)

            # 执行采集
            print(f"  启动MediaCrawler...")
            os.chdir(self.mediacrawler_path)

            # 使用uv run执行
            cmd = [
                "uv", "run", "main.py"
            ]

            try:
                # 在MediaCrawler目录中执行
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',  # 忽略编码错误
                    timeout=600  # 10分钟超时
                )

                if result.returncode != 0:
                    print(f"  ⚠ MediaCrawler执行可能有问题，返回码: {result.returncode}")
                    print(f"  错误信息: {result.stderr}")
                else:
                    print(f"  MediaCrawler已完成")

                    # 等待文件生成
                    time.sleep(2)

                    # 读取JSON数据
                    json_files = list(self.json_path.glob("search_contents_*.json"))
                    if json_files:
                        # 取最新的文件
                        latest_json = max(json_files, key=lambda p: p.stat().st_mtime)
                        try:
                            with open(latest_json, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                all_data.extend(data)
                                print(f"  采集到 {len(data)} 条")
                        except (json.JSONDecodeError, UnicodeDecodeError) as e:
                            print(f"  ⚠ JSON文件解析失败: {e}")
                            # 尝试其他编码
                            try:
                                with open(latest_json, 'r', encoding='gbk') as f:
                                    data = json.load(f)
                                    all_data.extend(data)
                                    print(f"  采集到 {len(data)} 条 (GBK编码)")
                            except:
                                print(f"  ⚠ 所有编码尝试失败")
                    else:
                        print(f"  ⚠ 未找到JSON文件")

            except subprocess.TimeoutExpired:
                print(f"  ❌ 采集超时")
            except Exception as e:
                print(f"  ❌ 采集失败: {e}")

        # 如果没有采集到数据，尝试读取现有的JSON文件
        if len(all_data) == 0:
            print(f"  尝试读取现有数据...")
            json_files = list(self.json_path.glob("search_contents_*.json"))
            if json_files:
                latest_json = max(json_files, key=lambda p: p.stat().st_mtime)
                try:
                    with open(latest_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_data.extend(data)
                        print(f"  读取现有数据 {len(data)} 条")
                except Exception as e:
                    print(f"  ⚠ 读取现有数据失败: {e}")

        print(f"✅ 总共采集到 {len(all_data)} 条")

        # 去重（按note_id）
        unique_data = {}
        for note in all_data:
            note_id = note.get('note_id')
            if note_id and note_id not in unique_data:
                unique_data[note_id] = note

        unique_list = list(unique_data.values())
        print(f"✅ 去重后 {len(unique_list)} 条")

        return unique_list

#!/usr/bin/env python3
"""
小红书数据采集脚本
用于采集指定关键词的笔记和评论数据
"""

import os
import sys
import json
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path

# MediaCrawler 路径
MEDIACRAWLER_HOME = os.path.expanduser("~/MediaCrawler")
MEDIACRAWLER_VENV = os.path.join(MEDIACRAWLER_HOME, ".venv")
MEDIACRAWLER_PYTHON = os.path.join(MEDIACRAWLER_VENV, "bin", "python3")
MEDIACRAWLER_SCRIPT = os.path.join(MEDIACRAWLER_HOME, "main.py")


class XHSCollector:
    """小红书数据采集器"""

    def __init__(self, config_path=None):
        """
        初始化采集器

        Args:
            config_path: 配置文件路径
        """
        SKILL_DIR = Path(__file__).parent.parent
        if config_path is None:
            config_path = SKILL_DIR / "config" / "brands.json"

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.keywords = self.config.get('keywords', [])
        self.competitors = self.config.get('competitors', [])
        self.max_notes = self.config.get('max_notes', 10)

        # 检查 MediaCrawler 环境
        self.mediacrawler_available = self._check_mediacrawler()

    def _check_mediacrawler(self):
        """检查 MediaCrawler 是否可用"""
        if not os.path.exists(MEDIACRAWLER_HOME):
            return False
        if not os.path.exists(MEDIACRAWLER_VENV):
            return False
        if not os.path.exists(MEDIACRAWLER_SCRIPT):
            return False
        return True

    async def collect_notes(self, keyword):
        """
        采集指定关键词的笔记

        Args:
            keyword: 搜索关键词

        Returns:
            list: 笔记列表
        """
        if not self.mediacrawler_available:
            print(f"❌ MediaCrawler 不可用，无法采集数据")
            print(f"   请检查 MediaCrawler 安装路径: {MEDIACRAWLER_HOME}")
            raise RuntimeError("MediaCrawler 不可用")

        try:
            # 使用 MediaCrawler 采集数据
            print(f"🔍 正在采集关键词: {keyword}")

            # 修改配置文件
            self._modify_mediacrawler_config(keyword)

            # 设置环境变量
            env = os.environ.copy()
            env['PYTHONPATH'] = MEDIACRAWLER_HOME

            # 构建命令（不带参数，使用配置文件）
            cmd = [MEDIACRAWLER_PYTHON, MEDIACRAWLER_SCRIPT]

            # 运行采集
            result = subprocess.run(
                cmd,
                cwd=MEDIACRAWLER_HOME,
                capture_output=True,
                timeout=600  # 10分钟超时
            )

            if result.returncode == 0:
                print(f"✅ 采集完成: {keyword}")
                # 解析采集的数据文件
                return self._parse_mediacrawler_data(keyword)
            else:
                print(f"❌ 采集失败:")
                print(f"   返回码: {result.returncode}")
                # 尝试解码错误信息，忽略编码错误
                try:
                    stderr = result.stderr.decode('utf-8', errors='ignore')
                    print(f"   错误: {stderr[:500]}")
                except:
                    print(f"   错误: (无法解码)")
                raise RuntimeError(f"MediaCrawler 采集失败")

        except subprocess.TimeoutExpired:
            print(f"❌ 采集超时（10分钟）")
            raise RuntimeError("MediaCrawler 采集超时")
        except Exception as e:
            print(f"❌ 采集出错: {e}")
            raise

    def _modify_mediacrawler_config(self, keyword):
        """修改 MediaCrawler 配置文件"""
        import re
        import shutil

        config_file = Path(MEDIACRAWLER_HOME) / "config" / "base_config.py"
        backup_file = Path(MEDIACRAWLER_HOME) / "config" / "base_config.py.backup_competitor_alert"

        if not config_file.exists():
            raise FileNotFoundError(f"MediaCrawler 配置文件不存在: {config_file}")

        # 备份配置文件（如果还没有备份）
        if not backup_file.exists():
            shutil.copy2(config_file, backup_file)
            print(f"✓ 已备份配置文件")

        # 读取配置
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 修改关键词
        content_new = re.sub(
            r'KEYWORDS = ".*?"',
            f'KEYWORDS = "{keyword}"',
            content
        )

        # 设置平台为小红书
        content_new = re.sub(
            r'PLATFORM = ".*?"',
            'PLATFORM = "xhs"',
            content_new
        )

        # 设置爬取数量
        content_new = re.sub(
            r'CRAWLER_MAX_NOTES_COUNT = \d+',
            f'CRAWLER_MAX_NOTES_COUNT = {self.max_notes}',
            content_new
        )

        # 确保开启评论爬取
        content_new = re.sub(
            r'ENABLE_GET_COMMENTS = (True|False)',
            'ENABLE_GET_COMMENTS = True',
            content_new
        )

        # 设置数据保存类型为 json
        content_new = re.sub(
            r'SAVE_DATA_OPTION = ".*?"',
            'SAVE_DATA_OPTION = "json"',
            content_new
        )

        # 写回配置
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(content_new)

        print(f"✓ MediaCrawler 配置已更新: 关键词={keyword}, 数量={self.max_notes}")

    def _parse_mediacrawler_data(self, keyword):
        """解析 MediaCrawler 采集的数据"""
        data_dir = Path(MEDIACRAWLER_HOME) / "data" / "xhs" / "json"

        if not data_dir.exists():
            print(f"❌ MediaCrawler 数据目录不存在: {data_dir}")
            raise FileNotFoundError(f"数据目录不存在: {data_dir}")

        # 找到最新的笔记和评论数据文件
        notes_files = list(data_dir.glob("search_contents_*.json"))
        comments_files = list(data_dir.glob("search_comments_*.json"))

        if not notes_files:
            print(f"❌ 未找到笔记数据文件")
            raise FileNotFoundError("未找到采集数据文件")

        latest_notes_file = max(notes_files, key=os.path.getmtime)
        print(f"📂 读取笔记文件: {latest_notes_file}")

        try:
            with open(latest_notes_file, 'r', encoding='utf-8') as f:
                notes_data = json.load(f)

            # 读取评论数据（如果存在）
            comments_data = {}
            if comments_files:
                latest_comments_file = max(comments_files, key=os.path.getmtime)
                print(f"📂 读取评论文件: {latest_comments_file}")
                with open(latest_comments_file, 'r', encoding='utf-8') as f:
                    comments = json.load(f)
                    # 按 note_id 索引评论
                    for comment in comments:
                        note_id = comment.get('note_id')
                        if note_id:
                            if note_id not in comments_data:
                                comments_data[note_id] = []
                            comments_data[note_id].append(comment)
                print(f"✓ 加载了 {len(comments)} 条评论")

            # 标准化笔记格式
            notes = []
            for item in notes_data:
                note = self._normalize_note(item)
                # 将评论附加到笔记上
                note_id = note.get('note_id')
                if note_id in comments_data:
                    note['comments'] = comments_data[note_id]
                else:
                    note['comments'] = []
                notes.append(note)

            return notes

        except Exception as e:
            print(f"❌ 解析数据失败: {e}")
            raise

    def _normalize_note(self, item):
        """将 MediaCrawler 数据标准化为统一格式"""
        # MediaCrawler 字段映射
        return {
            'title': item.get('title', item.get('note_card', {}).get('title', '')),
            'url': item.get('url', item.get('note_card', {}).get('url', '')),
            'author': item.get('author', item.get('user', {}).get('nickname', '')),
            'likes': item.get('liked_count', item.get('interact_info', {}).get('liked_count', 0)),
            'comments': item.get('comment_count', item.get('interact_info', {}).get('comment_count', 0)),
            'content': item.get('desc', item.get('note_card', {}).get('desc', '')),
            'note_id': item.get('note_id', item.get('note_card', {}).get('note_id', '')),
            'raw_data': item  # 保留原始数据用于提取评论
        }

    async def collect_comments(self, note_url):
        """
        采集指定笔记的评论

        Args:
            note_url: 笔记链接

        Returns:
            list: 评论列表
        """
        # MediaCrawler 会同时采集评论，数据已在笔记数据中
        # 从已采集的笔记数据中提取评论
        return []

    def filter_competitor_mentions(self, comments):
        """
        过滤出包含竞品关键词的评论

        Args:
            comments: 评论列表

        Returns:
            list: 包含竞品的评论
        """
        results = []
        for comment in comments:
            content = comment.get('content', '')
            for brand in self.competitors:
                if brand in content:
                    results.append({
                        **comment,
                        'detected_brand': brand
                    })
                    break
        return results

    async def scan(self):
        """
        执行完整扫描流程

        Returns:
            dict: 扫描结果
        """
        all_results = {
            'scan_time': datetime.now().isoformat(),
            'keywords_searched': self.keywords,
            'competitors_found': {},
            'total_notes_scanned': 0,
            'total_comments_scanned': 0,
            'competitor_mentions': []
        }

        for keyword in self.keywords:
            print(f"🔍 搜索关键词: {keyword}")

            # 采集笔记（包含评论数据）
            notes = await self.collect_notes(keyword)
            all_results['total_notes_scanned'] += len(notes)

            for note in notes:
                note_url = note.get('url', '')
                note_title = note.get('title', '')

                # 从原始数据中提取评论
                comments = self._extract_comments_from_note(note)
                all_results['total_comments_scanned'] += len(comments)

                # 检测竞品提及
                competitor_comments = self.filter_competitor_mentions(comments)

                if competitor_comments:
                    for comment in competitor_comments:
                        brand = comment['detected_brand']
                        if brand not in all_results['competitors_found']:
                            all_results['competitors_found'][brand] = 0
                        all_results['competitors_found'][brand] += 1

                        all_results['competitor_mentions'].append({
                            'keyword': keyword,
                            'note_title': note_title,
                            'note_url': note_url,
                            'brand': brand,
                            'comment': comment
                        })

        return all_results

    def _extract_comments_from_note(self, note):
        """从笔记数据中提取评论"""
        comments = []

        # 优先使用已加载的评论数据
        if 'comments' in note and note['comments']:
            return [self._normalize_comment(c) for c in note['comments'] if self._normalize_comment(c)]

        # 否则从原始数据中提取
        raw_data = note.get('raw_data', {})

        # MediaCrawler 可能有不同的字段存储评论
        # 1. 直接的 comments 字段
        if 'comments' in raw_data:
            comments.extend(raw_data['comments'])

        # 2. comment_list 字段
        if 'comment_list' in raw_data:
            comments.extend(raw_data['comment_list'])

        # 3. 嵌套的评论数据
        if 'comment' in raw_data:
            comment_data = raw_data['comment']
            if isinstance(comment_data, list):
                comments.extend(comment_data)
            elif isinstance(comment_data, dict) and 'comments' in comment_data:
                comments.extend(comment_data['comments'])

        # 标准化评论格式
        normalized_comments = []
        for comment in comments:
            normalized = self._normalize_comment(comment)
            if normalized:
                normalized_comments.append(normalized)

        return normalized_comments

    def _normalize_comment(self, comment):
        """标准化评论格式"""
        if not isinstance(comment, dict):
            return None

        # 提取评论内容
        content = ''
        if 'content' in comment:
            content = comment['content']
        elif 'text' in comment:
            content = comment['text']
        elif 'comment_content' in comment:
            content = comment['comment_content']
        elif 'desc' in comment:
            content = comment['desc']

        # 提取用户信息
        user = '匿名用户'
        if 'user' in comment:
            user_data = comment['user']
            if isinstance(user_data, dict):
                user = user_data.get('nickname', user_data.get('username', '匿名用户'))
            else:
                user = str(user_data)
        elif 'nickname' in comment:
            user = comment['nickname']
        elif 'author' in comment:
            user = comment['author']

        # 提取时间
        time = '未知时间'
        if 'time' in comment:
            time = comment['time']
        elif 'create_time' in comment:
            time = comment['create_time']
        elif 'timestamp' in comment:
            time = comment['timestamp']

        return {
            'content': content,
            'user': user,
            'time': time,
            'raw_data': comment
        }


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='小红书竞品数据采集')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--keyword', help='搜索关键词（覆盖配置）')

    args = parser.parse_args()

    collector = XHSCollector(args.config)

    if args.keyword:
        collector.keywords = [args.keyword]

    results = await collector.scan()

    print(json.dumps(results, ensure_ascii=False, indent=2))

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 结果已保存到: {args.output}")


if __name__ == '__main__':
    asyncio.run(main())

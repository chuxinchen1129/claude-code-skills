#!/usr/bin/env python3
"""
MediaCrawler 采集结果导入器

功能：
1. 扫描 MediaCrawler 采集结果目录
2. 读取并解析 JSON 文件
3. 判断笔记类型（视频/图文）
4. 调用 MaterialOrganizer 组织材料
5. 更新索引文件

作者：大秘书系统
版本：v1.0
创建时间：2026-02-12
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MediaCrawlerImporter:
    """MediaCrawler 采集结果导入器 - 将采集结果组织到对标参考"""

    # MediaCrawler 数据目录
    MEDIACRAWLER_BASE = Path.home() / "MediaCrawler" / "data"

    # 平台数据目录
    PLATFORM_DIRS = {
        'xhs': MEDIACRAWLER_BASE / "xhs" / "json",
        'douyin': MEDIACRAWLER_BASE / "douyin" / "json",
        'weibo': MEDIACRAWLER_BASE / "weibo" / "json",
        'bilibili': MEDIACRAWLER_BASE / "bilibili" / "json"
    }

    def __init__(self, material_base_path=None, platform='xhs'):
        """
        初始化导入器

        Args:
            material_base_path: 材料存储基础路径（对标参考）
            platform: 平台类型（xhs, douyin, weibo等）
        """
        # 材料存储路径
        if material_base_path is None:
            material_base_path = Path.home() / "Desktop" / "DaMiShuSystem-main-backup" / "工作空间" / "对标参考"
        self.material_base = Path(material_base_path)

        # 导入 MaterialOrganizer
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from material_organizer import MaterialOrganizer

        self.organizer = MaterialOrganizer(self.material_base)

        # 平台数据目录
        self.platform = platform
        self.source_dir = self.PLATFORM_DIRS.get(platform, self.PLATFORM_DIRS['xhs'])

        if not self.source_dir.exists():
            logger.warning(f"MediaCrawler {platform} 数据目录不存在: {self.source_dir}")

        logger.info(f"MediaCrawlerImporter initialized: platform={platform}, source={self.source_dir}")

    def scan_collections(self, days=7):
        """
        扫描最近 N 天的采集结果

        Args:
            days: 天数，0 表示扫描所有

        Returns:
            list: JSON 文件列表（按修改时间排序，最新的在前）
        """
        if not self.source_dir.exists():
            logger.warning(f"数据目录不存在: {self.source_dir}")
            return []

        now = datetime.now()
        cutoff_time = now - timedelta(days=days) if days > 0 else None

        recent_files = []
        for json_file in self.source_dir.glob("*.json"):
            try:
                mtime = datetime.fromtimestamp(json_file.stat().st_mtime)

                # 过滤
                if cutoff_time and mtime < cutoff_time:
                    continue

                recent_files.append({
                    'path': json_file,
                    'mtime': mtime,
                    'size': json_file.stat().st_size
                })
            except Exception as e:
                logger.warning(f"无法读取文件 {json_file.name}: {e}")

        # 按修改时间排序（最新的在前）
        recent_files.sort(key=lambda x: x['mtime'], reverse=True)
        logger.info(f"扫描到 {len(recent_files)} 个采集文件（{days}天内）")

        return recent_files

    def detect_note_type(self, note_data):
        """
        检测笔记类型（视频/图文）

        Args:
            note_data: 笔记数据（字典）

        Returns:
            str: 'video' 或 'image'
        """
        # 检测视频字段
        video_fields = ['video_url', 'video_local_path', 'video_stream', 'has_video']

        for field in video_fields:
            if note_data.get(field):
                return 'video'

        # 默认为图文
        return 'image'

    def normalize_note_data(self, note_data, json_file):
        """
        标准化笔记数据格式，适配 MaterialOrganizer

        Args:
            note_data: 原始笔记数据
            json_file: 来源JSON文件路径

        Returns:
            dict: 标准化后的笔记数据
        """
        # 基础字段映射
        note_id = note_data.get('note_id', note_data.get('id', note_data.get('note_id', '')))[:8]
        title = note_data.get('title', note_data.get('note_title', '未命名'))

        # 处理时间戳
        publish_date = None
        for date_field in ['create_time', 'note_time', 'published_at', 'date']:
            if note_data.get(date_field):
                try:
                    ts = note_data[date_field]
                    # 处理毫秒时间戳
                    if isinstance(ts, (int, float)) and ts > 10000000000:
                        # 可能是毫秒时间戳
                        if ts > 1000000000000:  # 1970年以后的毫秒
                            publish_date = datetime.fromtimestamp(ts / 1000)
                        else:
                            publish_date = datetime.fromtimestamp(ts)
                    else:
                        # 已经是 datetime 对象
                        publish_date = ts
                    break
                except Exception:
                    continue

        # 标准化元数据
        normalized = {
            'note_id': note_id,
            'title': title,
            'desc': note_data.get('desc', note_data.get('note_desc', note_data.get('text', ''))),
            'author': note_data.get('nickname', note_data.get('author', note_data.get('user', {}).get('nickname', ''))),
            'fans': note_data.get('liked_count', note_data.get('user', {}).get('follower_count', 0)),
            'publish_date': publish_date,
            'likes': note_data.get('liked_count', note_data.get('interact_info', {}).get('liked_count', 0)),
            'collects': note_data.get('collected_count', note_data.get('interact_info', {}).get('collected_count', 0)),
            'comments': note_data.get('comment_count', note_data.get('interact_info', {}).get('comment_count', 0)),
            'url': note_data.get('note_url', note_data.get('url', '')),
            'original_url': note_data.get('note_url', note_data.get('url', ''))
        }

        return normalized

    def import_file(self, json_file):
        """
        导入单个 JSON 文件

        Args:
            json_file: JSON 文件路径

        Returns:
            dict: 导入结果统计
        """
        logger.info(f"导入文件: {json_file.name}")

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 处理不同的数据结构
            if isinstance(data, list):
                notes = data
            elif isinstance(data, dict) and 'data' in data:
                notes = data['data']
            else:
                notes = []

            stats = {
                'total': len(notes),
                'video': 0,
                'image': 0,
                'failed': 0,
                'imported': 0
            }

            for note in notes:
                try:
                    # 标准化数据
                    normalized = self.normalize_note_data(note, json_file)

                    # 检测笔记类型
                    note_type = self.detect_note_type(note)

                    # 根据类型调用 MaterialOrganizer
                    if note_type == 'video':
                        self.organizer.organize_xhs_video(normalized)
                        stats['video'] += 1
                    else:
                        self.organizer.organize_xhs_image(normalized)
                        stats['image'] += 1

                    stats['imported'] += 1

                except Exception as e:
                    logger.error(f"导入笔记失败: {str(e)}")
                    stats['failed'] += 1

            logger.info(f"导入完成: {stats['imported']}/{stats['total']} 成功, {stats['failed']} 失败")

            return stats

        except Exception as e:
            logger.error(f"读取文件失败 {json_file.name}: {e}")
            return {
                'total': 0,
                'video': 0,
                'image': 0,
                'failed': 1,
                'imported': 0
            }

    def import_collections(self, days=7, limit=None):
        """
        导入多个采集结果文件

        Args:
            days: 最近 N 天的采集结果
            limit: 最多导入的文件数量

        Returns:
            dict: 总体导入统计
        """
        # 扫描采集文件
        files = self.scan_collections(days)

        if limit and len(files) > limit:
            files = files[:limit]

        total_stats = {
            'total': 0,
            'video': 0,
            'image': 0,
            'failed': 0,
            'imported': 0,
            'files': len(files)
        }

        for file_info in files:
            stats = self.import_file(file_info['path'])
            for key in ['total', 'video', 'image', 'failed', 'imported']:
                total_stats[key] += stats[key]

        # 更新索引
        self.organizer.update_index()

        logger.info(f"批量导入完成: {total_stats['imported']} 条笔记, {total_stats['video']} 视频, {total_stats['image']} 图文")

        return total_stats

    def get_import_summary(self, days=7):
        """
        获取导入摘要信息

        Args:
            days: 天数

        Returns:
            dict: 摘要信息
        """
        files = self.scan_collections(days)

        if not files:
            return {
                'available': 0,
                'latest_date': None,
                'oldest_date': None,
                'total_size_mb': 0
            }

        dates = [f['mtime'] for f in files]
        total_size = sum(f['size'] for f in files) / (1024 * 1024)

        return {
            'available': len(files),
            'latest_date': max(dates).isoformat() if dates else None,
            'oldest_date': min(dates).isoformat() if dates else None,
            'total_size_mb': round(total_size, 2)
        }


def create_importer(material_base_path=None, platform='xhs'):
    """创建 MediaCrawlerImporter 实例"""
    return MediaCrawlerImporter(material_base_path, platform)


if __name__ == '__main__':
    import sys

    # 测试导入器
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python media_crawler_importer.py scan [--days N]")
        print("  python media_crawler_importer.py import [--days N] [--limit N]")
        print()
        print("Examples:")
        print("  python media_crawler_importer.py scan --days 7")
        print("  python media_crawler_importer.py import --days 7 --limit 5")
        sys.exit(1)

    command = sys.argv[1]
    importer = create_importer()

    if command == 'scan':
        # 扫描模式
        days = 7
        if '--days' in sys.argv:
            idx = sys.argv.index('--days')
            if idx + 1 < len(sys.argv):
                days = int(sys.argv[idx + 1])

        summary = importer.get_import_summary(days)
        print(f"📊 扫描摘要 ({days}天内):")
        print(f"  可用文件: {summary['available']}")
        print(f"  最新采集: {summary['latest_date']}")
        print(f"  最早采集: {summary['oldest_date']}")
        print(f"  总大小: {summary['total_size_mb']} MB")

    elif command == 'import':
        # 导入模式
        days = 7
        limit = None

        if '--days' in sys.argv:
            idx = sys.argv.index('--days')
            if idx + 1 < len(sys.argv):
                days = int(sys.argv[idx + 1])

        if '--limit' in sys.argv:
            idx = sys.argv.index('--limit')
            if idx + 1 < len(sys.argv):
                limit = int(sys.argv[idx + 1])

        stats = importer.import_collections(days, limit)
        print(f"✅ 导入完成:")
        print(f"  扫描文件: {stats['files']}")
        print(f"  导入成功: {stats['imported']}/{stats['total']}")
        print(f"  视频笔记: {stats['video']}")
        print(f"  图文笔记: {stats['image']}")
        print(f"  导入失败: {stats['failed']}")

    else:
        print(f"未知命令: {command}")
        sys.exit(1)

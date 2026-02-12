#!/usr/bin/env python3
"""
材料组织器

功能：
1. 按类型组织材料（小红书视频/图文/微信文章）
2. 生成元数据JSON文件
3. 自动生成可搜索的index.md索引
4. 管理文件命名规范

作者：大秘书系统
版本：v1.0
创建时间：2026-02-12
"""

import os
import re
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MaterialOrganizer:
    """材料组织器 - 将采集的内容按类型组织到对标参考文件夹"""

    # 文件名最大长度（避免过长）
    MAX_FILENAME_LENGTH = 100

    def __init__(self, material_base_path=None):
        """
        初始化材料组织器

        Args:
            material_base_path: 材料存储基础路径
        """
        if material_base_path is None:
            material_base_path = Path.home() / "Desktop" / "DaMiShuSystem-main-backup" / "工作空间" / "对标参考"
        self.material_base = Path(material_base_path)

        # 确保目录存在
        self.material_base.mkdir(parents=True, exist_ok=True)

        # 子目录
        self.dirs = {
            'xhs_video': self.material_base / "小红书视频",
            'xhs_image': self.material_base / "小红书图文",
            'wechat': self.material_base / "微信文章"
        }
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # 索引文件
        self.index_file = self.material_base / "index.md"

        logger.info(f"MaterialOrganizer initialized: {self.material_base}")

    def sanitize_filename(self, filename):
        """
        清理文件名，移除非法字符

        Args:
            filename: 原始文件名

        Returns:
            str: 清理后的文件名
        """
        # 移除或替换非法字符
        illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        cleaned = filename
        for char in illegal_chars:
            cleaned = cleaned.replace(char, '_')

        # 限制长度
        if len(cleaned) > self.MAX_FILENAME_LENGTH:
            cleaned = cleaned[:self.MAX_FILENAME_LENGTH]

        return cleaned

    def generate_folder_name(self, metadata):
        """
        根据元数据生成文件夹名

        Args:
            metadata: 笔记/文章元数据

        Returns:
            str: 文件夹名 (格式: YYYY-MM-DD_序号_标题)
        """
        # 获取时间或使用当前时间
        publish_date = metadata.get('publish_date') or metadata.get('date')
        if publish_date:
            try:
                if isinstance(publish_date, (int, float)):
                    # 时间戳格式
                    dt = datetime.fromtimestamp(publish_date / 1000)
                else:
                    # ISO格式或其他
                    dt = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            except:
                dt = datetime.now()
        else:
            dt = datetime.now()

        date_str = dt.strftime('%Y-%m-%d')

        # 获取标题
        title = metadata.get('title', metadata.get('desc', '未命名'))[:30]
        title_clean = self.sanitize_filename(title)

        # 生成序号（查找现有文件夹）
        content_type = metadata.get('type', 'xhs_video')
        dir_key = 'xhs_video' if content_type == 'xhs_video' else 'xhs_image' if content_type == 'xhs_image' else 'wechat'

        # 查找该类型下已有的文件夹数量
        existing_count = len(list(self.dirs[dir_key].glob(f"{date_str}_*")))
        seq_num = existing_count + 1

        return f"{date_str}_{seq_num:04d}_{title_clean}"

    def organize_xhs_video(self, note_data, media_files=None):
        """
        组织小红书视频笔记材料

        Args:
            note_data: 笔记元数据 {
                note_id, title, desc, author, fans,
                publish_date, likes, collects, comments, ...
            }
            media_files: 媒体文件 {
                cover: Path,  # 封面图路径
                video: Path,  # 视频文件路径
                transcript: Path  # 转录文字路径
            }

        Returns:
            dict: 组织结果
        """
        note_id = note_data.get('note_id', note_data.get('id', ''))[:8]

        # 准备元数据
        metadata = {
            'type': 'xhs_video',
            'note_id': note_id,
            'title': note_data.get('title', ''),
            'desc': note_data.get('desc', ''),
            'author': note_data.get('author', ''),
            'fans': note_data.get('fans', 0),
            'publish_date': note_data.get('publish_date', note_data.get('date', '')),
            'likes': note_data.get('liked_count', note_data.get('likes', 0)),
            'collects': note_data.get('collected_count', note_data.get('collects', 0)),
            'comments': note_data.get('comment_count', note_data.get('comments', 0)),
            'url': note_data.get('url', ''),
            'original_url': note_data.get('original_url', '')
        }

        # 生成文件夹名
        folder_name = self.generate_folder_name(metadata)
        folder_path = self.dirs['xhs_video'] / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Organizing XHS video: {folder_name}")

        # 保存元数据
        metadata_file = folder_path / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # 复制媒体文件
        saved_files = {'metadata': str(metadata_file)}

        if media_files:
            if media_files.get('cover'):
                cover_dest = folder_path / "cover.jpg"
                shutil.copy2(media_files['cover'], cover_dest)
                saved_files['cover'] = str(cover_dest)

            if media_files.get('video'):
                video_dest = folder_path / "video.mp4"
                shutil.copy2(media_files['video'], video_dest)
                saved_files['video'] = str(video_dest)

            if media_files.get('transcript'):
                transcript_dest = folder_path / "transcript.txt"
                shutil.copy2(media_files['transcript'], transcript_dest)
                saved_files['transcript'] = str(transcript_dest)

        # 保存正文
        if metadata.get('desc'):
            desc_file = folder_path / "content.md"
            with open(desc_file, 'w', encoding='utf-8') as f:
                f.write(f"# {metadata['title']}\n\n")
                f.write(metadata['desc'])
            saved_files['content'] = str(desc_file)

        logger.info(f"XHS video organized: {folder_path}")
        return {
            'success': True,
            'folder_path': str(folder_path),
            'folder_name': folder_name,
            'saved_files': saved_files,
            'metadata': metadata
        }

    def organize_xhs_image(self, note_data, media_files=None):
        """
        组织小红书图文笔记材料

        Args:
            note_data: 笔记元数据
            media_files: 媒体文件 {
                cover: Path,  # 封面图路径
                images: List[Path]  # 多张图片路径
            }

        Returns:
            dict: 组织结果
        """
        note_id = note_data.get('note_id', note_data.get('id', ''))[:8]

        # 准备元数据
        metadata = {
            'type': 'xhs_image',
            'note_id': note_id,
            'title': note_data.get('title', ''),
            'desc': note_data.get('desc', ''),
            'author': note_data.get('author', ''),
            'fans': note_data.get('fans', 0),
            'publish_date': note_data.get('publish_date', note_data.get('date', '')),
            'likes': note_data.get('liked_count', note_data.get('likes', 0)),
            'collects': note_data.get('collected_count', note_data.get('collects', 0)),
            'comments': note_data.get('comment_count', note_data.get('comments', 0)),
            'url': note_data.get('url', ''),
            'original_url': note_data.get('original_url', '')
        }

        # 生成文件夹名
        folder_name = self.generate_folder_name(metadata)
        folder_path = self.dirs['xhs_image'] / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Organizing XHS image: {folder_name}")

        # 保存元数据
        metadata_file = folder_path / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        saved_files = {'metadata': str(metadata_file)}

        # 复制媒体文件
        if media_files:
            if media_files.get('cover'):
                cover_dest = folder_path / "cover.jpg"
                shutil.copy2(media_files['cover'], cover_dest)
                saved_files['cover'] = str(cover_dest)

            # 多张图片
            if media_files.get('images'):
                images_dir = folder_path / "images"
                images_dir.mkdir(exist_ok=True)
                for i, img_path in enumerate(media_files['images'], 1):
                    img_ext = img_path.suffix
                    img_dest = images_dir / f"image_{i:03d}{img_ext}"
                    shutil.copy2(img_path, img_dest)
                saved_files['images'] = str(images_dir)

        # 保存正文
        if metadata.get('desc'):
            desc_file = folder_path / "content.md"
            with open(desc_file, 'w', encoding='utf-8') as f:
                f.write(f"# {metadata['title']}\n\n")
                f.write(metadata['desc'])
            saved_files['content'] = str(desc_file)

        logger.info(f"XHS image organized: {folder_path}")
        return {
            'success': True,
            'folder_path': str(folder_path),
            'folder_name': folder_name,
            'saved_files': saved_files,
            'metadata': metadata
        }

    def organize_wechat_article(self, article_data, markdown_content=None):
        """
        组织微信文章材料

        Args:
            article_data: 文章元数据 {
                title, author, publish_date, url, ...
            }
            markdown_content: Markdown内容

        Returns:
            dict: 组织结果
        """
        # 准备元数据
        metadata = {
            'type': 'wechat_article',
            'title': article_data.get('title', ''),
            'author': article_data.get('author', ''),
            'publish_date': article_data.get('date', ''),
            'url': article_data.get('url', ''),
            'original_url': article_data.get('original_url', '')
        }

        # 生成文件夹名
        folder_name = self.generate_folder_name(metadata)
        folder_path = self.dirs['wechat'] / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Organizing WeChat article: {folder_name}")

        # 保存元数据
        metadata_file = folder_path / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        saved_files = {'metadata': str(metadata_file)}

        # 保存Markdown文章
        if markdown_content:
            article_file = folder_path / "article.md"
            with open(article_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            saved_files['article'] = str(article_file)

        logger.info(f"WeChat article organized: {folder_path}")
        return {
            'success': True,
            'folder_path': str(folder_path),
            'folder_name': folder_name,
            'saved_files': saved_files,
            'metadata': metadata
        }

    def update_index(self):
        """
        更新或创建索引文件 index.md

        Returns:
            dict: 索引更新结果
        """
        # 统计各类型材料
        index_data = {
            'xhs_video': [],
            'xhs_image': [],
            'wechat': []
        }

        # 扫描小红书视频
        for folder in self.dirs['xhs_video'].glob('*_*'):
            if folder.is_dir():
                metadata_file = folder / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        index_data['xhs_video'].append({
                            'folder': folder.name,
                            'title': metadata.get('title', ''),
                            'date': folder.name[:10],  # YYYY-MM-DD
                            'likes': metadata.get('likes', 0)
                        })
                    except:
                        pass

        # 扫描小红书图文
        for folder in self.dirs['xhs_image'].glob('*_*'):
            if folder.is_dir():
                metadata_file = folder / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        index_data['xhs_image'].append({
                            'folder': folder.name,
                            'title': metadata.get('title', ''),
                            'date': folder.name[:10],
                            'likes': metadata.get('likes', 0)
                        })
                    except:
                        pass

        # 扫描微信文章
        for folder in self.dirs['wechat'].glob('*_*'):
            if folder.is_dir():
                metadata_file = folder / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        index_data['wechat'].append({
                            'folder': folder.name,
                            'title': metadata.get('title', ''),
                            'date': folder.name[:10]
                        })
                    except:
                        pass

        # 按日期排序（最新的在前）
        for key in index_data:
            index_data[key].sort(key=lambda x: x['date'], reverse=True)

        # 生成Markdown索引
        index_content = f"""# 对标参考材料索引

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 统计

| 类型 | 数量 |
|------|------|
| 小红书视频 | {len(index_data['xhs_video'])} |
| 小红书图文 | {len(index_data['xhs_image'])} |
| 微信文章 | {len(index_data['wechat'])} |
| **总计** | {len(index_data['xhs_video']) + len(index_data['xhs_image']) + len(index_data['wechat'])} |

---

## 小红书视频 ({len(index_data['xhs_video'])}篇)

"""

        if index_data['xhs_video']:
            for item in index_data['xhs_video'][:20]:  # 只显示前20个
                index_content += f"""
### [{item['date']}] {item['title']}
- **文件夹**: `{item['folder']}`
- **点赞**: {item['likes']}
"""
            if len(index_data['xhs_video']) > 20:
                index_content += f"\n... 还有 {len(index_data['xhs_video']) - 20} 篇视频笔记\n"
        else:
            index_content += "\n暂无视频笔记\n"

        index_content += "\n---\n\n## 小红书图文 ({}篇)\n\n".format(len(index_data['xhs_image']))

        if index_data['xhs_image']:
            for item in index_data['xhs_image'][:20]:
                index_content += f"""
### [{item['date']}] {item['title']}
- **文件夹**: `{item['folder']}`
- **点赞**: {item['likes']}
"""
            if len(index_data['xhs_image']) > 20:
                index_content += f"\n... 还有 {len(index_data['xhs_image']) - 20} 篇图文笔记\n"
        else:
            index_content += "\n暂无图文笔记\n"

        index_content += "\n---\n\n## 微信文章 ({}篇)\n\n".format(len(index_data['wechat']))

        if index_data['wechat']:
            for item in index_data['wechat'][:20]:
                index_content += f"""
### [{item['date']}] {item['title']}
- **文件夹**: `{item['folder']}`
"""
            if len(index_data['wechat']) > 20:
                index_content += f"\n... 还有 {len(index_data['wechat']) - 20} 篇文章\n"
        else:
            index_content += "\n暂无微信文章\n"

        index_content += f"""
---

**说明**:
- 每个材料按 `YYYY-MM-DD_序号_标题/` 格式组织
- 包含完整元数据 `metadata.json`
- 视频笔记包含：封面、视频、转录文字、正文
- 图文笔记包含：封面、图片、正文
- 微信文章包含：Markdown文章、元数据

---

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # 写入索引文件
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)

        logger.info(f"Index updated: {self.index_file}")

        return {
            'success': True,
            'index_file': str(self.index_file),
            'stats': {
                'xhs_video': len(index_data['xhs_video']),
                'xhs_image': len(index_data['xhs_image']),
                'wechat': len(index_data['wechat']),
                'total': len(index_data['xhs_video']) + len(index_data['xhs_image']) + len(index_data['wechat'])
            }
        }


# 便捷函数
def create_organizer(material_base_path=None):
    """创建MaterialOrganizer实例"""
    return MaterialOrganizer(material_base_path)


if __name__ == '__main__':
    import sys

    # 测试代码
    organizer = MaterialOrganizer()

    print("Testing MaterialOrganizer")
    print("=" * 60)

    # 测试更新索引
    result = organizer.update_index()
    print(f"Index update result: {result}")

#!/usr/bin/env python3
"""
小红书媒体文件后处理脚本

功能：
1. 下载封面图
2. 下载视频文件（视频笔记）
3. 转录视频内容（使用 Whisper）
4. 生成结构化输出

使用：
    python3 process_xhs_media.py --input ~/MediaCrawler/data/xhs/json/search_contents_*.json

作者：大秘书系统
版本：v1.0
创建时间：2026-02-11
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import subprocess
import requests

class XHSMediaProcessor:
    """小红书媒体文件处理器"""

    def __init__(self, input_dir, output_dir=None):
        """
        初始化处理器

        Args:
            input_dir: MediaCrawler 输出目录
            output_dir: 处理后文件保存目录
        """
        self.input_dir = Path(input_dir)
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = self.input_dir.parent / "processed"

        # 创建输出目录
        self.media_dir = self.output_dir / "media"
        self.media_dir.mkdir(parents=True, exist_ok=True)

        # 下载会话
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15',
            'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

    def load_notes(self):
        """加载笔记数据"""
        json_files = list(self.input_dir.glob("search_contents_*.json"))

        if not json_files:
            print(f"❌ 未找到笔记数据文件: {self.input_dir}")
            return []

        # 使用最新的文件
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        print(f"📂 读取文件: {latest_file.name}")

        with open(latest_file, 'r', encoding='utf-8') as f:
            notes = json.load(f)

        print(f"✓ 加载了 {len(notes)} 条笔记")
        return notes

    def download_cover(self, note, index):
        """
        下载封面图

        Args:
            note: 笔记数据
            index: 笔记序号

        Returns:
            str: 保存的文件路径
        """
        cover_url = note.get('image', '')
        if not cover_url:
            return None

        try:
            print(f"  [{index}] 下载封面...")
            response = requests.get(cover_url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                # 确定文件扩展名
                content_type = response.headers.get('content-type', '')
                if 'webp' in content_type:
                    ext = '.webp'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'jpg' in content_type or 'jpeg' in content_type:
                    ext = '.jpg'
                else:
                    ext = '.jpg'

                # 保存文件
                filename = f"{index:04d}_cover{ext}"
                filepath = self.media_dir / filename

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                print(f"  ✓ 已保存: {filename}")
                return str(filepath)
            else:
                print(f"  ✗ 下载失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"  ✗ 下载异常: {e}")
            return None

    def download_video(self, note, index):
        """
        下载视频文件（仅视频笔记）

        Args:
            note: 笔记数据
            index: 笔记序号

        Returns:
            str: 保存的文件路径
        """
        video_url = note.get('video', '')
        note_type = note.get('type', '')

        # 只处理视频笔记
        if note_type != 'video' or not video_url:
            return None

        try:
            print(f"  [{index}] 下载视频...")
            response = requests.get(video_url, headers=self.headers, timeout=300, stream=True)
            if response.status_code == 200:
                # 视频文件
                filename = f"{index:04d}_video.mp4"
                filepath = self.media_dir / filename

                # 流式写入
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"  ✓ 已保存: {filename} ({os.path.getsize(filepath)/1024/1024:.1f} MB)")
                return str(filepath)
            else:
                print(f"  ✗ 下载失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"  ✗ 下载异常: {e}")
            return None

    def transcribe_video(self, video_path, index):
        """
        使用 Whisper 转录视频

        Args:
            video_path: 视频文件路径
            index: 笔记序号

        Returns:
            str: 转录文本文件路径
        """
        if not video_path or not Path(video_path).exists():
            return None

        try:
            print(f"  [{index}] 转录视频...")

            # 检查 Whisper 是否可用
            whisper_cmd = shutil.which('whisper')

            if whisper_cmd:
                # 使用系统 Whisper
                output_file = self.media_dir / f"{index:04d}_transcript.txt"

                cmd = [
                    'whisper',
                    str(video_path),
                    '--model', 'base',
                    '--output_format', 'txt',
                    '--output_dir', str(self.media_dir),
                    '--output_type', 'txt'
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10分钟超时
                )

                if result.returncode == 0:
                    print(f"  ✓ 转录完成: {index:04d}_transcript.txt")
                    return str(output_file)
                else:
                    print(f"  ✗ 转录失败: {result.stderr[:100] if result.stderr else 'Unknown error'}")
                    return None
            else:
                # 系统没有 Whisper，尝试使用 OpenAI API
                print(f"  ⚠️  未找到系统 Whisper，跳过转录")
                return None

        except subprocess.TimeoutExpired:
            print(f"  ✗ 转录超时（10分钟）")
            return None
        except Exception as e:
            print(f"  ✗ 转录异常: {e}")
            return None

    def process_note(self, note, index):
        """
        处理单条笔记

        Args:
            note: 笔记数据
            index: 笔记序号

        Returns:
            dict: 处理结果
        """
        note_id = note.get('note_id', '')[:8]
        title = note.get('title', '无标题')
        desc = note.get('desc', '')
        note_type = note.get('type', 'normal')

        print(f"\n{'='*60}")
        print(f"笔记 {index}: {title}")
        print(f"类型: {note_type}")
        print(f"{'='*60}")

        result = {
            'index': index,
            'note_id': note_id,
            'title': title,
            'desc': desc,
            'type': note_type,
            'cover': None,
            'video': None,
            'transcript': None
        }

        # 下载封面
        result['cover'] = self.download_cover(note, index)

        # 下载视频（如果是视频笔记）
        if note_type == 'video':
            result['video'] = self.download_video(note, index)

            # 转录视频
            if result['video']:
                result['transcript'] = self.transcribe_video(result['video'], index)

        return result

    def generate_summary(self, results):
        """
        生成处理汇总报告

        Args:
            results: 处理结果列表
        """
        summary_file = self.output_dir / "汇总报告.md"

        # 统计
        total = len(results)
        video_count = sum(1 for r in results if r['type'] == 'video')
        cover_count = sum(1 for r in results if r['cover'])
        transcript_count = sum(1 for r in results if r['transcript'])

        # 生成 Markdown 报告
        content = f"""# 小红书媒体处理报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 处理统计

| 项目 | 数量 |
|------|------|
| 总笔记数 | {total} |
| 视频笔记 | {video_count} |
| 封面下载成功 | {cover_count} |
| 视频转录完成 | {transcript_count} |

## 📋 笔记列表

"""

        # 按视频笔记优先
        video_notes = [r for r in results if r['type'] == 'video']
        normal_notes = [r for r in results if r['type'] != 'video']

        if video_notes:
            content += "\n### 🎬 视频笔记\n\n"

            for r in video_notes[:10]:  # 只显示前10个
                status = "✓" if r['video'] else "✗"
                trans_status = "✓" if r['transcript'] else "✗"
                content += f"{status} **{r['title']}**\n"
                content += f"  - 封面: {'✓' if r['cover'] else '✗'}\n"
                content += f"  - 视频: {status}\n"
                content += f"  - 转录: {trans_status}\n\n"

            if len(video_notes) > 10:
                content += f"... 还有 {len(video_notes) - 10} 条视频笔记\n"

        if normal_notes:
            content += "\n### 📝 图文笔记\n\n"
            content += f"共 {len(normal_notes)} 条图文笔记（前10条）\n\n"

            for r in normal_notes[:10]:
                status = "✓" if r['cover'] else "✗"
                content += f"{status} **{r['title']}**\n"
                content += f"  - 封面: {status}\n\n"

            if len(normal_notes) > 10:
                content += f"... 还有 {len(normal_notes) - 10} 条图文笔记\n"

        content += f"""
## 📁 文件位置

- 媒体文件: `{self.media_dir.relative_to(self.output_dir)}/`
- 完整报告: `{summary_file.relative_to(self.output_dir)}`

## 💡 下一步操作

### 内容创作
- 视频文案: 查看 `*_transcript.txt` 文件
- 标题参考: 查看本报告中的笔记标题
- 封面参考: 使用 `{self.media_dir.relative_to(self.output_dir)}/` 中的图片

### 数据分析
- 使用 `data-analysis-expert` 技能进行数据分析
- 提取关键词、用户痛点等
"""

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n✅ 汇总报告已生成: {summary_file}")
        print(f"📁 媒体文件保存在: {self.media_dir}")

    def run(self, limit=None):
        """
        执行处理流程

        Args:
            limit: 处理数量限制（None 表示全部）
        """
        print("="*60)
        print("小红书媒体文件处理器")
        print("="*60)
        print()

        # 加载笔记
        notes = self.load_notes()
        if not notes:
            return

        # 限制处理数量
        if limit:
            notes = notes[:limit]
            print(f"⚠️  限制处理数量: {limit}")
        else:
            limit = len(notes)

        print(f"📋 开始处理 {len(notes)} 条笔记...\n")

        # 处理每条笔记
        results = []
        for i, note in enumerate(notes, 1):
            result = self.process_note(note, i)
            results.append(result)

            # 每处理5条输出进度
            if i % 5 == 0:
                print(f"  进度: {i}/{limit}")

        # 生成汇总报告
        self.generate_summary(results)

        print("\n" + "="*60)
        print("✅ 处理完成！")
        print("="*60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='小红书媒体文件后处理脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--input', '-i',
        help='MediaCrawler 输出目录',
        default='~/MediaCrawler/data/xhs/json'
    )

    parser.add_argument(
        '--output', '-o',
        help='处理结果输出目录',
        default=None
    )

    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='处理笔记数量限制（默认全部）',
        default=None
    )

    args = parser.parse_args()

    # 展开路径
    input_dir = Path(args.input).expanduser()
    output_dir = Path(args.output).expanduser() if args.output else None

    # 检查输入目录
    if not input_dir.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return 1

    # 创建处理器并执行
    processor = XHSMediaProcessor(input_dir, output_dir)
    processor.run(limit=args.limit)


if __name__ == '__main__':
    sys.exit(main())

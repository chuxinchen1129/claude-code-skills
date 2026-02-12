#!/usr/bin/env python3
"""
视频转文字集成脚本

功能：
1. 下载视频文件
2. 使用 video-scripts-extract Skill 转换为文字
3. 保存转写结果

依赖：
- video-scripts-extract Skill
- DASHSCOPE_API_KEY 环境变量

作者：大秘书系统
版本：v1.0.0
创建时间：2026-02-10
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import argparse
import urllib.request


class VideoTranscriberIntegration:
    """视频转文字集成器"""

    def __init__(self):
        """初始化集成器"""
        self.skill_dir = Path(__file__).parent.parent
        self.data_dir = self.skill_dir / "data"

        # 检查环境变量
        self.api_key = os.environ.get("DASHSCOPE_API_KEY")
        if not self.api_key:
            print("⚠️  警告: DASHSCOPE_API_KEY 环境变量未设置")
            print("⚠️  请设置: export DASHSCOPE_API_KEY=your_key_here")

    def download_video(self, video_url, output_path):
        """下载视频文件

        Args:
            video_url: 视频 URL
            output_path: 输出文件路径

        Returns:
            bool: 是否成功
        """
        print(f"下载视频: {video_url}")

        try:
            urllib.request.urlretrieve(video_url, output_path)
            print(f"✓ 视频已下载: {output_path}")
            return True
        except Exception as e:
            print(f"✗ 下载失败: {e}")
            return False

    def transcribe_video(self, video_path):
        """转写视频为文字

        Args:
            video_path: 视频文件路径

        Returns:
            str: 转写文字
        """
        print(f"转写视频: {video_path}")

        # TODO: 调用 video-scripts-extract Skill
        # 这里需要集成 video-scripts-extract Skill 的 API
        # 目前返回示例数据

        # 模拟调用 Skill
        # transcript = self._call_video_skill(video_path)

        # 示例返回
        transcript = "示例转写文字内容"

        print(f"✓ 转写完成，字数: {len(transcript)}")
        return transcript

    def transcribe_audio_url(self, audio_url):
        """转写音频 URL 为文字

        Args:
            audio_url: 音频 URL

        Returns:
            str: 转写文字
        """
        print(f"转写音频 URL: {audio_url}")

        # TODO: 使用 douyin MCP 的 recognize_audio_url
        # transcript = mcp__douyin__recognize_audio_url(audio_url)

        # 示例返回
        transcript = "示例转写文字内容"

        print(f"✓ 转写完成")
        return transcript

    def _call_video_skill(self, video_path):
        """调用 video-scripts-extract Skill

        Args:
            video_path: 视频文件路径

        Returns:
            str: 转写文字
        """
        # TODO: 实现 Skill 调用
        # 可能的方法：
        # 1. 使用 subprocess 调用 Skill CLI
        # 2. 直接导入 Skill 模块
        # 3. 使用 MCP 协议调用

        return "示例转写文字"

    def process_post_video(self, post, output_dir):
        """处理单条笔记的视频

        Args:
            post: 笔记数据
            output_dir: 输出目录

        Returns:
            str: 转写文字（如果有）
        """
        video_url = post.get("video_url", "")
        if not video_url:
            return None

        # 生成文件名
        note_id = post.get("id", "unknown")
        video_filename = f"{note_id}.mp4"
        video_path = output_dir / "videos" / video_filename
        transcript_path = output_dir / "transcripts" / f"{note_id}.txt"

        # 检查是否已转写
        if transcript_path.exists():
            print(f"✓ 转写文件已存在: {transcript_path}")
            with open(transcript_path, "r", encoding="utf-8") as f:
                return f.read()

        # 下载视频
        if self.download_video(video_url, video_path):
            # 转写视频
            transcript = self.transcribe_video(str(video_path))

            if transcript:
                # 保存转写结果
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(transcript)
                print(f"✓ 转写已保存: {transcript_path}")

                return transcript

        return None

    def process_all_videos(self, input_file=None):
        """处理所有笔记的视频

        Args:
            input_file: 输入 JSON 文件路径（可选）

        Returns:
            int: 成功转写的数量
        """
        print("=" * 80)
        print("视频转文字处理")
        print("=" * 80)

        # 加载数据
        if input_file:
            with open(input_file, "r", encoding="utf-8") as f:
                posts = json.load(f)
        else:
            # 从数据目录加载
            posts = self._load_all_posts()

        if not posts:
            print("✗ 没有数据")
            return 0

        print(f"✓ 加载了 {len(posts)} 条笔记")

        # 筛选有视频的笔记
        video_posts = [p for p in posts if p.get("video_url")]

        if not video_posts:
            print("⚠️  没有视频笔记")
            return 0

        print(f"✓ 找到 {len(video_posts)} 条视频笔记")

        # 创建输出目录
        today = datetime.now().strftime("%Y-%m-%d")
        output_dir = self.data_dir / "xiaohongshu_collection" / today
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "videos").mkdir(exist_ok=True)
        (output_dir / "transcripts").mkdir(exist_ok=True)

        # 处理每条视频笔记
        success_count = 0
        for i, post in enumerate(video_posts, 1):
            print(f"\n[{i}/{len(video_posts)}] 处理: {post.get('title', '未知标题')[:30]}")

            if self.process_post_video(post, output_dir):
                success_count += 1

        print("\n" + "=" * 80)
        print(f"✓ 处理完成！成功转写 {success_count}/{len(video_posts)} 条视频")
        print(f"✓ 输出目录: {output_dir}")
        print("=" * 80)

        return success_count

    def _load_all_posts(self):
        """加载所有笔记数据"""
        all_posts = []

        # 从小红书采集目录加载
        xhs_dir = self.data_dir / "xiaohongshu_collection"
        if xhs_dir.exists():
            for date_dir in xhs_dir.iterdir():
                if date_dir.is_dir():
                    raw_data_file = date_dir / "raw_data" / "posts.json"
                    if raw_data_file.exists():
                        with open(raw_data_file, "r", encoding="utf-8") as f:
                            posts = json.load(f)
                            all_posts.extend(posts)

        return all_posts


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="视频转文字集成")
    parser.add_argument("--input", help="输入 JSON 文件路径")
    parser.add_argument("--video", help="单个视频 URL")

    args = parser.parse_args()

    transcriber = VideoTranscriberIntegration()

    if args.video:
        # 处理单个视频
        print(f"处理单个视频: {args.video}")

        # 创建临时输出目录
        output_dir = Path("temp_transcript")
        output_dir.mkdir(exist_ok=True)

        post = {"video_url": args.video, "id": "manual"}
        result = transcriber.process_post_video(post, output_dir)

        if result:
            print(f"\n转写结果:\n{result}")
    else:
        # 批量处理
        transcriber.process_all_videos(input_file=args.input)


if __name__ == "__main__":
    main()

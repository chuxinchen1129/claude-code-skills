#!/usr/bin/env python3
"""
视频转文字脚本 - 使用本地 Whisper 模型

使用方法:
    python transcribe_local.py --input video.mp4 --output output.txt
    python transcribe_local.py --input video.mp4 --output output.txt --model base
    python transcribe_local.py --input video.mp4 --output subtitles.srt --format srt
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import whisper
except ImportError:
    print("错误: 请先安装 openai-whisper 库")
    print("安装命令: pip install openai-whisper")
    sys.exit(1)


def transcribe_with_local(input_file: str, output_file: str, output_format: str = "txt",
                          model_size: str = "base", language: str = "zh",
                          device: str = "cpu", verbose: bool = True):
    """
    使用本地 Whisper 模型转录视频/音频

    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        output_format: 输出格式 (txt, srt, json, vtt, md)
        model_size: 模型大小 (tiny, base, small, medium, large)
        language: 语言代码 (zh, en, auto)
        device: 设备 (cpu, cuda)
        verbose: 显示详细输出
    """
    # 检查文件是否存在
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"输入文件不存在: {input_file}")

    print(f"正在转录: {input_file}")
    print(f"使用模型: {model_size}")
    print(f"设备: {device}")
    print(f"语言: {language if language != 'auto' else '自动检测'}")

    try:
        # 加载模型
        print("正在加载模型...")
        model = whisper.load_model(model_size, device=device)

        # 转录
        print("正在转录...")
        if language == "auto":
            result = model.transcribe(input_file, verbose=verbose)
        else:
            result = model.transcribe(input_file, language=language, verbose=verbose)

        # 创建输出目录
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 根据格式输出
        if output_format == "txt":
            # 纯文本格式
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result["text"].strip())
            print(f"✅ 转录完成，已保存到: {output_file}")

        elif output_format == "srt":
            # SRT 字幕格式
            with open(output_file, "w", encoding="utf-8") as f:
                for i, segment in enumerate(result["segments"], 1):
                    start_time = format_timestamp_srt(segment["start"])
                    end_time = format_timestamp_srt(segment["end"])
                    text = segment["text"].strip()
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
            print(f"✅ 字幕生成完成，已保存到: {output_file}")

        elif output_format == "vtt":
            # VTT 字幕格式
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("WEBVTT\n\n")
                for segment in result["segments"]:
                    start_time = format_timestamp_vtt(segment["start"])
                    end_time = format_timestamp_vtt(segment["end"])
                    text = segment["text"].strip()
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
            print(f"✅ VTT 字幕生成完成，已保存到: {output_file}")

        elif output_format == "json":
            # JSON 格式（包含完整信息）
            import json
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ JSON 文件生成完成，已保存到: {output_file}")

        elif output_format == "md":
            # Markdown 格式（带时间戳）
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("# 视频转录\n\n")
                for segment in result["segments"]:
                    timestamp = format_timestamp_readable(segment["start"])
                    text = segment["text"].strip()
                    f.write(f"## [{timestamp}] {text}\n\n")
            print(f"✅ Markdown 文件生成完成，已保存到: {output_file}")

        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

        # 显示统计信息
        duration = result["segments"][-1]["end"] if result["segments"] else 0
        word_count = len(result["text"].split())
        print(f"\n转录统计:")
        print(f"  时长: {duration/60:.1f} 分钟")
        print(f"  字数: {word_count}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


def format_timestamp_srt(seconds: float) -> str:
    """格式化时间戳为 SRT 格式"""
    from datetime import timedelta
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """格式化时间戳为 VTT 格式"""
    from datetime import timedelta
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"


def format_timestamp_readable(seconds: float) -> str:
    """格式化时间戳为可读格式"""
    from datetime import timedelta
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def main():
    parser = argparse.ArgumentParser(
        description="视频转文字 - 使用本地 Whisper 模型",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转录为纯文本（使用 base 模型）
  python transcribe_local.py --input video.mp4 --output output.txt

  # 生成 SRT 字幕
  python transcribe_local.py --input video.mp4 --output subtitles.srt --format srt

  # 使用更大的模型（更准确）
  python transcribe_local.py --input video.mp4 --output output.txt --model medium

  # 指定语言
  python transcribe_local.py --input video.mp4 --output output.txt --language zh

  # 使用 GPU 加速
  python transcribe_local.py --input video.mp4 --output output.txt --device cuda
        """
    )

    parser.add_argument("--input", "-i", required=True,
                       help="输入文件路径（视频或音频）")
    parser.add_argument("--output", "-o", required=True,
                       help="输出文件路径")
    parser.add_argument("--format", "-f", default="txt",
                       choices=["txt", "srt", "vtt", "json", "md"],
                       help="输出格式 (默认: txt)")
    parser.add_argument("--model", "-m", default="base",
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper 模型大小 (默认: base)")
    parser.add_argument("--language", "-l", default="zh",
                       help="语言代码 (zh, en, auto，默认: zh)")
    parser.add_argument("--device", "-d", default="cpu",
                       choices=["cpu", "cuda"],
                       help="设备 (cpu, cuda，默认: cpu)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="显示详细输出")

    args = parser.parse_args()

    # 转录
    transcribe_with_local(
        input_file=args.input,
        output_file=args.output,
        output_format=args.format,
        model_size=args.model,
        language=args.language,
        device=args.device,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
视频转文字脚本 - 使用 OpenAI Whisper API

使用方法:
    python transcribe.py --input video.mp4 --output output.txt
    python transcribe.py --input video.mp4 --output transcript.json --format json
    python transcribe.py --input video.mp4 --output subtitles.srt --format srt
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import timedelta

try:
    import openai
except ImportError:
    print("错误: 请先安装 openai 库")
    print("安装命令: pip install openai")
    sys.exit(1)


def format_timestamp(seconds: float) -> str:
    """格式化时间戳为 SRT 格式"""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def transcribe_with_api(input_file: str, output_file: str, output_format: str = "txt",
                        language: str = "auto", model: str = "whisper-1",
                        api_key: str = None):
    """
    使用 OpenAI Whisper API 转录视频/音频

    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        output_format: 输出格式 (txt, srt, json, vtt)
        language: 语言代码 (zh, en, auto)
        model: Whisper 模型名称
        api_key: OpenAI API Key
    """
    # 设置 API Key
    if api_key:
        openai.api_key = api_key
    elif os.getenv("OPENAI_API_KEY"):
        openai.api_key = os.getenv("OPENAI_API_KEY")
    else:
        raise ValueError("请设置 OPENAI_API_KEY 环境变量或通过 --api_key 参数提供")

    # 检查文件是否存在
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"输入文件不存在: {input_file}")

    print(f"正在转录: {input_file}")
    print(f"使用模型: {model}")
    print(f"语言: {language if language != 'auto' else '自动检测'}")

    try:
        # 打开音频文件
        with open(input_file, "rb") as audio_file:
            # 调用 Whisper API
            if language == "auto":
                response = openai.Audio.transcribe(
                    model=model,
                    file=audio_file,
                    response_format="verbose_json"
                )
            else:
                response = openai.Audio.transcribe(
                    model=model,
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"
                )

        # 根据格式输出
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_format == "txt":
            # 纯文本格式
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(response["text"])
            print(f"✅ 转录完成，已保存到: {output_file}")

        elif output_format == "srt":
            # SRT 字幕格式
            with open(output_file, "w", encoding="utf-8") as f:
                for i, segment in enumerate(response["segments"], 1):
                    start_time = format_timestamp(segment["start"])
                    end_time = format_timestamp(segment["end"])
                    text = segment["text"].strip()
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
            print(f"✅ 字幕生成完成，已保存到: {output_file}")

        elif output_format == "vtt":
            # VTT 字幕格式
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("WEBVTT\n\n")
                for segment in response["segments"]:
                    start_time = format_timestamp(segment["start"]).replace(",", ".")
                    end_time = format_timestamp(segment["end"]).replace(",", ".")
                    text = segment["text"].strip()
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{text}\n\n")
            print(f"✅ VTT 字幕生成完成，已保存到: {output_file}")

        elif output_format == "json":
            # JSON 格式（包含完整信息）
            import json
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(response, f, ensure_ascii=False, indent=2)
            print(f"✅ JSON 文件生成完成，已保存到: {output_file}")

        elif output_format == "md":
            # Markdown 格式（带时间戳）
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("# 视频转录\n\n")
                for segment in response["segments"]:
                    timestamp = format_timestamp(segment["start"])
                    text = segment["text"].strip()
                    f.write(f"## [{timestamp}] {text}\n\n")
            print(f"✅ Markdown 文件生成完成，已保存到: {output_file}")

        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

        # 显示转录文本预览
        print("\n转录文本预览:")
        print("-" * 60)
        print(response["text"][:200] + "..." if len(response["text"]) > 200 else response["text"])
        print("-" * 60)

    except openai.error.APIError as e:
        print(f"❌ API 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="视频转文字 - 使用 OpenAI Whisper API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转录为纯文本
  python transcribe.py --input video.mp4 --output output.txt

  # 生成 SRT 字幕
  python transcribe.py --input video.mp4 --output subtitles.srt --format srt

  # 转录为 JSON（包含时间戳）
  python transcribe.py --input video.mp4 --output transcript.json --format json

  # 指定语言
  python transcribe.py --input video.mp4 --output output.txt --language zh

  # 使用 Whisper Large V3 模型
  python transcribe.py --input video.mp4 --output output.txt --model whisper-large-v3
        """
    )

    parser.add_argument("--input", "-i", required=True,
                       help="输入文件路径（视频或音频）")
    parser.add_argument("--output", "-o", required=True,
                       help="输出文件路径")
    parser.add_argument("--format", "-f", default="txt",
                       choices=["txt", "srt", "vtt", "json", "md"],
                       help="输出格式 (默认: txt)")
    parser.add_argument("--language", "-l", default="auto",
                       help="语言代码 (zh, en, auto，默认: auto)")
    parser.add_argument("--model", "-m", default="whisper-1",
                       choices=["whisper-1", "whisper-large-v3"],
                       help="Whisper 模型 (默认: whisper-1)")
    parser.add_argument("--api-key", "-k",
                       help="OpenAI API Key（或使用 OPENAI_API_KEY 环境变量）")

    args = parser.parse_args()

    # 转录
    transcribe_with_api(
        input_file=args.input,
        output_file=args.output,
        output_format=args.format,
        language=args.language,
        model=args.model,
        api_key=args.api_key
    )


if __name__ == "__main__":
    main()

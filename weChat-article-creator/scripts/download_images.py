#!/usr/bin/env python3
"""
图片下载工具

从 Unsplash 搜索并下载图片，
按顺序命名并保存到指定目录。

Usage:
    python download_images.py
"""

import requests
import os
from pathlib import Path
from urllib.parse import quote


# Unsplash API 配置
UNSPLASH_ACCESS_KEY = "Mx4coH5WrohL6YL-prHoieUWFFIc9TQNi6ZZKZu96Ks"  # Access Key
UNSPLASH_SECRET_KEY = "E7aKZ_mFRYdY1eqQRoG7KewJltoDQ6DnQzo25xd2W2E"  # Secret Key (备用)
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"


def download_image(url, save_path):
    """
    下载单张图片

    Args:
        url: 图片 URL
        save_path: 保存路径

    Returns:
        bool: 是否下载成功
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            f.write(response.content)

        return True
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False


def search_unsplash(query, per_page=10):
    """
    在 Unsplash 上搜索图片

    Args:
        query: 搜索关键词
        per_page: 返回结果数量

    Returns:
        图片信息列表
    """
    if not UNSPLASH_ACCESS_KEY or UNSPLASH_ACCESS_KEY == "YOUR_ACCESS_KEY_HERE":
        print("⚠️  警告: 未设置 Unsplash API key")
        print("请访问 https://unsplash.com/developers 申请免费 API key")
        print("然后将 API key 填入脚本的 UNSPLASH_ACCESS_KEY 变量\n")
        return []

    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape"  # 横向图片
    }

    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }

    try:
        response = requests.get(UNSPLASH_API_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        results = []
        for photo in data.get("results", []):
            results.append({
                "id": photo["id"],
                "url": photo["urls"]["regular"],  # 中等尺寸
                "full_url": photo["urls"]["full"],  # 高清
                "description": photo.get("description") or photo.get("alt_description", ""),
                "photographer": photo["user"]["name"],
                "photographer_url": photo["user"]["links"]["html"]
            })

        return results

    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return []


def download_images_by_keywords(keywords, output_dir, limit=1):
    """
    根据关键词列表下载图片

    Args:
        keywords: 关键词列表
        output_dir: 输出目录
        limit: 每个关键词下载的图片数量

    Returns:
        下载结果列表 [(keyword, filename), ...]
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []
    image_counter = 1

    for keyword in keywords:
        print(f"\n搜索关键词: {keyword}")

        # 搜索图片
        images = search_unsplash(keyword, per_page=limit)

        if not images:
            print(f"  ⚠️  未找到相关图片")
            continue

        # 下载图片
        for idx, img in enumerate(images[:limit]):
            # 生成文件名（按顺序）
            filename = f"image-{image_counter:02d}.jpg"
            filepath = output_path / filename

            print(f"  下载中: {filename}")
            print(f"    描述: {img['description']}")
            print(f"    摄影师: {img['photographer']}")

            # 下载图片
            if download_image(img["url"], filepath):
                results.append({
                    "keyword": keyword,
                    "filename": filename,
                    "description": img["description"],
                    "photographer": img["photographer"],
                    "photographer_url": img["photographer_url"]
                })
                image_counter += 1
            else:
                print(f"  ❌ 下载失败: {filename}")

    return results


def generate_image_markdown(results):
    """
    生成图片引用的 markdown 文档

    Args:
        results: 下载结果列表

    Returns:
        markdown 内容
    """
    md_content = "# 图片引用清单\n\n"
    md_content += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    md_content += "---\n\n"

    for idx, result in enumerate(results, 1):
        md_content += f"## {idx}. {result['filename']}\n\n"
        md_content += f"**关键词**: {result['keyword']}\n\n"
        md_content += f"**描述**: {result['description']}\n\n"
        md_content += f"**文章中引用**: `[图片：{result['filename']}]`\n\n"
        md_content += f"**摄影师**: [{result['photographer']}]({result['photographer_url']})\n\n"
        md_content += "---\n\n"

    # 使用说明
    md_content += "## 使用说明\n\n"
    md_content += "在文章中需要插入图片的位置，使用以下格式：\n\n"
    md_content += "```\n"
    md_content += "[图片：image-01.jpg]\n"
    md_content += "```\n\n"

    return md_content


def main():
    """
    主函数：命令行交互式使用
    """
    print("=== 图片下载工具 ===\n")

    # 检查 API key
    if not UNSPLASH_ACCESS_KEY or UNSPLASH_ACCESS_KEY == "YOUR_ACCESS_KEY_HERE":
        print("⚠️  首次使用需要配置 Unsplash API key\n")
        print("1. 访问 https://unsplash.com/developers")
        print("2. 注册并创建新应用（免费）")
        print("3. 获取 Access Key")
        print("4. 将 Access Key 填入此脚本的 UNSPLASH_ACCESS_KEY 变量\n")
        return

    # 获取输出目录
    default_output = Path(__file__).parent.parent / "assets" / "output" / "images"
    output_dir = input(f"请输入输出目录（默认: {default_output}）: ").strip()

    if not output_dir:
        output_dir = default_output

    # 获取关键词
    print("\n请输入图片搜索关键词（一行一个，输入空行结束）:")

    keywords = []
    for line in input():
        line = line.strip()
        if not line:
            break
        keywords.append(line)

    if not keywords:
        print("❌ 未输入关键词")
        return

    # 获取每个关键词下载数量
    limit_input = input("\n每个关键词下载几张图片？（默认1）: ").strip()
    limit = int(limit_input) if limit_input.isdigit() else 1

    # 下载图片
    print(f"\n开始下载图片...")
    results = download_images_by_keywords(keywords, output_dir, limit)

    # 显示结果
    if results:
        print(f"\n✅ 成功下载 {len(results)} 张图片")
        print(f"保存位置: {output_dir}\n")

        # 生成 markdown 文档
        from datetime import datetime
        md_content = generate_image_markdown(results)

        md_path = Path(output_dir).parent / "research" / "image_references.md"
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(md_content, encoding='utf-8')

        print(f"图片引用清单已保存到: {md_path}\n")

        # 显示图片列表
        print("=== 下载的图片 ===")
        for result in results:
            print(f"  {result['filename']} - {result['keyword']}")
    else:
        print("\n❌ 没有成功下载任何图片")


if __name__ == "__main__":
    main()

---
name: bilibili-video-summarizer
description: 自动总结B站收藏夹中的长视频。当用户提到"B站视频总结"、"bilibili收藏夹"、"视频字幕提取"、"B站视频AI总结"或需要定时自动处理B站收藏夹视频时使用此技能。支持抓取收藏夹、提取字幕（yt-dlp+ffmpeg）、AI结构化总结、飞书Base存储。
compatibility: requires yt-dlp, ffmpeg, python, 飞书API访问权限
---

# B站长视频自动总结技能

自动处理B站收藏夹中的长视频，提取字幕并生成AI结构化摘要，保存到飞书多维表格。

## 工作流程

```
收藏夹URL → 抓取视频列表 → 筛选新视频 → 提取字幕 → AI总结 → 飞书Base存储 → 更新处理记录
```

## 配置文件

在 `scripts/config.json` 中配置：

```json
{
  "favlist_url": "https://space.bilibili.com/UID/favlist?fid=收藏夹ID",
  "processed_videos_db": "processed_videos.json",
  "feishu": {
    "app_token": "飞书Base的app_token",
    "table_id": "表格ID"
  }
}
```

## 执行步骤

### 1. 加载配置和状态

```bash
python scripts/bilibili_summarizer.py --init
```

- 读取 `scripts/config.json`
- 加载 `processed_videos.json`（已处理视频ID集合）

### 2. 抓取收藏夹视频列表

```bash
python scripts/bilibili_summarizer.py --fetch
```

使用 B站API或 yt-dlp 获取收藏夹中的视频列表：
- 视频ID (bvid)
- 标题
- 时长（筛选 >10 分钟的视频）
- 上传时间
- 作者

**筛选条件**：
- 时长 > 10 分钟
- 视频ID 不在 `processed_videos` 中

### 3. 提取字幕

对每个新视频，使用 yt-dlp 提取字幕：

```bash
yt-dlp --write-auto-sub --sub-lang zh-Hans --skip-download \
  --sub-format "ttml" --convert-subs srt \
  "https://www.bilibili.com/video/{bvid}" -o subtitles/{bvid}.srt
```

如果自动字幕不可用，尝试手动字幕。

### 4. 生成AI摘要

读取字幕文件 `subtitles/{bvid}.srt`，调用AI生成结构化摘要：

```python
summary = generate_summary(transcript, video_info)
```

**摘要格式**：
```markdown
# {视频标题}

## 基本信息
- **视频ID**: {bvid}
- **作者**: {uploader}
- **时长**: {duration}
- **URL**: {video_url}
- **处理时间**: {timestamp}

## 核心观点
1. 观点一...
2. 观点二...
3. 观点三...

## 关键结论
- 结论一
- 结论二

## 技术要点（如适用）
- 要点一
- 要点二
```

### 5. 保存到飞书Base

使用飞书MCP工具或API，将摘要写入多维表格：

```python
# 使用飞书MCP工具
mcp__lark-mcp__bitable_v1_appTableRecord_create(
  path={"app_token": config.feishu.app_token, "table_id": config.feishu.table_id},
  data={
    "fields": {
      "视频标题": title,
      "视频ID": bvid,
      "视频URL": url,
      "作者": uploader,
      "时长": duration,
      "核心观点": key_points,  # 多选文本
      "关键结论": conclusions,
      "处理时间": timestamp
    }
  }
)
```

### 6. 更新处理记录

将成功处理的视频ID添加到 `processed_videos.json`：

```bash
python scripts/bilibili_summarizer.py --mark-processed {bvid}
```

## 完整命令

```bash
# 处理所有新视频
python scripts/bilibili_summarizer.py --run

# 查看待处理视频
python scripts/bilibili_summarizer.py --list-new

# 手动指定视频处理
python scripts/bilibili_summarizer.py --video {bvid}
```

## 错误处理

- **字幕提取失败**：记录到日志，跳过该视频
- **飞书写入失败**：重试3次，失败后记录到本地备份
- **网络错误**：等待后重试

## 定时任务设置

使用 crontab 或 launchd 设置定时执行：

```bash
# crontab -e
# 每天早上8点检查并处理新视频
0 8 * * * cd /path/to/skills/bilibili-video-summarizer && python scripts/bilibili_summarizer.py --run >> logs/summarizer.log 2>&1
```

## 输出示例

成功处理后的飞书Base记录：

| 视频标题 | 视频ID | 作者 | 时长 | 核心观点 | 关键结论 | 处理时间 |
|---------|--------|------|------|---------|---------|---------|
| Claude深度解析 | BV1xx | XXX | 25:30 | 1. LLM原理... 2. 架构设计... | - 模型规模是关键 | 2026-03-11 09:00 |

## 注意事项

1. **字幕依赖**：依赖B站提供的字幕，部分视频可能无字幕
2. **API限制**：注意B站API调用频率限制
3. **摘要质量**：长视频建议分段处理或提取关键片段
4. **飞书权限**：确保有Base的写入权限

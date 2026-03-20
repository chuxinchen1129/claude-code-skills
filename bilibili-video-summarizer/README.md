# B站视频自动总结技能

自动处理B站收藏夹中的长视频，提取字幕并生成AI结构化摘要，保存到飞书多维表格。

## 功能特性

- ✅ 自动抓取收藏夹视频列表
- ✅ 智能筛选新视频（时长 > 10 分钟）
- ✅ 自动提取字幕（yt-dlp + ffmpeg）
- ✅ AI 生成结构化摘要
- ✅ 飞书 Base 自动存储
- ✅ 定时自动运行支持

## 安装依赖

```bash
# 使用 pip 安装
pip install yt-dlp python-dateutil

# 或使用 conda
conda install -c conda-forge ffmpeg

# 验证安装
yt-dlp --version
ffmpeg -version
```

## 快速开始

### 1. 配置

复制 `config.json.template` 到 `config.json` 并填入：

```json
{
  "favlist_url": "https://space.bilibili.com/你的UID/favlist?fid=收藏夹ID",
  "feishu": {
    "app_token": "你的飞书app_token",
    "table_id": "你的飞书表格ID"
  }
}
```

### 2. 初始化

```bash
python scripts/bilibili_summarizer.py --init
```

### 3. 测试运行

```bash
# 查看待处理视频
python scripts/bilibili_summarizer.py --list-new

# 处理所有新视频
python scripts/bilibili_summarizer.py --run
```

## 定时任务

### crontab 方式

```bash
crontab -e

# 每天早上8点检查并处理新视频
0 8 * * * cd /path/to/skills/bilibili-video-summarizer && python scripts/bilibili_summarizer.py --run >> logs/summarizer.log 2>&1
```

### macOS launchd 方式

创建 `~/Library/LaunchAgents/com.bilibili-summarizer.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>B站视频总结</string>
    <key>ProgramArguments</key>
    <array>
        <string>scripts/bilibili_summarizer.py</string>
        <string>--run</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/echo/Desktop/DMS/skills/bilibili-video-summarizer</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>logs/summarizer.log</string>
</dict>
</plist>
```

加载任务：

```bash
launchctl load ~/Library/LaunchAgents/com.bilibili-summarizer.plist
```

## 文件结构

```
bilibili-video-summarizer/
├── SKILL.md                 # 技能主文档
├── scripts/
│   ├── config.json            # 配置文件（需填写）
│   ├── config.json.template  # 配置模板
│   ├── bilibili_summarizer.py # 主程序
│   └── feishu_uploader.py     # 飞书上传模块
├── subtitles/               # 字幕存储目录
├── logs/                   # 日志目录
└── processed_videos.json    # 已处理视频记录
```

## 注意事项

1. **飞书权限**：需要确保有 Base 的写入权限
2. **API 限制**：注意 B 站 API 调用频率
3. **字幕依赖**：部分视频可能无字幕
4. **网络环境**：需要稳定的网络连接

## 故障排除

### 字幕提取失败
- 检查 yt-dlp 是否为最新版本
- 确认网络连接
- 检查视频是否有字幕

### 飞书写入失败
- 检查 app_token 是否有效
- 检查表格 ID 是否正确
- 查看日志获取详细错误信息

## 支持

遇到问题请检查 `logs/summarizer.log` 获取详细错误信息。

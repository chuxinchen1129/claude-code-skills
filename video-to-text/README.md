# Video-to-Text Skill - 快速使用指南

> **视频转文字技能**
> **核心功能**: 视频/音频转文字、字幕生成

---

## 🚀 一分钟上手

### 使用 Whisper API（推荐）

```bash
# 1. 安装依赖
pip install openai

# 2. 设置 API Key
export OPENAI_API_KEY="sk-..."

# 3. 转换视频为文字
python ~/.config/claude-code/skills/video-to-text/scripts/transcribe.py \
  --input video.mp4 \
  --output output.txt
```

### 使用本地 Whisper（免费）

```bash
# 1. 安装依赖
pip install openai-whisper

# 2. 转换视频为文字
python ~/.config/claude-code/skills/video-to-text/scripts/transcribe_local.py \
  --input video.mp4 \
  --output output.txt
```

---

## 📋 常用命令

### 基础转录

**Whisper API**:
```bash
python scripts/transcribe.py \
  --input video.mp4 \
  --output output.txt \
  --language zh
```

**本地 Whisper**:
```bash
python scripts/transcribe_local.py \
  --input video.mp4 \
  --output output.txt \
  --model base \
  --language zh
```

### 生成字幕

```bash
python scripts/generate_srt.py \
  --input transcript.json \
  --output subtitles.srt
```

### 文本总结

```bash
python scripts/summarize.py \
  --input transcript.txt \
  --output summary.md \
  --format markdown
```

### 批量处理

```bash
python scripts/batch_transcribe.py \
  --input_folder ./videos \
  --output_folder ./transcripts \
  --format txt,srt
```

---

## 🎯 使用场景

### 场景 1: 视频内容总结

```bash
# 1. 转录视频
python scripts/transcribe.py --input video.mp4 --output transcript.txt

# 2. 生成摘要
python scripts/summarize.py --input transcript.txt --output summary.md
```

### 场景 2: 生成视频字幕

```bash
# 1. 转录视频（带时间戳）
python scripts/transcribe.py \
  --input video.mp4 \
  --output transcript.json \
  --format json

# 2. 生成 SRT 字幕
python scripts/generate_srt.py \
  --input transcript.json \
  --output subtitles.srt
```

### 场景 3: 会议录音转文字

```bash
# 转录会议录音
python scripts/transcribe.py \
  --input meeting.mp3 \
  --output meeting.txt \
  --language zh

# 生成会议纪要
python scripts/summarize.py \
  --input meeting.txt \
  --output meeting_minutes.md \
  --type meeting
```

---

## ⚙️ 配置说明

### Whisper API 配置

**环境变量**:
```bash
export OPENAI_API_KEY="sk-..."
export WHISPER_MODEL="whisper-1"
```

**配置文件**: `config/config.yaml`
```yaml
api_key: "${OPENAI_API_KEY}"
model: "whisper-1"
language: "zh"
temperature: 0.0

output_format:
  - txt
  - srt
  - json
```

### 本地 Whisper 配置

**模型选择**:
```yaml
model_size: "base"  # tiny, base, small, medium, large
device: "cpu"       # cpu 或 cuda
language: "zh"
```

**模型对比**:

| 模型 | 大小 | 速度 | 准确度 | 推荐场景 |
|------|------|------|--------|---------|
| tiny | ~40MB | 最快 | 较低 | 快速测试 |
| base | ~80MB | 快 | 中等 | 日常使用 ⭐ |
| small | ~250MB | 中等 | 较好 | 平衡选择 |
| medium | ~770MB | 较慢 | 好 | 高准确度 |
| large | ~1.5GB | 最慢 | 最好 | 专业使用 |

---

## 📂 输出格式

### TXT（纯文本）

```
大家好，欢迎来到今天的视频。今天我们要讨论的话题是人工智能。
首先，让我们来看看AI的发展历史。
```

### SRT（字幕文件）

```srt
1
00:00:00,000 --> 00:00:05,000
大家好，欢迎来到今天的视频。

2
00:00:05,000 --> 00:00:12,000
今天我们要讨论的话题是人工智能。
```

### JSON（结构化）

```json
{
  "text": "大家好...",
  "segments": [
    {"start": 0.0, "end": 5.0, "text": "大家好，欢迎来到今天的视频。"}
  ]
}
```

### Markdown（带时间戳）

```markdown
# 视频转录

## [00:00:00] 开场
大家好，欢迎来到今天的视频。

## [00:00:05] 话题介绍
今天我们要讨论的话题是人工智能。
```

---

## 💡 最佳实践

### 1. 文件准备

- ✅ 高质量音频/视频
- ✅ 清晰的语音，无背景噪音
- ✅ 文件大小 < 500MB（API 模式）

### 2. 语言选择

- ✅ 明确指定语言：`--language zh`
- ✅ 中英混合：`--language auto`

### 3. 模型选择

- **日常使用**: `base`（平衡速度和准确度）
- **高准确度**: `medium` 或 `large`
- **快速测试**: `tiny`

### 4. 输出格式

- 纯文本：TXT
- 视频字幕：SRT
- 数据处理：JSON
- 阅读笔记：Markdown

---

## ⚠️ 常见问题

### Q1: Whisper API 成本？

**A**:
- 按使用量计费
- 价格：$0.006 / 分钟
- 示例：1小时视频 ≈ $0.36

### Q2: 本地 Whisper 速度？

**A**:
- base 模型：实时速度（1小时视频 ≈ 10-15分钟）
- large 模型：较慢（1小时视频 ≈ 30-60分钟）
- GPU 加速：可提速 5-10 倍

### Q3: 如何处理大文件？

**A**:
- API 模式：自动分块处理（每块 25MB）
- 本地模式：无限制，但需注意内存

### Q4: 准确度如何提高？

**A**:
- ✅ 使用高质量音频
- ✅ 减少背景噪音
- ✅ 使用更大的模型（medium/large）
- ✅ 明确指定语言

### Q5: 支持哪些语言？

**A**:
- 支持 50+ 种语言
- 中文：`zh`
- 英文：`en`
- 自动检测：`auto`

---

## 🔗 完整文档

查看完整文档：
```bash
cat ~/.config/claude-code/skills/video-to-text/SKILL.md
```

**核心内容**:
- 详细使用场景
- API 参考
- 高级功能
- 性能对比
- 最佳实践

---

## 📞 需要帮助？

**查看完整技能说明**:
- SKILL.md：完整技能文档
- examples/：使用示例
- docs/：高级指南

**技术支持**:
- OpenAI Whisper: https://platform.openai.com/docs/guides/speech-to-text
- GitHub: https://github.com/openai/whisper

---

**版本**: v1.0
**最后更新**: 2026-01-27

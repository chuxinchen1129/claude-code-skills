# Video-to-Text Skill

> **视频转文字技能**
> **版本**: v1.0
> **核心功能**: 视频/音频转文字、字幕生成、内容总结

---

## 🎯 技能概述

Video-to-Text 是一个强大的视频和音频转文字工具，使用 OpenAI Whisper 模型将视频和音频文件转换为文本，支持自动生成字幕文件、时间戳保留和内容总结。

### 核心能力

1. **视频转文字**：MP4, MOV, M4V 等视频格式转换为文本
2. **音频转文字**：MP3, WAV, M4A 等音频格式转换为文本
3. **字幕生成**：自动生成 SRT、VTT 等字幕文件
4. **时间戳保留**：保留每个句子的时间戳信息
5. **多语言支持**：支持中文、英文等多种语言
6. **内容总结**：基于转录文本自动生成摘要
7. **说话人识别**（可选）：识别不同的说话人

### 支持的格式

**视频格式**:
- MP4, MOV, M4V, AVI, MKV, WebM

**音频格式**:
- MP3, WAV, M4A, AAC, FLAC, OGG

**输出格式**:
- 纯文本（TXT）
- 字幕文件（SRT, VTT）
- JSON（包含时间戳）
- Markdown（带时间戳）

---

## 🚀 快速开始

### 基础使用

**使用 Whisper API**（推荐）:
```bash
# 安装依赖
pip install openai

# 转换视频为文字
python scripts/transcribe.py --input video.mp4 --output output.txt
```

**使用本地 Whisper 模型**:
```bash
# 安装依赖
pip install openai-whisper

# 转换视频为文字
python scripts/transcribe_local.py --input video.mp4 --output output.txt
```

---

## 📋 使用场景

### 场景 1: 视频内容总结

**任务**: 将长视频转换为文本并生成摘要

**流程**:
1. 视频转文字
2. 清理和分段文本
3. 生成摘要（关键点提取）
4. 输出 Markdown 格式总结

**示例**:
- 输入：1小时的教学视频
- 输出：10分钟的阅读摘要

### 场景 2: 采访记录整理

**任务**: 将采访录音转换为文字记录

**流程**:
1. 音频转文字
2. 保留时间戳
3. 识别说话人（可选）
4. 输出结构化访谈记录

**输出格式**:
```markdown
## 采访记录

**采访时间**: 2026-01-27
**采访对象**: XXX
**采访时长**: 45分钟

### 问题1: ...
**对象**: [00:02:15] 回答内容...
```

### 场景 3: 视频字幕生成

**任务**: 为视频生成字幕文件

**流程**:
1. 视频转文字（带时间戳）
2. 生成 SRT 格式字幕
3. 自动分段和断句
4. 导出字幕文件

**输出**:
- SRT 文件（视频编辑软件兼容）
- VTT 文件（Web 字幕）

### 场景 4: 会议记录转录

**任务**: 会议录音转文字

**流程**:
1. 会议录音转文字
2. 识别发言人（可选）
3. 提取关键决策和行动项
4. 生成会议纪要

**输出**:
- 完整转录文本
- 会议纪要（Markdown）
- 行动项清单

### 场景 5: 播客文本化

**任务**: 播客音频转文字

**流程**:
1. 播客音频转文字
2. 识别章节和话题
3. 生成带时间戳的文本
4. 输出博客文章格式

---

## 🔧 配置说明

### Whisper API 配置

**环境变量**:
```bash
# OpenAI API Key
export OPENAI_API_KEY="sk-..."

# 默认模型
export WHISPER_MODEL="whisper-1"  # whisper-1 或 whisper-large-v3
```

**配置文件**: `config/config.yaml`
```yaml
# Whisper API 配置
api_key: "${OPENAI_API_KEY}"
model: "whisper-1"
language: "zh"  # 自动检测或指定语言
temperature: 0.0

# 输出配置
output_format:
  - txt      # 纯文本
  - srt      # 字幕文件
  - json     # JSON格式（含时间戳）

# 处理配置
chunk_size: 25  # MB，大文件分块处理
verbose: true
```

### 本地 Whisper 配置

**模型选择**:
```yaml
# 模型大小（越大越准确，但越慢）
model_size: "base"  # tiny, base, small, medium, large

# 设备配置
device: "cpu"  # cpu 或 cuda（如果有GPU）
compute_type: "float32"  # float32, float16, int8

# 语言配置
language: "zh"  # 中文
task: "transcribe"  # transcribe 或 translate
```

---

## 📂 文件结构

```
video-to-text/
├── SKILL.md                 # 本文件
├── README.md                # 快速使用指南
├── config/
│   ├── config.yaml          # 配置文件
│   └── config.example.yaml  # 配置示例
├── scripts/
│   ├── transcribe.py        # Whisper API 转录脚本
│   ├── transcribe_local.py  # 本地 Whisper 转录脚本
│   ├── generate_srt.py      # 生成 SRT 字幕
│   ├── summarize.py         # 文本总结
│   └── utils.py             # 工具函数
├── examples/
│   ├── video_example.mp4    # 示例视频（小文件）
│   └── output_example.txt   # 示例输出
└── docs/
    ├── api_reference.md     # API 参考
    └── advanced_guide.md    # 高级使用指南
```

---

## 🛠️ 核心脚本

### transcribe.py（Whisper API）

**功能**: 使用 OpenAI Whisper API 转录视频/音频

**用法**:
```bash
python scripts/transcribe.py \
  --input video.mp4 \
  --output output.txt \
  --format txt,srt,json \
  --language zh
```

**参数**:
- `--input`: 输入文件路径
- `--output`: 输出文件路径
- `--format`: 输出格式（txt, srt, json, vtt）
- `--language`: 语言代码（zh, en, auto）
- `--model`: Whisper 模型（whisper-1, whisper-large-v3）
- `--timestamps`: 是否保留时间戳

**输出示例**:
```
[00:00:00] 大家好，欢迎来到今天的视频。
[00:00:05] 今天我们要讨论的话题是人工智能。
[00:00:12] 首先，让我们来看看AI的发展历史。
```

---

### transcribe_local.py（本地 Whisper）

**功能**: 使用本地 Whisper 模型转录（离线，免费）

**用法**:
```bash
python scripts/transcribe_local.py \
  --input video.mp4 \
  --output output.txt \
  --model base \
  --language zh
```

**参数**:
- `--input`: 输入文件路径
- `--output`: 输出文件路径
- `--model`: 模型大小（tiny, base, small, medium, large）
- `--language`: 语言代码
- `--device`: 设备（cpu, cuda）
- `--verbose`: 显示详细输出

**模型对比**:

| 模型 | 大小 | 速度 | 准确度 | 内存占用 |
|------|------|------|--------|---------|
| tiny | ~40MB | 最快 | 较低 | ~1GB |
| base | ~80MB | 快 | 中等 | ~1GB |
| small | ~250MB | 中等 | 较好 | ~2GB |
| medium | ~770MB | 较慢 | 好 | ~5GB |
| large | ~1.5GB | 最慢 | 最好 | ~10GB |

**推荐**:
- 日常使用：`base` 或 `small`
- 高准确度：`medium` 或 `large`
- 快速测试：`tiny`

---

### generate_srt.py

**功能**: 生成标准 SRT 字幕文件

**用法**:
```bash
python scripts/generate_srt.py \
  --input transcript.json \
  --output subtitles.srt
```

**SRT 格式示例**:
```srt
1
00:00:00,000 --> 00:00:05,000
大家好，欢迎来到今天的视频。

2
00:00:05,000 --> 00:00:12,000
今天我们要讨论的话题是人工智能。
```

---

### summarize.py

**功能**: 基于转录文本生成摘要

**用法**:
```bash
python scripts/summarize.py \
  --input transcript.txt \
  --output summary.md \
  --format markdown
```

**摘要类型**:
- 关键点提取
- 章节总结
- 行动项提取
- 问答对生成

---

## 📊 输出格式

### TXT 格式（纯文本）

```
大家好，欢迎来到今天的视频。今天我们要讨论的话题是人工智能。
首先，让我们来看看AI的发展历史。人工智能的概念最早出现在1956年的达特茅斯会议上。
...
```

### SRT 格式（字幕）

```srt
1
00:00:00,000 --> 00:00:05,000
大家好，欢迎来到今天的视频。

2
00:00:05,000 --> 00:00:12,000
今天我们要讨论的话题是人工智能。
```

### JSON 格式（结构化数据）

```json
{
  "text": "大家好，欢迎来到今天的视频。",
  "segments": [
    {
      "start": 0.0,
      "end": 5.0,
      "text": "大家好，欢迎来到今天的视频。"
    },
    {
      "start": 5.0,
      "end": 12.0,
      "text": "今天我们要讨论的话题是人工智能。"
    }
  ]
}
```

### Markdown 格式（带时间戳）

```markdown
# 视频转录

## [00:00:00] 开场

大家好，欢迎来到今天的视频。

## [00:00:05] 话题介绍

今天我们要讨论的话题是人工智能。
```

---

## 🎯 与其他 Agent 的协作

### 与写作Agent协作

**场景**: 基于视频内容创作文章

**流程**:
1. 视频转文字
2. 提取关键观点
3. 写作Agent基于转录文本创作文章
4. 引用原文时间戳

### 与知识Agent协作

**场景**: 视频内容归档到知识库

**流程**:
1. 播客视频转文字
2. 提取关键信息
3. 生成知识卡片
4. 存储到知识库

### 与数据分析Agent协作

**场景**: 分析大量视频内容

**流程**:
1. 批量视频转文字
2. 文本分析和关键词提取
3. 生成分析报告
4. 可视化趋势

---

## ⚙️ 高级功能

### 说话人识别

**功能**: 识别不同的说话人（需要额外配置）

**实现**:
```python
# 使用 pyannote.audio
from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization"
)

diarization =_pipeline(audio_path)
# 输出：说话人1 [00:00:00 - 00:01:30]
#       说话人2 [00:01:30 - 00:02:45]
```

### 多语言处理

**自动语言检测**:
```python
# Whisper 自动检测语言
language = transcript.detect_language()
```

**翻译功能**:
```python
# 翻译为英文
task = "translate"  # 而不是 "transcribe"
```

### 批量处理

**处理多个文件**:
```bash
python scripts/batch_transcribe.py \
  --input_folder ./videos \
  --output_folder ./transcripts \
  --format txt,srt
```

---

## 💡 最佳实践

### 1. 文件准备

- ✅ 使用高质量的音频/视频文件
- ✅ 确保音频清晰，无背景噪音
- ✅ 文件大小建议 < 500MB（Whisper API 限制）
- ✅ 大文件先分割再处理

### 2. 语言选择

- ✅ 明确指定语言（更准确）
- ✅ 中英文混合：使用 `auto` 检测
- ✅ 纯中文：指定 `zh`
- ✅ 纯英文：指定 `en`

### 3. 模型选择

**API 模式**:
- 速度优先：`whisper-1`
- 准确度优先：`whisper-large-v3`

**本地模式**:
- 快速测试：`tiny`
- 日常使用：`base` 或 `small`
- 高准确度：`medium` 或 `large`

### 4. 输出格式

- 纯文本：TXT
- 视频字幕：SRT
- Web 字幕：VTT
- 结构化数据：JSON
- 带时间戳：Markdown

---

## 📈 性能对比

### Whisper API vs 本地 Whisper

| 特性 | API | 本地 |
|------|-----|------|
| 速度 | 快 | 慢（取决于硬件） |
| 成本 | 按使用量付费 | 免费 |
| 准确度 | 高 | 高（大模型） |
| 网络要求 | 需要 | 不需要 |
| 文件大小限制 | 25MB（分块） | 无限制 |
| 隐私性 | 上传到 OpenAI | 完全本地 |
| 语言支持 | 50+ | 50+ |

### 推荐使用场景

**使用 API**:
- ✅ 小文件（< 25MB）
- ✅ 需要快速结果
- ✅ 不介意上传文件
- ✅ 偶尔使用

**使用本地**:
- ✅ 大文件（> 25MB）
- ✅ 隐私敏感内容
- ✅ 频繁使用
- ✅ 离线环境
- ✅ 有 GPU 加速

---

## 🔗 参考资源

### 官方文档

- OpenAI Whisper API: https://platform.openai.com/docs/guides/speech-to-text
- GitHub Whisper: https://github.com/openai/whisper

### 相关工具

- pyannote.audio: 说话人识别
- FFmpeg: 视频音频处理
-Subtitle Edit: 字幕编辑工具

---

## ⚠️ 注意事项

### API 使用限制

- 文件大小：最大 25MB（需分块）
- 每日限制：根据 API 额度
- 成本：按使用量计费
- 隐私：文件上传到 OpenAI

### 本地使用限制

- 硬件要求：CPU 较慢，GPU 推荐
- 存储空间：模型占用 1-10GB
- 速度：大模型较慢
- 内存：至少 8GB RAM

### 准确度影响

**影响准确度的因素**:
- 音频质量（噪音、回声）
- 说话速度（过快或过慢）
- 口音和方言
- 专业术语
- 背景音乐

**提高准确度**:
- ✅ 使用高质量音频
- ✅ 减少背景噪音
- ✅ 清晰发音
- ✅ 避免多说话人重叠
- ✅ 使用更大的模型

---

## 🚀 后续优化方向

- [ ] 说话人识别集成
- [ ] 实时转录（流式）
- [ ] 多语言翻译
- [ ] 标点符号优化
- [ ] 专业术语词典
- [ ] 章节自动分割
- [ ] 情感分析
- [ ] 关键词高亮

---

**Skill 版本**: v1.0
**最后更新**: 2026-01-27
**状态**: ✅ 已完成，可以使用

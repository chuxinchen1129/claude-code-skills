---
name: wuxin-sleep-hotspot-collector
description: 悟昕睡眠热点采集分析系统 - 自动采集小红书/微信公众号/抖音睡眠相关内容，分析爆款特征，生成报告并上传飞书。当用户提到"采集睡眠热点"、"分析小红书睡眠内容"、"每周内容分析"时使用。
version: 1.0.0
created: 2026-02-10
updated: 2026-02-10
---

# 悟昕睡眠热点采集分析系统

## 🎯 核心功能

自动采集和分析睡眠相关内容的热点数据，支持：
- **小红书自动采集**：关键词"睡眠仪"、"左点"、"睡眠"
- **多平台链接处理**：小红书、微信公众号、抖音
- **视频转文字**：自动下载视频并提取文案
- **每周自动分析**：爆款特征、标题公式、内容结构
- **飞书集成**：自动上传数据和报告

---

## 📁 目录结构

**Important**: 所有脚本位于 `scripts/` 子目录。

**Agent 执行说明**:
1. 确定此 SKILL.md 文件的目录路径为 `SKILL_DIR`
2. 脚本路径 = `${SKILL_DIR}/scripts/<script-name>.py`
3. 将本文档中所有 `${SKILL_DIR}` 替换为实际路径

```
${SKILL_DIR}/
├── SKILL.md                    # 本文件
├── scripts/                    # Python 脚本
│   ├── xiaohongshu_collector.py    # 小红书采集
│   ├── link_processor.py           # 链接处理器
│   ├── video_downloader.py         # 视频下载
│   ├── video_transcriber.py        # 视频转文字
│   ├── weekly_analyzer.py          # 每周分析器
│   └── feishu_uploader.py          # 飞书上传
├── references/                 # 参考文档
│   ├──爆款特征分析模板.md
│   ├── 标题公式库.md
│   └── 内容结构分析框架.md
├── config/                     # 配置文件
│   ├── keywords.json           # 采集关键词
│   └── platforms.json          # 平台配置
└── data/                       # 数据存储
    ├── xiaohongshu_collection/ # 小红书采集数据
    └── feishu_input/           # 飞书输入数据
```

---

## 🚀 快速开始

### 场景 1：小红书自动采集

**触发词**：
- "采集小红书睡眠热点"
- "分析睡眠仪相关内容"
- "采集左点睡眠仪数据"

**执行流程**：
```bash
# 使用 MediaCrawler Skill 采集数据
# 采集关键词：睡眠仪、左点、睡眠
# 筛选条件：TOP30 高互动笔记
```

**数据存储**：
```
data/xiaohongshu_collection/
└── [YYYY-MM-DD]/
    ├── raw_data/           # 原始数据 JSON
    ├── covers/            # 封面图片
    ├── videos/            # 下载的视频
    ├── transcripts/       # 视频转文字
    └── analysis/          # 分析报告
```

### 场景 2：处理链接

**触发词**：
- "分析这个链接"
- "采集这个笔记"
- 用户发送小红书/微信/抖音链接

**支持平台**：
| 平台 | 工具 | 说明 |
|------|------|------|
| 小红书 | MediaCrawler Skill | 完整数据采集 |
| 微信公众号 | baoyu-url-to-markdown Skill | 文章转 Markdown |
| 抖音 | douyin MCP Tools | 视频解析和转文字 |
| 其他网页 | baoyu-url-to-markdown Skill | 网页转 Markdown |

**执行流程**：
```
用户发送链接 → 识别平台 → 使用对应工具抓取
→ 下载视频/图片 → 转出文字 → 保存到文件夹
```

**数据存储**：
```
data/feishu_input/
└── [YYYY-MM-DD_HH-MM]/
    ├── source/            # 来源链接
    ├── covers/           # 封面图片
    ├── videos/           # 下载的视频
    ├── transcripts/      # 视频转文字
    └── content/          # 文本内容
```

### 场景 3：每周自动分析

**触发词**：
- "执行每周分析"
- "生成内容分析报告"
- "分析本周数据"

**执行时间**：每周一中午 12:00（通过 daily-review Skill 集成）

**分析内容**：
1. **互动数据分析**：点赞、评论、收藏趋势
2. **标题特征提取**：爆款标题公式识别
3. **内容结构分析**：intro/3板块/CTA 识别
4. **核心卖点统计**：品牌卖点使用情况
5. **情感词汇分析**：高频情感词统计
6. **数据引用情况**：科学数据引用统计

**输出报告**：
```
data/weekly_reports/
└── [YYYY-MM-DD]/
    ├── 分析报告.md         # Markdown 分析报告
    ├── 小红书数据表.xlsx   # 数据表格
    └── 公众号数据表.xlsx   # 公众号数据表格
```

---

## 🔧 脚本说明

### 1. xiaohongshu_collector.py

**功能**：小红书自动采集

**依赖**：MediaCrawler Skill

**执行**：
```bash
python3 ${SKILL_DIR}/scripts/xiaohongshu_collector.py
```

**参数**：
- `--keywords`: 采集关键词（默认：睡眠仪,左点,睡眠）
- `--limit`: 采集数量（默认：100）
- `--top`: 取 TOP N（默认：30）

### 2. link_processor.py

**功能**：多平台链接处理

**执行**：
```bash
python3 ${SKILL_DIR}/scripts/link_processor.py <url>
```

**支持**：
- 小红书笔记链接
- 微信公众号文章链接
- 抖音视频链接
- 其他网页链接

### 3. weekly_analyzer.py

**功能**：每周数据分析

**执行**：
```bash
python3 ${SKILL_DIR}/scripts/weekly_analyzer.py
```

**输出**：
- Markdown 分析报告
- Excel 数据表格
- 更新建议

### 4. feishu_uploader.py

**功能**：飞书上传（集成 feishu-automation-v2）

**执行**：
```bash
python3 ${SKILL_DIR}/scripts/feishu_uploader.py --report <报告路径> --table <表格路径>
```

**依赖**：feishu-automation-v2 Skill

---

## 📋 配置文件

### config/keywords.json

采集关键词配置：

```json
{
  "xiaohongshu": ["睡眠仪", "左点", "睡眠"],
  "douyin": ["睡眠仪", "左点睡眠仪"],
  "wechat": ["睡眠", "失眠", "助眠"]
}
```

### config/platforms.json

平台配置：

```json
{
  "xiaohongshu": {
    "enabled": true,
    "tool": "MediaCrawler",
    "min_likes": 100
  },
  "douyin": {
    "enabled": true,
    "tool": "douyin-mcp"
  },
  "wechat": {
    "enabled": true,
    "tool": "baoyu-url-to-markdown"
  }
}
```

---

## 🔄 自动化集成

### 每周自动分析（通过 daily-review Skill）

集成到 daily-review Skill 的定时任务中：

**配置文件**：`scripts/auto_review_config.yaml`

```yaml
schedule: "0 12 * * 1"  # 每周一中午 12:00
actions:
  - type: "xiaohongshu_collect"
    keywords: ["睡眠仪", "左点", "睡眠"]
  - type: "analyze"
    output: "weekly_report"
  - type: "feishu_upload"
```

---

## 📊 分析报告模板

### 报告结构

```markdown
# 睡眠热点内容分析报告 - YYYY-MM-DD

## 一、本周数据概览
- 采集笔记数：XX 篇
- 总互动量：XX 万
- 爆款笔记（>1000赞）：XX 篇

## 二、爆款特征分析
### 2.1 标题公式 TOP5
1. [公式类型] - 出现次数
2. ...

### 2.2 内容结构分析
- Intro 类型分布
- 3板块主题分布
- CTA 类型分布

### 2.3 核心卖点使用
- 卖点1：出现次数
- 卖点2：出现次数

## 三、趋势洞察
### 3.1 新兴话题
- 话题1：描述
- 话题2：描述

### 3.2 情感词汇 TOP10
1. 词汇 - 频次
2. ...

## 四、更新建议
1. 建议添加到参考文档的案例
2. 建议关注的新趋势
3. 建议调整的内容方向
```

---

## 🎯 触发场景

| 用户输入 | 触发动作 |
|---------|---------|
| "采集小红书睡眠热点" | 执行小红书自动采集 |
| "分析这个链接" + URL | 处理链接并分析 |
| "执行每周分析" | 生成每周分析报告 |
| "上传到飞书" | 上传数据和报告到飞书 |

---

## 🔗 依赖技能

| Skill | 用途 |
|-------|------|
| **media-crawler** | 小红书数据采集 |
| **baoyu-url-to-markdown** | 微信/网页转 Markdown |
| **douyin-mcp** | 抖音视频解析 |
| **video-scripts-extract** | 视频转文字 |
| **feishu-automation-v2** | 飞书上传和通知 |
| **daily-review** | 定时任务调度 |

---

## 📝 注意事项

1. **首次使用**：确保已配置相关依赖技能
2. **飞书上传**：需要先完成 OAuth 授权（feishu-automation-v2）
3. **视频处理**：视频转文字需要 DASHSCOPE_API_KEY 环境变量
4. **定时任务**：通过 daily-review Skill 配置

---

## 🚨 故障排除

### 问题 1：MediaCrawler 采集失败

**检查**：
- MediaCrawler Skill 是否已安装
- 网络连接是否正常
- 关键词是否正确

### 问题 2：视频转文字失败

**解决**：
```bash
export DASHSCOPE_API_KEY=your_key_here
```

### 问题 3：飞书上传说失败

**解决**：
```bash
# 重新完成 OAuth 授权
python3 ~/Desktop/DaMiShuSystem-main-backup/feishu_oauth_setup.py
```

---

## 📈 版本历史

### v1.0.0 (2026-02-10)

**初始功能**：
- ✅ 小红书自动采集
- ✅ 多平台链接处理
- ✅ 视频下载和转文字
- ✅ 每周自动分析
- ✅ 飞书上传集成

---

**创建时间**: 2026-02-10
**版本**: v1.0.0
**作者**: 大秘书系统

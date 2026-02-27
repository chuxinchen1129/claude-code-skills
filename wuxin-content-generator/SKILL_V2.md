---
name: wuxin-content-generator
description: 悟昕内容生成器 - 支持小红书图文、视频脚本、话题池生成。当用户提到"生成悟昕内容"、"悟昕脚本"、"视频脚本"、"话题池"、"常规投放"时使用。
version: 2.0.0
created: 2026-02-25
updated: 2026-02-26
---

# 悟昕内容生成器 Skill v2.0

## 功能概览

本技能整合3大内容生成能力：

| 模式 | 功能 | 输入 | 输出 |
|------|------|------|------|
| **图文模式** | 小红书科普图文 | 主题关键词 | 标题+正文+标签 |
| **脚本模式** | 30秒视频脚本 | 话题/场景 | Excel脚本表 |
| **话题池模式** | 话题裂变+评分 | 营销节点 | 候选选题→Top选题 |

---

## 使用场景

### 场景1：完整流程（推荐）⭐

**用户说**：
- "生成常规投放脚本"
- "悟昕日常推广内容"
- "生成Top18视频脚本"

**自动执行**：
```
1. 话题池生成（50个候选选题）
   ↓
2. 话题评分筛选（Top18）
   ↓
3. 脚本生成（标准格式）
   ↓
4. Excel输出
```

**输出**：`常规投放_Top18脚本_YYYY-MM-DD.xlsx`

### 场景2：单步执行

**用户说**：
- "生成话题池：常规投放，10个基础选题"
- "评分筛选：常规投放_话题池.xlsx"
- "生成脚本：使用场景+午休场景"

**仅执行指定步骤**

---

## 完整流程参数

### 必填参数

| 参数 | 说明 | 示例 |
|------|------|------|
| **营销节点** | 营销场景类型 | "常规投放"、"春节送礼"、"母亲节" |
| **基础选题数** | 基础选题数量 | 默认10个 |
| **裂变维度数** | 每个选题裂变数 | 默认5个 |
| **目标数量** | 最终筛选数量 | 默认18个 |

### 可选参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| **场景类型** | 场景分类 | 使用场景/情感场景/科普场景 |
| **品牌植入** | 品牌植入程度 | 超软性植入 |
| **及格分数线** | 评分及格线 | 25分 |
| **爆款导向** | 优先钩子+情感 | 是 |

---

## 子命令说明

### 1. 话题池生成

**触发词**：
- "生成话题池"
- "话题池生成"
- "选题裂变"

**参数**：
```bash
python src/main.py topic-pool \
  --node "常规投放" \
  --base-topics 10 \
  --fission 5 \
  --scenes "使用场景,情感场景,科普场景"
```

**输出**：
- `常规投放_话题池.json`
- `常规投放_话题池.xlsx`

### 2. 话题评分

**触发词**：
- "评分筛选"
- "话题评分"
- "筛选Top选题"

**参数**：
```bash
python src/main.py rate \
  --input "常规投放_话题池.xlsx" \
  --node "常规投放" \
  --target-count 18 \
  --passing-line 25 \
  --focus-viral
```

**输出**：
- `常规投放_选题评分.json`
- `常规投放_Top18选题.xlsx`

### 3. 脚本生成

**触发词**：
- "生成脚本"
- "视频脚本"
- "Top18脚本"

**参数**：
```bash
python src/main.py scripts \
  --input "常规投放_Top18选题.xlsx" \
  --brand-integration "soft" \
  --output-format "excel"
```

**输出**：
- `常规投放_Top18脚本_标准格式版.xlsx`
- `常规投放_Top18脚本_标准格式版.md`

### 4. 完整流程（一键执行）⭐

**触发词**：
- "生成常规投放脚本"
- "完整流程"
- "一键生成"

**参数**：
```bash
python src/main.py full-pipeline \
  --node "常规投放" \
  --base-topics 10 \
  --fission 5 \
  --target-count 18 \
  --brand-integration "soft" \
  --output "excel"
```

**输出**：
- `常规投放_话题池.xlsx`（候选选题）
- `常规投放_Top18选题.xlsx`（评分结果）
- `常规投放_Top18脚本_标准格式版.xlsx`（最终脚本）

---

## CLI 使用示例

### 快速开始（完整流程）

```bash
cd ~/Desktop/DMS/skills/wuxin-content-generator

# 一键生成常规投放脚本
python src/main.py full-pipeline \
  --node "常规投放" \
  --target-count 18
```

### 分步执行

```bash
# 步骤1: 生成话题池
python src/main.py topic-pool --node "常规投放"

# 步骤2: 评分筛选
python src/main.py rate \
  --input "output/常规投放_话题池.xlsx" \
  --target-count 18

# 步骤3: 生成脚本
python src/main.py scripts \
  --input "output/常规投放_Top18选题.xlsx"
```

---

## 文件结构

```
wuxin-content-generator/
├── SKILL.md              # 本文档
├── src/
│   ├── main.py           # CLI 入口（argparse）
│   ├── prompts.py        # Prompt 模板
│   ├── topic_pool.py     # 话题池生成模块
│   ├── topic_rater.py    # 话题评分模块
│   └── script_gen.py     # 脚本生成模块
├── assets/               # 品牌资产软链接
│   └── 03_WUXIN_CONTENT/ → ~/Desktop/DMS/03_WUXIN_CONTENT/
├── references/           # 参考文档
│   ├── video_script_structure.md
│   └── brand_assets.md
├── output/               # 输出目录
└── config.yaml           # 配置文件
```

---

## 配置文件

**config.yaml**：
```yaml
# 品牌资产路径
brand_assets:
  selling_points: "../03_WUXIN_CONTENT/assets/悟昕资产库/悟昕睡眠仪-ToC卖点库.md"
  knowledge_base: "../03_WUXIN_CONTENT/assets/悟昕资产库/悟昕科技知识库.md"
  marketing_calendar: "../03_WUXIN_CONTENT/00_Strategy_Planning/marketing_calendar.csv"

# 输出路径
output_dir: "./output"

# 默认参数
defaults:
  base_topics: 10
  fission_per_topic: 5
  target_count: 18
  passing_line: 25
  brand_integration: "soft"
```

---

## 依赖

```
pandas
openpyxl
pyyaml
jinja2
```

---

## 更新日志

### v2.0.0 (2026-02-26)
- ✅ 整合话题池生成功能
- ✅ 整合话题评分功能
- ✅ 新增视频脚本生成功能
- ✅ 支持完整流程一键执行
- ✅ 支持分步单模块执行
- ✅ 最终输出Excel格式

### v1.0.0 (2026-02-25)
- 初始版本：小红书图文生成

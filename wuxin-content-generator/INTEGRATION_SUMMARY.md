# 悟昕内容生成器 - 3技能整合方案

> **版本**：v2.0
> **创建时间**：2026-02-26
> **状态**：已完成

---

## 整合概述

将3个独立技能整合为一个统一的内容生成器：

| 原技能 | 功能 | 整合后 |
|--------|------|--------|
| wuxin-topic-pool-generator | 话题池生成 | src/topic_pool.py |
| wuxin-topic-rater | 话题评分 | src/topic_rater.py |
| wuxin-content-generator | 内容生成 | src/script_gen.py |

---

## 文件结构

```
wuxin-content-generator/
├── SKILL.md              # 原版（小红书图文）
├── SKILL_V2.md           # 新版（整合版）⭐
├── src/
│   ├── main.py           # 原版（图文生成）
│   ├── main_v2.py        # 新版CLI入口 ⭐
│   ├── prompts.py        # Prompt模板
│   ├── topic_pool.py     # 话题池生成模块 ⭐
│   ├── topic_rater.py    # 话题评分模块 ⭐
│   └── script_gen.py     # 脚本生成模块 ⭐
├── assets/               # 品牌资产软链接
└── output/               # 输出目录
```

---

## 工作流程

### 完整流程（一键执行）

```
用户: "生成常规投放脚本"
  ↓
[步骤1] 生成话题池 (10基础 × 5裂变 = 50选题)
  ↓
[步骤2] 评分筛选 (6维度评分 → Top18)
  ↓
[步骤3] 脚本生成 (标准格式 Excel)
  ↓
输出: 常规投放_Top18脚本_标准格式版.xlsx
```

### 分步执行

```
# 步骤1: 生成话题池
python src/main_v2.py topic-pool --node "常规投放"

# 步骤2: 评分筛选
python src/main_v2.py rate \
  --input "常规投放_话题池.xlsx" \
  --target-count 18

# 步骤3: 生成脚本
python src/main_v2.py scripts \
  --input "常规投放_Top18选题.xlsx"
```

---

## CLI 命令

### 1. 完整流程（推荐）

```bash
python src/main_v2.py full-pipeline \
  --node "常规投放" \
  --target-count 18
```

**参数说明**：
- `--node`: 营销节点（必填）
- `--base-topics`: 基础选题数（默认10）
- `--fission`: 裂变维度数（默认5）
- `--target-count`: 最终筛选数（默认18）
- `--passing-line`: 及格分数线（默认25）
- `--focus-viral`: 优先爆款潜力
- `--brand-integration`: 品牌植入程度（soft/medium/hard）

### 2. 单步命令

```bash
# 话题池生成
python src/main_v2.py topic-pool \
  --node "常规投放" \
  --base-topics 10 \
  --fission 5

# 话题评分
python src/main_v2.py rate \
  --input "常规投放_话题池.xlsx" \
  --target-count 18 \
  --passing-line 25

# 脚本生成
python src/main_v2.py scripts \
  --input "常规投放_Top18选题.xlsx" \
  --brand-integration soft
```

---

## 自然语言触发

### 触发词

用户说以下词语时，AI自动调用完整流程：

- "生成常规投放脚本"
- "悟昕日常推广内容"
- "生成Top18视频脚本"
- "悟昕话题池生成"

### AI 执行流程

1. **理解意图**：识别为常规投放脚本生成任务
2. **收集参数**：确认营销节点、目标数量等
3. **执行流程**：
   - 生成话题池（50个候选）
   - 评分筛选（Top18）
   - 脚本生成（标准格式）
4. **输出结果**：Excel + Markdown

---

## 模块说明

### topic_pool.py - 话题池生成

**功能**：基于基础选题，通过5维度裂变生成候选话题池

**核心函数**：
```python
generate_topic_pool(node, base_topics_count, fission_per_topic)
```

**5大裂变维度**：
1. 场景显微镜 - 画面细节放大
2. 认知粉碎机 - 科学概念冲击
3. 情绪共振器 - 第一人称代入
4. 剧情反转器 - 意外转折
5. 社交话题器 - 讨论传播

### topic_rater.py - 话题评分

**功能**：6维度评分系统，筛选高质量选题

**核心函数**：
```python
rate_all_topics(topics, node, target_count, passing_line, focus_viral)
```

**6大评分维度**：
1. 营销节点关联度 ⭐⭐⭐
2. 场景多样化 ⭐⭐
3. 钩子强度 ⭐⭐
4. 情感共鸣 ⭐
5. 品牌一致性 ⭐
6. 数据支撑 ⭐

**评分规则**：
- 总分满分：30分
- 及格线：25分（严格）
- 优秀：25-30分

### script_gen.py - 脚本生成

**功能**：基于评分后的选题生成30秒视频脚本

**核心函数**：
```python
generate_scripts_from_topics(topics, brand_integration)
```

**脚本格式**（12列标准格式）：
1. 序号
2. 场景分类
3. 目标人群
4. 封面大字
5. 发布标题
6. 发布文案
7. 纯文本旁白
8. 旁白字数
9. 0-3s黄金钩子
10. 3-10s痛点深挖
11. 10-20s原理展现
12. 20-30s爽感结尾

**品牌植入策略**（超软性）：
- 台词不提名"悟昕"、"睡眠仪"
- 前20秒不出现产品画面
- 聚焦睡眠问题，不讲产品功能
- CTA用"搜XXX"而非"搜悟昕"

---

## 输出文件

### 话题池输出

- `常规投放_话题池.json` - 完整JSON格式
- `常规投放_话题池.xlsx` - Excel格式（50行）

### 评分输出

- `常规投放_选题评分.json` - 完整评分数据
- `常规投放_Top18选题.xlsx` - 推荐选题（18行）

### 脚本输出

- `常规投放_Top18脚本_标准格式版.xlsx` - 最终脚本（18行×12列）
- `常规投放_Top18脚本_标准格式版.md` - Markdown版本

---

## 配置文件

**config.yaml**（可选）：

```yaml
# 品牌资产路径
brand_assets:
  selling_points: "../03_WUXIN_CONTENT/assets/悟昕资产库/悟昕睡眠仪-ToC卖点库.md"
  knowledge_base: "../03_WUXIN_CONTENT/assets/悟昕资产库/悟昕科技知识库.md"

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

## 测试

### 测试完整流程

```bash
cd ~/Desktop/DMS/skills/wuxin-content-generator

python src/main_v2.py full-pipeline \
  --node "常规投放" \
  --target-count 18 \
  --output "./output"
```

### 测试单步流程

```bash
# 测试话题池生成
python src/topic_pool.py

# 测试话题评分
python src/topic_rater.py

# 测试脚本生成
python src/script_gen.py
```

---

## 下一步优化

1. **配置文件支持**：读取config.yaml加载参数
2. **品牌资产集成**：链接到悟昕资产库
3. **AI模型调用**：集成ZhipuAI生成更高质量内容
4. **飞书自动上传**：生成后自动上传到飞书
5. **进度可视化**：添加tqdm进度条

---

**整合完成！现在可以一键生成从话题池到脚本的完整流程。**

---
name: wuxin-pr-article
description: |
  悟昕公关文章生成器。当用户提到：
  - "生成公关文章"、"品牌软文"、"媒体稿件"
  - "悟昕公关"、"PR文章"、"软文"
  - "品牌推广文章"、"官方媒体稿件"

  支持：品牌背书、行业洞察、用户故事、正式公文风格
version: 1.0.0
created: 2026-02-26
updated: 2026-02-26
---

# 悟昕公关文章生成器

**技能名称**：wuxin-pr-article

**用途**：基于悟昕品牌资产生成正式公关文章和软文

---

## 功能概览

| 功能 | 输入 | 输出 |
|------|------|------|
| **品牌背书文** | 品牌信息+权威背书 | Markdown正式公文 |
| **行业洞察文** | 行业趋势+品牌定位 | 深度分析文章 |
| **用户故事文** | 用户案例+品牌价值 | 故事化软文 |
| **媒体稿件** | 新闻事件+品牌角度 | 通用新闻稿 |

---

## 使用场景

### 场景1：品牌背书文

**用户说**：
- "生成一篇品牌背书文章"
- "写悟昕的品牌介绍"

**自动执行**：
```
1. 读取品牌档案
2. 整合核心卖点
3. 应用正式公文语气
4. 生成Markdown输出
```

### 场景2：行业洞察文

**用户说**：
- "写一篇睡眠行业的深度分析"
- "生成睡眠科技趋势文章"

### 场景3：用户故事文

**用户说**：
- "写一个用户使用悟昕的成功案例"
- "生成用户证言文章"

---

## CLI 命令

```bash
# 生成品牌背书文
python src/main.py brand-story --tone formal

# 生成行业洞察文
python src/main.py industry-insight --topic "睡眠科技趋势"

# 生成用户故事文
python src/main.py user-story --audience "职场人士"
```

---

## 输出格式

### Markdown 结构

```markdown
# 文章标题

> 副标题/导语

## 背景介绍
行业背景 + 品牌定位

## 核心价值
品牌核心卖点 + 科学依据

## 用户案例/数据支撑
真实案例 + 权威数据

## 品牌愿景
未来展望 + 品牌使命
```

---

## 内容风格

### 语气要求
- **正式专业**：符合媒体发布标准
- **客观中立**：以第三方视角叙述
- **权威可信**：数据支撑、专家背书

### 禁用词汇
- 夸张宣传词汇
- 绝对化表述
- 过于口语化表达

---

## 配置

**共享配置**：`03_WUXIN_CONTENT/assets/config.yaml`

**本地配置**：`config.yaml`
```yaml
# 引用共享配置
include: ../../03_WUXIN_CONTENT/assets/config.yaml

# 技能特定配置
defaults:
  tone: formal                      # 语气: formal/professional
  length: medium                    # 长度: short/medium/long
  brand_integration: explicit       # 品牌植入: explicit/balanced
```

---

## 依赖资源

| 资源类型 | 路径 |
|---------|------|
| 品牌档案 | `03_WUXIN_CONTENT/assets/brand/` |
| 卖点库 | `03_WUXIN_CONTENT/assets/brand/selling-points.md` |
| 知识库 | `03_WUXIN_CONTENT/assets/brand/knowledge-base.md` |
| PR模板 | `03_WUXIN_CONTENT/assets/templates/pr-article/` |

---

## 内容风格 ⭐ NEW

生成内容后，**自动调用** `writing-style-standardizer` 进行风格统一：

```yaml
风格模式: 品牌推广风格
品牌调性: 悟昕（科学循证 + 温暖治愈 + 优雅克制）
检查级别: 基础
```

**核心要求**：
- ✅ 标题：15-25字，痛点+解决方案暗示式
- ✅ 开篇：场景化引入，避免无效铺垫
- ✅ 段落：简洁有力，每段聚焦一个核心观点
- ✅ 数据：引用权威来源、支撑数据
- ✅ 禁止词：绝绝子、神级、根治、第一等

**品牌植入原则**：
- 超软性："搜「睡眠管理」试试看" 而非 "立即购买"
- 一次一处：不要堆砌卖点
- 场景化：在解决方案中自然呈现

---

## 相关文档

- **风格标准化器**：`skills/writing-style-standardizer/SKILL.md`
- PR文章模板：`03_WUXIN_CONTENT/assets/templates/pr-article/公关文章模板.md`
- 品牌档案：`03_WUXIN_CONTENT/assets/悟昕资产库/01-品牌档案/`

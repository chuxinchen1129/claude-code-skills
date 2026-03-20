---
name: wuxin-wechat-article
description: |
  悟昕公众号文章生成器。当用户提到：
  - "生成公众号文章"、"微信推文"、"长文"
  - "悟昕公众号"、"公众号内容"
  - "深度文章"、"睡眠科普长文"

  支持：长文深度、讲故事逻辑、Markdown输出、品牌植入
version: 1.0.0
created: 2026-02-26
updated: 2026-02-26
---

# 悟昕公众号文章生成器

**技能名称**：wuxin-wechat-article

**用途**：基于睡眠科学 Wiki 生成公众号深度文章

---

## 功能概览

| 功能 | 输入 | 输出 |
|------|------|------|
| **科普长文** | 主题+深度 | 2000字深度文章 |
| **故事型文章** | 场景+人物 | 叙事性长文 |
| **问答型文章** | 问题+解答 | Q&A结构文章 |
| **清单型文章** | 主题+要点 | 结构化清单文 |

---

## 使用场景

### 场景1：科普长文

**用户说**：
- "生成一篇关于深睡的公众号文章"
- "写睡眠科学的深度科普"

**自动执行**：
```
1. 选择科学主题
2. 构建文章结构（引入-展开-收尾）
3. 整合科学依据和品牌卖点
4. 生成2000字长文
```

### 场景2：故事型文章

**用户说**：
- "写一个失眠治愈故事"
- "生成用户改变经历文章"

### 场景3：清单型文章

**用户说**：
- "生成10个睡眠建议清单"
- "写睡眠误区科普清单"

---

## CLI 命令

```bash
# 生成科普长文
python src/main.py science-article --topic "深睡" --depth 2000

# 生成故事型文章
python src/main.py story-article --scene "失眠" --persona "职场妈妈"

# 生成清单型文章
python src/main.py list-article --topic "睡眠误区" --count 10

# Markdown 转 HTML（悟昕品牌样式）
python src/html_formatter.py input.md -o output.html
```

---

## HTML 格式化 ⭐

> **推荐使用统一排版工具**：
> 对于 Markdown 转 HTML 排版，推荐使用 **`wechat-formatter`** skill，它支持：
> - 自动检测文章类型（悟昕/宠商圈）
> - 统一的品牌样式管理
> - 更好的维护性
>
> 使用方法：
> ```
> python ~/.claude/skills/wechat-formatter/scripts/format.py input.md -o output.html -t wuxin
> ```
>
> 本项目的 `html_formatter.py` 仍可继续使用。

### 悟昕品牌样式

**样式规范文档**：`03_WUXIN_CONTENT/assets/templates/wuxin-html-style.md`

**品牌调色盘**：
| 用途 | 色值 |
|------|------|
| 品牌紫 | `#7C5DFA` |
| 正文色 | `#4A5568` |
| 边框色 | `#E2E8F0` |

**标志性元素**：
- **巨型序号**：56px Georgia 斜体，#7C5DFA
- **双边框标题**：1px淡灰上边框 + 3px品牌紫下边框
- **关键词强调**：#7C5DFA 加粗显示

### 格式化命令

```bash
# Markdown 转 HTML
python src/html_formatter.py input.md -o output.html

# 不添加 END 结尾标识
python src/html_formatter.py input.md -o output.html --no-end
```

### HTML 特性

✅ **100% 内联 CSS** - 符合微信后台要求
✅ **全平台兼容** - iOS、Android、PC 完美适配
✅ **悟昕品牌色** - 自动应用 #7C5DFA 紫色系
✅ **标志性小标题** - 01, 02, 03... 悬浮序号样式

---

## 输出格式

### Markdown 结构（长文）

```markdown
# 文章标题

> 导语/引言

## 第一部分：引入话题
- 个人故事/社会现象
- 提出核心问题

## 第二部分：知识展开
- 科学原理
- 权威数据
- 专家观点

## 第三部分：解决方案
- 实用建议
- 品牌价值融入
- 行动指南

## 第四部分：总结升华
- 金句收尾
- 引导互动

---
*排版说明、参考文献*
```

---

## 内容风格

### 语气要求
- **温暖治愈**：像朋友聊天一样亲切
- **专业可信**：科学依据支撑观点
- **故事驱动**：用故事传递价值

### 公众号特性
- **排版友好**：分段清晰，易读性强
- **视觉元素**：标题、引用、列表丰富
- **互动引导**：结尾引导关注/点赞/转发

---

## 配置

**共享配置**：`03_WUXIN_CONTENT/assets/config.yaml`

**本地配置**：`config.yaml`
```yaml
# 引用共享配置
include: ../../03_WUXIN_CONTENT/assets/config.yaml

# 技能特定配置
defaults:
  length: long                     # 长度: long=长文(2000字)
  style: narrative                 # 风格: narrative=叙事
  brand_integration: balanced      # 品牌植入: balanced=平衡
```

---

## 依赖资源

| 资源类型 | 路径 |
|---------|------|
| 睡眠科学 Wiki | `03_WUXIN_CONTENT/assets/wiki/` |
| 品牌资产 | `03_WUXIN_CONTENT/assets/brand/` |
| 公众号模板 | `03_WUXIN_CONTENT/assets/templates/wechat-article/` |
| **HTML样式规范** | `03_WUXIN_CONTENT/assets/templates/wuxin-html-style.md` |

---

## 风格控制 ⭐ NEW

生成内容后，**自动调用** `writing-style-standardizer` 进行风格统一：

```yaml
风格模式: 通用科普风格 / 品牌推广风格
品牌调性: 悟昕（科学循证 + 温暖治愈 + 优雅克制）
检查级别: 基础
```

**核心要求**：
- ✅ 标题：15-25字，疑问/亮点式
- ✅ 开篇：场景化引入，避免无效铺垫
- ✅ 段落：80-120字，空行分隔
- ✅ 数据：引用《睡眠健康调查报告》等权威来源
- ✅ 禁止词：绝绝子、神级、根治、第一等

**品牌植入原则**：
- 超软性："搜「睡眠管理」" 而非 "立即购买"
- 一次一处：不要堆砌卖点
- 场景化：在解决方案中自然呈现

---

## 相关文档

- **风格标准化器**：`skills/writing-style-standardizer/SKILL.md`
- **悟昕HTML样式规范**：`03_WUXIN_CONTENT/assets/templates/wuxin-html-style.md`
- 公众号文章模板：`03_WUXIN_CONTENT/assets/templates/wechat-article/`
- 睡眠科学 Wiki：`03_WUXIN_CONTENT/05_Sleep_Science_Wiki/`

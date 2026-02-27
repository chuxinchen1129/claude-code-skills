---
name: wuxin-content-suite
description: |
  悟昕内容生成套件 - 统一入口。当用户提到：
  - "悟昕内容"、"悟昕生成"、"Wuxin内容"
  - "视频脚本"、"科普图文"、"公关文章"、"公众号文章"
  - "睡眠内容"、"悟昕品牌内容"

  支持4种内容类型：视频脚本(30秒4段式)、科普图文(小红书)、公关文章(正式)、公众号文章(长文)
version: 1.0.0
created: 2026-02-26
updated: 2026-02-26
---

# 悟昕内容生成套件

**套件名称**：wuxin-content-suite

**用途**：悟昕品牌内容生成的统一入口，支持4种内容类型

---

## 支持的内容类型

| 内容类型 | 触发词 | 技能 | 输出格式 |
|---------|--------|------|---------|
| **视频脚本** | "视频脚本"、"30秒脚本"、"抖音脚本" | wuxin-script-generator | Excel (12列) |
| **科普图文** | "科普图文"、"小红书图文"、"笔记" | wuxin-xhs-content | CSV (13列) |
| **公关文章** | "公关文章"、"软文"、"媒体稿" | wuxin-pr-article | Markdown |
| **公众号文章** | "公众号文章"、"微信推文"、"长文" | wuxin-wechat-article | Markdown |

---

## 快速开始

### 方式一：直接调用子技能（推荐）

每个生成器都可以独立使用：

```bash
# 视频脚本生成器
cd skills/wuxin-script-generator
python src/main.py full-pipeline --node "常规投放" --target-count 18

# 科普图文生成器
cd skills/wuxin-xhs-content
python src/main.py batch --node "常规投放" --days 7

# 公关文章生成器
cd skills/wuxin-pr-article
python src/main.py brand-story

# 公众号文章生成器
cd skills/wuxin-wechat-article
python src/main.py science-article --topic "深睡"
```

### 方式二：使用套件统一入口

```bash
# 使用套件CLI（需要创建）
cd skills/wuxin-content-suite
python cli.py generate --type script --node "常规投放"
```

---

## 架构说明

### 三层共享模型

```
┌─────────────────────────────────────────────────────────────────┐
│                        Layer 1: 共享资源层                         │
│                  (03_WUXIN_CONTENT/assets/ 共享库)               │
├─────────────────────────────────────────────────────────────────┤
│  • 睡眠科学 Wiki (05_Sleep_Science_Wiki/)                       │
│  • 品牌资产库 (悟昕资产库/)                                      │
│  • 话题库 (02_话题库/)                                           │
│  • 创作指南 (03_创作指南/)                                       │
│  • 配置中心 (config.yaml)                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓ 引用
┌─────────────────────────────────────────────────────────────────┐
│                    Layer 2: 内容生成技能层                        │
│                     (skills/wuxin-*-*/)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │ 视频脚本生成器   │  │  科普图文生成器  │  │ 公关文章生成器 │  │
│  │ (script-gen)    │  │ (xhs-content)   │  │ (pr-article)   │  │
│  ├─────────────────┤  ├─────────────────┤  ├───────────────┤  │
│  │ • 30秒4段式      │  │ • intro+3板块   │  │ • 正式公文     │  │
│  │ • Excel输出     │  │ • CSV输出       │  │ • Markdown输出 │  │
│  │ • 超软植入       │  │ • 小红书风格     │  │ • 品牌背书     │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│                                                                     │
│  ┌─────────────────┐                                                │
│  │ 公众号推文生成器 │                                                │
│  │ (wechat-article)│                                                │
│  ├─────────────────┤                                                │
│  │ • 长文深度       │                                                │
│  │ • 讲故事逻辑     │                                                │
│  │ • Markdown输出 │                                                │
│  └─────────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Layer 3: 套件入口层                           │
│                  (skills/wuxin-content-suite/)                     │
├─────────────────────────────────────────────────────────────────┤
│  • 统一CLI (cli.py)                                               │
│  • 触发词路由 (SKILL.md)                                          │
│  • 使用指南 (references/)                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 共享资源

### 中心配置
- **路径**：`03_WUXIN_CONTENT/assets/config.yaml`
- **功能**：统一管理品牌规范、资源路径、默认参数

### 品牌资产
- **卖点库**：`03_WUXIN_CONTENT/assets/brand/selling-points.md`
- **知识库**：`03_WUXIN_CONTENT/assets/brand/knowledge-base.md`
- **视觉规范**：`03_WUXIN_CONTENT/assets/brand/visual-guide.md`

### 内容模板
- **视频脚本**：`03_WUXIN_CONTENT/assets/templates/video-script/`
- **小红书图文**：`03_WUXIN_CONTENT/assets/templates/xhs-content/`
- **公关文章**：`03_WUXIN_CONTENT/assets/templates/pr-article/`
- **公众号文章**：`03_WUXIN_CONTENT/assets/templates/wechat-article/`

---

## 使用场景

### 场景1：视频脚本生成

**你说**："生成18个常规投放的视频脚本"

**自动路由到**：wuxin-script-generator
```
1. 生成话题池（50个候选）
2. 评分筛选（Top18）
3. 生成脚本（30秒4段式）
4. 输出Excel
```

### 场景2：科普图文生成

**你说**："生成本周的小红书科普内容"

**自动路由到**：wuxin-xhs-content
```
1. 读取营销日历
2. 匹配科学概念
3. 生成内容（intro+3板块+CTA）
4. 输出CSV
```

### 场景3：公关文章生成

**你说**："写一篇悟昕品牌背书文章"

**自动路由到**：wuxin-pr-article
```
1. 读取品牌档案
2. 整合核心卖点
3. 生成正式公文
4. 输出Markdown
```

### 场景4：公众号文章生成

**你说**："写一篇关于深睡的公众号文章"

**自动路由到**：wuxin-wechat-article
```
1. 选择科学主题
2. 构建文章结构
3. 生成2000字长文
4. 输出Markdown
```

---

## 配置说明

### 共享品牌规范

所有生成器遵循统一的品牌规范：

**语气**：温暖治愈、科学循证、优雅克制

**禁用词汇**：家人们、绝绝子、根治、第一、必需

**核心卖点**：
- AI智能睡眠管理师
- 医疗级EEG脑电监测
- 监测-干预-反馈闭环
- FDA认证CES技术
- 80%医疗级准确率

---

## 相关文档

- **使用指南**：`references/使用指南.md`
- **架构设计**：`references/架构设计.md`
- **开发文档**：`references/开发文档.md`

---

## 子技能链接

- **视频脚本生成器**：`skills/wuxin-script-generator/SKILL.md`
- **科普图文生成器**：`skills/wuxin-xhs-content/SKILL.md`
- **公关文章生成器**：`skills/wuxin-pr-article/SKILL.md`
- **公众号文章生成器**：`skills/wuxin-wechat-article/SKILL.md`

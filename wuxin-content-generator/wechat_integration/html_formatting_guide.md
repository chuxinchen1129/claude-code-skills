# 微信公众号HTML排版指南

> **目的**: 为悟昕公众号文章提供专属HTML模板
> **集成技能**: baoyu-markdown-to-html

---

## 集成方式

### 技能路径
**baoyu-markdown-to-html**
- 位置：`~/.claude/skills/baoyu-markdown-to-html/SKILL.md`
- 功能：将Markdown转换为 styled HTML
- 支持：悟昕专属模板、代码高亮、数学公式、图表

### 使用流程

```
生成Markdown文章
    ↓
调用baoyu-markdown-to-html技能
    ↓
选择悟昕专属模板
    ↓
生成HTML文章
    ↓
调用baoyu-post-to-wechat技能发布
```

---

## 悟昕专属模板

### 模板特点
- **品牌色调**：悟昕品牌色（深蓝+绿色点缀）
- **排版风格**：简洁优雅、科学专业
- **字体设置**：正文16px、标题24-32px
- **间距设置**：行距1.8、段间距1.5em

### HTML结构示例

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文章标题</title>
    <style>
        /* 悟昕品牌样式 */
        :root {
            --wuxin-primary: #1a3a52; /* 深蓝 */
            --wuxin-accent: #4a9c6d; /* 绿色 */
            --wuxin-bg: #f8f9fa;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.8;
            color: #333;
            max-width: 680px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: var(--wuxin-primary);
            font-size: 32px;
            margin-bottom: 30px;
        }
        h2 {
            color: var(--wuxin-primary);
            font-size: 24px;
            margin-top: 40px;
            margin-bottom: 20px;
            border-bottom: 2px solid var(--wuxin-accent);
            padding-bottom: 10px;
        }
        p {
            margin-bottom: 1.5em;
        }
        .highlight {
            background: var(--wuxin-bg);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid var(--wuxin-accent);
        }
    </style>
</head>
<body>
    <!-- 文章内容 -->
</body>
</html>
```

---

## 发布集成

### 技能路径
**baoyu-post-to-wechat**
- 位置：`~/.claude/skills/baoyu-post-to-wechat/SKILL.md`
- 功能：发布内容到微信公众号
- 支持：API方式、浏览器CDP方式

### 发布方式

#### 方式一：API方式
```python
# 使用公众号API发布
from baoyu_post_to_wechat import post_article

post_article(
    title="文章标题",
    content=html_content,  # HTML格式
    author="悟昕睡眠Lab",
    digest="文章摘要"
)
```

#### 方式二：浏览器CDP
```python
# 使用浏览器自动化发布
from baoyu_post_to_wechat import post_via_browser

post_via_browser(
    html_file="article.html",
    account="悟昕睡眠Lab"
)
```

---

## 完整工作流

### 1. 生成内容
```
用户指定平台和日期/主题
    ↓
询问场景："想要切入什么场景？"
    ↓
生成Markdown文章（2000-3000字）
```

### 2. 排版转换
```
调用baoyu-markdown-to-html技能
    ↓
选择悟昕专属模板
    ↓
生成HTML文章
```

### 3. 发布
```
调用baoyu-post-to-wechat技能
    ↓
选择发布方式（API/浏览器）
    ↓
发布到公众号
```

---

## 悟昕公众号配置

### 公众号信息
- **名称**：悟昕睡眠Lab
- **类型**：服务号
- **认证**：已认证

### 文章规范
- **字数**：2000-3000字
- **标题**：20字以内
- **摘要**：50字以内
- **封面**：900*500px，16:9

### 排版要求
- **正文**：16px
- **标题**：24-32px
- **行距**：1.8
- **段间距**：1.5em
- **页边距**：20px

---

## 常用HTML元素

### 章节标题
```html
<h2>章节标题</h2>
```

### 重点强调
```html
<div class="highlight">
    重点内容
</div>
```

### 数据展示
```html
<div class="data-box">
    <span class="data-number">80%</span>
    <span class="data-label">医疗级准确率</span>
</div>
```

### 引用
```html
<blockquote>
    引用内容
</blockquote>
```

---

**更新时间**: 2026-02-10
**集成技能**: baoyu-markdown-to-html, baoyu-post-to-wechat

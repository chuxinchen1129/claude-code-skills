# HTML 排版规范指南

> **创建时间**: 2026-02-02
> **版本**: v1.0
> **用途**: 确保不同类型文章的 HTML 排版风格一致

---

## 排版类型判断

**首先判断文章类型**：

| 文章类型 | 排版风格 |
|---------|---------|
| **宠商圈周报** | 完整边框排版（带卡片、边框、背景） |
| **其他所有文章** | 简洁排版（无边框、渐变标题仅01/02/03、橙色副标题） |

---

## 类型一：宠商圈周报排版

### 适用场景
- 文章标题包含"周报"
- 文章标题包含"宠商圈"
- 用户明确说明是"宠商圈周报"

### 排版规范

#### 整体容器
```html
<div class="weekly-report">
  <!-- 文章内容 -->
</div>
```

#### 标题层级

**01/02/03 主标题** - 渐变背景 + 白色文字
```html
<div class="section-title gradient-bg">
  <h2>01 标题文字</h2>
</div>
```

**副标题** - 橙色 + 左边框
```html
<h3 class="subsection-title">副标题文字</h3>
```

**三级标题** - 橙色 + 无边框
```html
<h4 class="tertiary-title">三级标题</h4>
```

#### 内容卡片
```html
<div class="content-card">
  <p>卡片内容</p>
</div>
```

#### 数据展示卡片
```html
<div class="data-card">
  <div class="data-number">123</div>
  <div class="data-label">数据说明</div>
</div>
```

#### 重点信息框
```html
<div class="highlight-box">
  <div class="box-icon">💡</div>
  <div class="box-content">重点信息内容</div>
</div>
```

---

## 类型二：普通文章排版（默认）⭐

### 适用场景
- 所有非"宠商圈周报"的文章
- 包括：商业分析、科普文章、品牌故事、公关软文等

### 排版规范

#### 整体容器
```html
<div class="article-content">
  <!-- 文章内容，无边框 -->
</div>
```

#### 标题层级

**01/02/03 主标题** - 渐变背景 + 白色文字（唯一使用渐变的标题）
```html
<div class="section-title gradient-bg">
  <h2>01 标题文字</h2>
</div>
```

**其他层级标题** - 橙色加粗，无边框、无背景
```html
<!-- 四级标题 -->
<h4 style="color: #FF6B35; font-weight: bold; margin-top: 1.5em;">小标题文字</h4>

<!-- 五级标题 -->
<h5 style="color: #FF6B35; font-weight: bold; margin-top: 1em;">小小标题</h5>
```

#### 正文段落
```html
<p style="line-height: 1.8; margin-bottom: 1em;">正文内容...</p>
```

#### 重点文字
```html
<!-- 强调文字 -->
<span style="color: #FF6B35; font-weight: bold;">重点内容</span>

<!-- 引用文字（无边框） -->
<blockquote style="border-left: 3px solid #FF6B35; padding-left: 1em; margin: 1.5em 0; color: #666;">
  引用内容
</blockquote>
```

#### 数据展示（无边框）
```html
<div style="display: flex; align-items: center; gap: 0.5em; margin: 1em 0;">
  <span style="font-size: 1.5em; color: #FF6B35; font-weight: bold;">123</span>
  <span style="color: #666;">数据说明</span>
</div>
```

#### 列表
```html
<!-- 无序列表 -->
<ul style="list-style: disc; padding-left: 1.5em; margin: 1em 0;">
  <li style="margin-bottom: 0.5em;">列表项</li>
</ul>

<!-- 有序列表 -->
<ol style="list-style: decimal; padding-left: 1.5em; margin: 1em 0;">
  <li style="margin-bottom: 0.5em;">列表项</li>
</ol>
```

---

## 完整对比示例

### 宠商圈周报完整示例

```html
<!DOCTYPE html>
<html>
<head>
<style>
  .weekly-report {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }

  .section-title {
    padding: 15px 20px;
    border-radius: 8px;
    margin: 30px 0 20px;
  }

  .gradient-bg {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }

  .subsection-title {
    color: #FF6B35;
    font-size: 1.3em;
    font-weight: bold;
    border-left: 4px solid #FF6B35;
    padding-left: 12px;
    margin: 25px 0 15px;
  }

  .content-card {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 20px;
    margin: 15px 0;
  }

  .data-card {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    margin: 10px 0;
  }

  .data-number {
    font-size: 2em;
    font-weight: bold;
    color: #667eea;
  }

  .highlight-box {
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
    padding: 15px;
    display: flex;
    gap: 10px;
    margin: 15px 0;
  }
</style>
</head>
<body>
<div class="weekly-report">
  <div class="section-title gradient-bg">
    <h2>01 本周数据概览</h2>
  </div>

  <h3 class="subsection-title">整体趋势</h3>

  <div class="content-card">
    <p>本周宠物行业整体表现稳定...</p>
  </div>

  <div class="data-card">
    <div class="data-number">+15.3%</div>
    <div class="data-label">环比增长</div>
  </div>
</div>
</body>
</html>
```

### 普通文章完整示例

```html
<!DOCTYPE html>
<html>
<head>
<style>
  .article-content {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    line-height: 1.8;
  }

  .section-title {
    padding: 15px 20px;
    border-radius: 8px;
    margin: 30px 0 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .section-title h2 {
    color: white;
    margin: 0;
  }

  p {
    margin-bottom: 1em;
    color: #333;
  }
</style>
</head>
<body>
<div class="article-content">
  <h1 style="text-align: center;">文章标题</h1>

  <div class="section-title">
    <h2>01 第一部分标题</h2>
  </div>

  <p>正文段落内容...</p>

  <h4 style="color: #FF6B35; font-weight: bold; margin-top: 1.5em;">小标题</h4>

  <p>更多正文内容...</p>

  <div style="display: flex; align-items: center; gap: 0.5em; margin: 1em 0;">
    <span style="font-size: 1.5em; color: #FF6B35; font-weight: bold;">10%</span>
    <span style="color: #666;">增长率</span>
  </div>

  <div class="section-title">
    <h2>02 第二部分标题</h2>
  </div>

  <!-- 更多内容... -->
</div>
</body>
</html>
```

---

## 快速检查清单

### 排版前

- [ ] 确认文章类型（宠商圈周报 vs 普通文章）

### 宠商圈周报

- [ ] 使用 `.weekly-report` 容器
- [ ] 01/02/03 标题使用渐变背景
- [ ] 副标题有左边框
- [ ] 内容卡片有边框和背景
- [ ] 数据卡片有独立样式

### 普通文章

- [ ] 使用 `.article-content` 容器
- [ ] 01/02/03 标题使用渐变背景（仅这些）
- [ ] 其他标题只用橙色加粗，无边框、无背景
- [ ] 正文无边框
- [ ] 数据展示简洁样式

---

## 颜色规范

| 用途 | 颜色值 | 使用场景 |
|-----|-------|---------|
| 渐变背景 | `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` | 01/02/03 主标题 |
| 橙色 | `#FF6B35` | 副标题、重点文字 |
| 正文 | `#333` | 正文文字 |
| 次要文字 | `#666` | 引用、说明文字 |
| 边框 | `#dee2e6` | 周报卡片边框 |
| 卡片背景 | `#f8f9fa` | 周报内容卡片 |

---

## 常见问题

### Q1: 如何判断文章类型？

**A**: 检查文章标题或用户说明：
- 标题包含"周报"+"宠商圈" → 宠商圈周报
- 用户明确说明"这是宠商圈周报" → 宠商圈周报
- 其他情况 → 普通文章

### Q2: 普通文章可以用边框吗？

**A**: 不可以。普通文章的正文不要使用任何边框卡片样式，保持简洁。

### Q3: 哪些标题可以使用渐变背景？

**A**: 只有 01/02/03 编号的主标题使用渐变背景。其他所有标题（四级、五级等）只用橙色加粗。

---

**最后更新**: 2026-02-02
**版本**: v1.0

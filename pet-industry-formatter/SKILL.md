# 宠商圈HTML排版Skill

> **版本**: v1.0
> **创建时间**: 2026-02-08
> **用途**: 专门为宠商圈行业文章提供HTML排版服务

---

## 技能描述

这是一个专门为宠商圈行业文章设计的HTML排版技能。它能够将Markdown格式的宠物行业文章转换为精美的HTML格式，适合在行业媒体、商业媒体和新媒体平台发布。

**已验证模板**: 基于《这个春节,宠物不再是"旁观者"——2026人宠共融生活图鉴》的实际排版代码。

---

## 核心特性

### 1. 专业排版风格
- 适合行业分析文章的排版样式
- 数据、案例、洞察分区分块展示
- 渐变色背景增强视觉效果
- 移动端适配优化

### 2. 特色区块样式
- **编者按区块** (`.intro`): 灰色背景 #f8f9fa + 红色左边框 #e74c3c
- **数据区块** (`.data-box`): 黄色背景 #fff3cd + 金色左边框 #ffc107
- **案例区块** (`.case-box`): 蓝色背景 #e7f3ff + 蓝色左边框 #2196F3
- **洞察区块** (`.insight-box`): 紫色背景 #f3e5f5 + 紫色左边框 #9C27B0
- **结语区块** (`.conclusion`): 渐变紫色背景 + 白色文字

### 3. 响应式设计
- 移动端字体和间距优化
- 图片自适应尺寸
- 标题层级清晰

---

## 使用方法

### 基本用法

```
用户: "帮我排版这篇宠文章"
或
用户: "把这篇文章转换成HTML格式"
```

### 技能会自动执行以下步骤:

1. **读取文章内容**
   - 支持Markdown格式
   - 支持纯文本格式

2. **智能识别内容结构**
   - 标题层级 (H1, H2, H3)
   - 数据区块
   - 案例区块
   - 洞察/观点区块
   - 编者按/引言
   - 结语

3. **应用专业样式**
   - 根据内容类型应用不同样式
   - 保持视觉一致性
   - 优化阅读体验

4. **生成HTML文件**
   - 保存到桌面或指定位置
   - 文件名自动生成
   - 包含完整CSS样式

---

## 完整HTML模板 (已验证)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[文章标题]</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.8;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-size: 17px;
        }
        h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 30px;
            line-height: 1.4;
            color: #1a1a1a;
        }
        h2 {
            font-size: 22px;
            font-weight: 600;
            margin-top: 40px;
            margin-bottom: 20px;
            line-height: 1.4;
            color: #2c3e50;
        }
        p {
            margin-bottom: 20px;
            text-align: justify;
        }
        .intro {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #e74c3c;
        }
        .highlight {
            background: linear-gradient(120deg, #a8e6cf 0%, #dcedc1 100%);
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 500;
        }
        .data-box {
            background: #fff3cd;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 25px 0;
            border-left: 4px solid #ffc107;
        }
        .case-box {
            background: #e7f3ff;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 25px 0;
            border-left: 4px solid #2196F3;
        }
        .insight-box {
            background: #f3e5f5;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 25px 0;
            border-left: 4px solid #9C27B0;
        }
        .conclusion {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin-top: 40px;
        }
        .conclusion h2 {
            color: white;
            margin-top: 0;
        }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 25px 0;
        }
        .caption {
            font-size: 14px;
            color: #666;
            text-align: center;
            margin-top: -15px;
            margin-bottom: 25px;
            font-style: italic;
        }
        @media (max-width: 600px) {
            body {
                padding: 15px;
                font-size: 16px;
            }
            h1 {
                font-size: 24px;
            }
            h2 {
                font-size: 20px;
            }
        }
    </style>
</head>
<body>
    <h1>[文章标题]</h1>

    <div class="intro">
        <p><strong>编者按：</strong>[编者按内容]</p>
    </div>

    <h2>[章节标题]</h2>

    <p>[正文内容]</p>

    <div class="data-box">
        <p><strong>[数据标题]：</strong></p>
        <ul>
            <li>[数据点1] <span class="highlight">[关键数字]</span></li>
            <li>[数据点2]</li>
        </ul>
    </div>

    <div class="case-box">
        <p><strong>【案例】[案例标题]</strong></p>
        <p>[案例内容]</p>
    </div>

    <div class="insight-box">
        <p><strong>【洞察】[洞察标题]</strong></p>
        <p>[洞察内容]</p>
    </div>

    <div class="conclusion">
        <h2>结语</h2>
        <p>[结语内容]</p>
    </div>

    <hr style="margin: 40px 0; border: none; border-top: 1px solid #eee;">

    <p style="font-size: 14px; color: #999; text-align: center;">
        <strong>数据来源：</strong>[数据来源说明]
    </p>
</body>
</html>
```

---

## 内容识别规则

### 编者按/引言区块 (`.intro`)
识别特征:
- 包含"编者按"、"引言"、"开篇"等关键词
- 文章开头的背景说明

**示例**:
```html
<div class="intro">
    <p><strong>编者按：</strong>2026年春节,一个明显的趋势正在形成...</p>
</div>
```

### 数据区块 (`.data-box`)
识别特征:
- 包含具体数字和百分比
- 标注数据来源
- "数据显示"、"数据表明"等关键词

**示例**:
```html
<div class="data-box">
    <p><strong>数据印证了这个变化：</strong></p>
    <ul>
        <li>2025年,市场规模达到<span class="highlight">3126亿元</span></li>
        <li>搜索量涨了<span class="highlight">10倍多</span></li>
        <li>订单增长<span class="highlight">29%</span></li>
    </ul>
</div>
```

### 案例区块 (`.case-box`)
识别特征:
- 包含公司名称、产品名称
- "案例"、"例如"等关键词
- 具体场景描述

**示例**:
```html
<div class="case-box">
    <p><strong>【案例】盒马推出宠物年夜饭礼盒</strong></p>
    <p>盒马首次推出宠物年夜饭礼盒,里面有佛跳墙...</p>
</div>
```

### 洞察/观点区块 (`.insight-box`)
识别特征:
- "洞察"、"分析"、"认为"等关键词
- 总结性观点
- 深度解读内容

**示例**:
```html
<div class="insight-box">
    <p><strong>【洞察】宠物社交化趋势</strong></p>
    <p>这种变化背后是宠物社交化趋势...</p>
</div>
```

### 结语区块 (`.conclusion`)
识别特征:
- "结语"、"总结"、"最后"等关键词
- 文章结尾的总结部分

**示例**:
```html
<div class="conclusion">
    <h2>结语</h2>
    <p>2026年的春节,宠物不再是"旁观者"。</p>
    <p>从年夜饭到拜年...</p>
</div>
```

---

## 样式规范

### 颜色方案

| 区块类型 | CSS类 | 背景色 | 边框色 | 用途 |
|---------|-------|--------|--------|------|
| 编者按 | `.intro` | #f8f9fa | #e74c3c (红) | 引言说明 |
| 数据 | `.data-box` | #fff3cd | #ffc107 (金) | 数据展示 |
| 案例 | `.case-box` | #e7f3ff | #2196F3 (蓝) | 案例说明 |
| 洞察 | `.insight-box` | #f3e5f5 | #9C27B0 (紫) | 观点洞察 |
| 结语 | `.conclusion` | 渐变紫 | 无 | 总结收尾 |

### 字体规范

- **中文字体**: PingFang SC, Hiragino Sans GB, Microsoft YaHei
- **英文字体**: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue
- **正文字号**: 17px (移动端 16px)
- **标题字号**: H1: 28px (24px), H2: 22px (20px)
- **行高**: 1.8

### 高亮样式

使用 `.highlight` 类来突出关键数字：

```html
<span class="highlight">3126亿元</span>
```

效果：渐变绿色背景 + 圆角

---

## 输出规范

### 文件命名规则
```
[文章标题]_最终版.html
```

示例:
```
这个春节,宠物不再是旁观者_最终版.html
```

### 输出位置
默认保存到桌面: `~/Desktop/`

用户可指定保存路径。

---

## 与写作Agent的配合

当写作Agent完成宠商圈文章创作后，此skill会自动被调用:

1. **写作Agent** 完成初稿
2. **写作Agent** 进行三轮审校
3. **写作Agent** 调用 **pet-industry-formatter** skill
4. **排版Skill** 生成精美HTML
5. **写作Agent** 交付最终成果

---

## 实际案例

**参考文章**: 《这个春节,宠物不再是"旁观者"——2026人宠共融生活图鉴》

**文件位置**: `/Users/echochen/Desktop/这个春节,宠物不再是旁观者_最终版.html`

**验证状态**: ✅ 已在生产环境使用

---

## 版本历史

### v1.0 (2026-02-08)
- ✅ 初始版本
- ✅ 基于实际文章验证
- ✅ 支持Markdown转HTML
- ✅ 5种特色区块样式
- ✅ 响应式设计
- ✅ 移动端优化

---

**宠商圈HTML排版Skill已准备就绪！**

使用方法:
1. 直接说"排版这篇文章"
2. 或"把这篇文章转换成HTML"
3. 或"生成宠物行业文章的HTML"

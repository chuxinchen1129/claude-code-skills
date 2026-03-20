# 宠商圈HTML排版Skill

> **推荐使用统一排版工具**：
> 现在推荐使用 **`wechat-formatter`** skill 进行统一排版，它支持：
> - 自动检测文章类型（悟昕/宠商圈）
> - 统一的品牌样式管理
> - 更好的维护性
>
> 使用方法：
> ```
> python ~/.claude/skills/wechat-formatter/scripts/format.py input.md -o output.html -t petcircle
> ```
>
> 本 skill 的样式规范已整合到 **`wechat-formatter`** 中。

---

> **版本**: v2.0
> **创建时间**: 2026-02-08
> **更新**: 2026-03-10
> **用途**: 专门为宠商圈行业文章提供HTML排版服务
> **状态**: 已整合到 `wechat-formatter` skill

---

## 技能描述

这是一个专门为宠商圈行业文章设计的HTML排版技能。它能够将Markdown格式的宠物行业文章转换为精美的HTML格式，适合在行业媒体、商业媒体和新媒体平台发布。

**已验证模板**: 基于《宠物经济炸裂：2026年全球宠物行业十大核心趋势》的实际排版代码。

---

## 核心特性

### 1. 专业排版风格
- 适合行业分析文章的排版样式
- 数据、案例、洞察分区分块展示
- **橙黄色渐变标题**增强视觉效果
- 移动端适配优化

### 2. 特色区块样式（橙黄色系 ✅）
- **正文区块**: 白色背景 #FFFFFF + 浅灰边框 #EEEEEE + 轻微阴影
- **小标题背景**: 橙黄色渐变 #FFC300 → #FFA500
- **强调色**: 橙红色 #FF4500（关键数字、标题）
- **正文色**: 深灰色 #3A3A3A

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
</head>
<body>
    <div style="background-color: #FFFFFF; padding: 15px 5px; font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei UI', 'Microsoft YaHei', Arial, sans-serif;">

        <!-- 标题 -->
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="font-size: 24px; color: #3A3A3A; font-weight: bold; margin: 0; line-height: 1.5;">
                [主标题]
            </h1>
            <p style="font-size: 16px; color: #FF4500; margin-top: 10px; font-weight: bold;">
                [副标题]
            </p>
        </div>

        <!-- 编者按 -->
        <div style="border: 1px solid #EEEEEE; padding: 15px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); margin-bottom: 20px;">
            <p style="color: #3A3A3A; font-size: 15px; line-height: 1.8; letter-spacing: 0.8px; margin: 0; text-align: justify;">
                <strong style="color: #FF4500; font-weight: bold;">编者按</strong>：[编者按内容]
            </p>
        </div>

        <!-- 章节标题 -->
        <div style="margin-top: 30px; margin-bottom: 20px;">
            <h2 style="font-size: 18px; color: #3A3A3A; font-weight: bold; margin: 0; padding: 6px 10px; display: inline-block; background-image: linear-gradient(to right, #FFC300, #FFA500); border-radius: 4px;">
                [章节标题]
            </h2>
        </div>

        <!-- 正文区块 -->
        <div style="border: 1px solid #EEEEEE; padding: 15px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); margin-bottom: 20px;">
            <p style="color: #3A3A3A; font-size: 15px; line-height: 1.8; letter-spacing: 0.8px; margin: 0; text-align: justify;">
                [正文内容] <strong style="color: #FF4500;">[关键数字]</strong> [正文内容]
            </p>
        </div>

        <!-- 图片 -->
        <div style="margin-top: 15px;">
            <img src="[图片路径]" alt="[图片说明]" style="width: 100%; height: auto; border-radius: 4px;">
        </div>

        <!-- 数据区块 -->
        <div style="border: 1px solid #EEEEEE; padding: 15px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); margin-bottom: 20px;">
            <p style="color: #3A3A3A; font-size: 15px; line-height: 1.8; letter-spacing: 0.8px; margin: 0; text-align: justify;">
                [数据内容] <strong style="color: #FF4500;">[关键数字]</strong> [数据内容]
            </p>
        </div>

        <!-- 案例区块 -->
        <div style="border: 1px solid #EEEEEE; padding: 15px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.08);">
            <p style="color: #3A3A3A; font-size: 15px; line-height: 1.8; letter-spacing: 0.8px; margin-bottom: 10px; text-align: justify;">
                <strong style="color: #FF4500; font-weight: bold;">[案例标题]</strong>
            </p>
            <p style="color: #3A3A3A; font-size: 15px; line-height: 1.8; letter-spacing: 0.8px; margin: 0; text-align: justify;">
                [案例内容]
            </p>
        </div>

        <!-- 结语 -->
        <div style="margin-top: 40px; margin-bottom: 20px;">
            <h2 style="font-size: 18px; color: #3A3A3A; font-weight: bold; margin: 0; padding: 6px 10px; display: inline-block; background-image: linear-gradient(to right, #FFC300, #FFA500); border-radius: 4px;">
                结语
            </h2>
        </div>

        <div style="border: 1px solid #EEEEEE; padding: 15px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.08);">
            <p style="color: #3A3A3A; font-size: 15px; line-height: 1.8; letter-spacing: 0.8px; margin: 0; text-align: justify;">
                [结语内容]
            </p>
        </div>

        <!-- 数据来源 -->
        <div style="margin-top: 30px;">
            <p style="font-size: 14px; color: #999999; text-align: center; line-height: 1.6;">
                <strong>数据来源</strong>：[数据来源说明]<br>
                <strong>发布时间</strong>：[发布日期]
            </p>
        </div>

        <!-- END标志 -->
        <p style="font-size: 15px; color: #FF4500; font-weight: bold; text-align: center; margin-top: 50px; margin-bottom: 20px;">
            END
        </p>

    </div>
</body>
</html>
```

---

## 颜色方案（v2.0 正确版本）

| 元素 | 颜色值 | 说明 |
|------|--------|------|
| **标题背景** | `#FFC300 → #FFA500` | 橙黄色渐变 |
| **强调色** | `#FF4500` | 橙红色（关键数字、标题） |
| **正文色** | `#3A3A3A` | 深灰色 |
| **正文背景** | `#FFFFFF` | 白色 |
| **边框** | `#EEEEEE` | 浅灰色 |
| **阴影** | `rgba(0,0,0,0.08)` | 轻微投影 |

### 区块样式

- **内容区块**：白色背景 + 浅灰边框 + 轻微阴影
- **小标题**：橙黄色渐变背景 + 圆角
- **关键数字**：橙红色 #FF4500 加粗

### 字体规范

- **中文字体**: PingFang SC, Hiragino Sans GB, Microsoft YaHei
- **英文字体**: -apple-system, BlinkMacSystemFont, Helvetica Neue
- **正文字号**: 15px
- **行高**: 1.8
- **字间距**: 0.8px

---

## 输出规范

### 文件命名规则
```
[文章标题]_最终版.html
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

### 风格参考

生成内容时可参考 **writing-style-standardizer** 的商业分析风格：
- 样本参考：sample_01_whole_foods.md ~ sample_05_time_relativity.md
- 语气：理性、深度、洞见驱动
- 特点：数据支撑、对比分析、洞见提炼

---

## 实际案例

**参考文章**: 《宠物经济炸裂：2026年全球宠物行业十大核心趋势》

**文件位置**: `~/Desktop/DMS/00.每日工作/2026-03-03_宠物经济炸裂_2026年全球宠物行业十大核心趋势/宠物经济炸裂_2026年全球宠物行业十大核心趋势_HTML_v2.html`

**验证状态**: ✅ 已在生产环境使用

---

## 版本历史

### v2.0 (2026-03-06)
- ✅ 更新为橙黄色系排版
- ✅ 基于《宠物经济炸裂》实际文章验证
- ✅ 统一使用橙红色强调色 #FF4500
- ✅ 橙黄色渐变标题背景

### v1.0 (2026-02-08)
- ❌ 错误版本（灰色+红色+蓝色+紫色）
- 已废弃

---

**宠商圈HTML排版Skill已更新为v2.0！**

使用方法:
1. 直接说"排版这篇文章"
2. 或"把这篇文章转换成HTML"
3. 或"生成宠物行业文章的HTML"
---
name: cover-generator
description: 现代社论风封面生成器，为PDF报告生成3:4比例的社论风格封面图片。与 baogaomiao 共享同一套底层引擎，避免自动流程和独立重生图结果不一致。支持版本化输出，便于反复迭代标题。
version: 1.0.0
created: 2026-03-16
updated: 2026-03-16

---

# 🎨 现代社论风封面生成器

快速为PDF报告生成专业、美观的社论风格封面图片。
当前独立 skill 与 `baogaomiao` 自动封面已复用同一底层实现。

## 🚀 快速开始

### 方式1：独立使用（推荐）

```bash
# 使用默认参数
cover-generator

# 指定参数
cover-generator --source "艺恩" --title "智驾未来AI重塑汽车消费" --year 2026

# 出多版封面
cover-generator --source "艺恩" --title "智驾未来AI重塑汽车消费" --year 2026 --variant v2
```

### 方式2：被其他skill调用

```python
from skills.cover_generator.scripts.cover_generator import CoverGenerator

generator = CoverGenerator()
result = generator.generate_cover(
    source="艺恩",
    chinese_title="智驾未来AI重塑汽车消费",
    english_title="AI RESHAPING AUTOMOTIVE CONSUMPTION",
    year=2026
)
```

---

## 📋 核心功能

### 1. 自动生成封面HTML
- **统一社论风格**：报告喵专属报纸杂志质感，专业大气
- **3:4比例**：适配小红书、朋友圈等社交平台
- **智能断词**：自动在语义边界处断行
- **统一底层**：直接复用 `baogaomiao` 的正式封面生成器
- **标题保真**：默认不改写标题语义，只做排版；如需中性化需显式开启

### 2. 图片转换
- **HTML转PNG**：使用Playwright实现高质量渲染
- **Retina质量**：2倍缩放，输出高清图片
- **本地处理**：无需上传，快速生成

### 3. 参数提取
- **来源机构**：自动识别或手动指定
- **年份提取**：从标题自动提取2024-2029年份
- **标题处理**：移除emoji，保留核心信息

---

## 🎛️ 参数说明

### 必需参数

| 参数 | 说明 | 示例 | 默认值 |
|------|------|------|--------|
| `chinese_title` | 中文标题 | "智驾未来AI重塑汽车消费" | - |
| `english_title` | 英文标题 | "AI RESHAPING AUTOMOTIVE" | - |
| `year` | 年份 | 2026 | 2026 |

### 可选参数

| 参数 | 说明 | 示例 | 默认值 |
|------|------|------|--------|
| `source` | 来源机构 | "艺恩" | "研究报告" |
| `page_count` | 报告页数 | 29 | - |
| `highlight_title` | 梗概标题 | "从营销狂欢到理性回归" | "核心要点" |
| `summary_text` | 摘要文本 | "智驾标配化，场景化种草" | 根据标题生成 |
| `report_type` | 报告类型 | "行业趋势报告" | "行业研究报告" |
| `output` | 输出文件名 | "cover_20260316.png" | 自动生成 |
| `variant` | 版本后缀 | "v2" | - |
| `neutralize_title` | 是否中性化标题 | false | false |

---

## 📐 封面布局

```
┌─────────────────────────┐
│     2026｜智驾未来AI    │  ← 第1行：年份｜主标题（最多10字）
│     重塑汽车消费        │
├─────────────────────────┤
│   场景化种草与90后      │  ← 第2行：副标题/梗概（最多12字）
│   男性用户驱动          │
├─────────────────────────┤
│   AI RESHAPING          │  ← 第3行：英文标题
│   AUTOMOTIVE CONSUMPTION │
├─────────────────────────┤
│   艺恩 | 29页 | 行业    │  ← 底部信息
│   趋势报告              │
└─────────────────────────┘
```

---

## 🔧 高级功能

### 标题控制规则

- 默认不修改标题语义，只负责排版
- 如果你在标题中显式使用 `｜`、`|` 或换行，会优先按你的断句来出图
- 需要多版时，使用 `--variant v2`、`--variant v3` 连续输出
- 只有在明确想把“龙头/密码/逆势增长”等字眼改中性时，才开启 `--neutralize-title`


### 字体设置

- **中文标题**：Noto Serif SC，加粗，57.6px
- **英文标题**：无衬线字体，36px
- **正文**：Noto Sans SC，常规，18px

---

## 📂 文件结构

```
skills/cover-generator/
├── SKILL.md              # 本文件
├── scripts/
│   ├── cover_generator.py    # 主生成器（调用 baogaomiao 正式封面引擎）
│   └── html_to_image.py      # 图片转换
├── references/
│   └── fonts/              # 字体文件（如需要）
└── output/                 # 生成的封面图片
```

---

## 🎯 使用场景

### 场景1：PDF报告处理
```bash
# 处理PDF后自动生成封面
baogaomiao /path/to/report.pdf
# 自动生成：cover_report_20260316.png
```

### 场景2：单独生成封面
```bash
# 为已有的报告生成封面
cover-generator \
  --source "东方财富" \
  --title "2026新能源汽车行业报告" \
  --year 2026
```

### 场景3：批量生成
```python
# 批量处理多个报告
reports = [
    {"title": "母婴行业报告", "year": 2026},
    {"title": "AI行业白皮书", "year": 2026}
]

for report in reports:
    generator.generate_cover(**report)
```

---

## ⚙️ 配置文件

配置文件位置：`scripts/cover_config.yaml`

```yaml
# 输出设置
output:
  dir: "output"
  scale: 2.0
  width: 1080
  height: 1440

# 字体设置
fonts:
  chinese_title: "Noto Serif SC"
  english_title: "Inter"
  body: "Noto Sans SC"

# 配色方案
colors:
  technology:
    primary: "#1a365d"
    secondary: "#2563eb"
  consumer:
    primary: "#7c2d12"
    secondary: "#ea580c"
```

---

## 🔗 与报告喵集成

报告喵skill与本 skill 共用同一套封面引擎：

```python
# baogaomiao处理流程
1. 提取PDF内容 ✅
2. 生成小红书笔记 ✅
3. 生成社论风封面 ✅ (调用cover-generator)
4. 转换为PNG图片 ✅
5. 发送到飞书 ✅
```

---

## 📝 示例

### 示例1：标准报告封面
```bash
cover-generator \
  --title "2026 OpenClaw AI Agent 技术白皮书" \
  --year 2026 \
  --highlight "AI Agent 技术全景" \
  --summary "从框架到应用"
```

生成：报告喵统一紫色渐变社论风封面

### 示例2：消费类报告
```bash
cover-generator \
  --title "2026母婴连锁经营数据报告" \
  --source "国金证券" \
  --highlight "逆势增长密码" \
  --year 2026
```

生成：报告喵统一紫色渐变社论风封面

---

## ⚠️ 注意事项

1. **标题长度**：中文标题建议控制在20字以内
2. **特殊字符**：自动移除emoji和特殊符号
3. **图片质量**：2倍缩放，文件大小约500KB-2MB
4. **生成速度**：约3-5秒/张
5. **依赖检查**：确保Playwright已安装

---

## 🐛 故障排查

### 问题1：Playwright未安装
```bash
pip install playwright
playwright install chromium
```

### 问题2：中文字体不显示
```bash
# 检查字体是否安装
fc-list :lang=zh | grep Noto
```

### 问题3：图片转换失败
- 检查HTML文件是否生成
- 查看日志中的错误信息
- 尝试手动用浏览器打开HTML

---

## 📞 技术支持

遇到问题？检查：
1. Python版本 >= 3.10
2. 依赖包是否安装完整
3. 日志文件：`logs/cover_generator.log`

---

**最后更新**：2026-03-16
**版本**：1.0.0

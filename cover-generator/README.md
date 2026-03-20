# 🎨 封面生成器 (Cover Generator)

现代社论风封面生成工具，为PDF报告生成专业、美观的封面图片。

## ✨ 特性

- 🎯 **独立使用**：可作为单独的命令行工具
- 🔌 **API调用**：可被其他skill（如baogaomiao）调用
- 🤖 **智能断词**：自动在语义边界处断开标题
- 🎨 **统一风格**：报告喵专属社论风，紫色渐变主题
- 📐 **标准比例**：3:4比例，适配小红书、朋友圈

## 🚀 快速开始

### 安装依赖

```bash
pip install playwright
playwright install chromium
```

### 基本使用

```bash
# 生成封面（使用示例参数）
python3 skills/cover-generator/scripts/cover_generator.py

# 指定参数
python3 skills/cover-generator/scripts/cover_generator.py \
  --chinese-title "2026新能源汽车行业报告" \
  --english-title "NEW ENERGY VEHICLE REPORT" \
  --year 2026 \
  --source "东方财富" \
  --output cover_ev_20260316.png
```

## 📖 参数说明

| 参数 | 必需 | 说明 | 示例 |
|------|------|------|------|
| `--chinese-title` | ✅ | 中文标题 | "2026智驾未来AI重塑汽车消费" |
| `--english-title` | ❌ | 英文标题 | "AI RESHAPING AUTOMOTIVE" |
| `--year` | ❌ | 年份（默认2026） | 2026 |
| `--source` | ❌ | 来源机构 | "艺恩" |
| `--highlight` | ❌ | 梗概标题 | "从营销狂欢到理性回归" |
| `--output` | ❌ | 输出文件名 | cover_20260316.png |

## 🔗 集成到报告喵

报告喵skill会自动调用封面生成器：

```python
# 在baogaomiao中调用
from skills.cover_generator.scripts.cover_generator import CoverGenerator

generator = CoverGenerator()
result = generator.generate_cover(
    chinese_title="智驾未来AI重塑汽车消费",
    english_title="AI RESHAPING AUTOMOTIVE",
    year=2026
)
```

## 📂 输出目录

生成的封面保存在：
```
skills/cover-generator/output/
├── cover_20260316_143022.png
└── cover_20260316_150833.png
```

## 🎯 使用场景

1. **PDF报告处理**：自动为报告生成封面
2. **单独生成**：为已有报告重新生成封面
3. **批量处理**：批量生成多个报告的封面

## ⚙️ 配置文件

配置文件：`scripts/cover_config.yaml`

## 📝 示例

```bash
# 科技类报告
python3 cover_generator.py \
  --chinese-title "2026 AI Agent技术白皮书" \
  --year 2026

# 消费类报告
python3 cover_generator.py \
  --chinese-title "2026母婴连锁经营数据报告" \
  --source "国金证券" \
  --highlight "逆势增长密码"
```

## 🔧 高级功能

### 自定义断词词库

```python
from scripts.title_splitter import TitleSplitter

splitter = TitleSplitter(custom_words=["OpenClaw", "AI", "Agent"])
```

### 自定义配色

修改HTML模板中的CSS变量。

---

**版本**: 1.0.0
**最后更新**: 2026-03-16

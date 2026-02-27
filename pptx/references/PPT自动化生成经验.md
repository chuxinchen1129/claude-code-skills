# PPT自动化生成经验

> **来源项目**: 潮宏基竞品分析 - 白岚银饰
> **经验提取时间**: 2026-02-06
> **复用性**: ⭐⭐⭐⭐⭐

---

## 🎯 适用场景

数据分析PPT自动生成，特别是：
- 社交媒体数据分析报告
- 竞品分析报告
- 市场研究可视化
- 图片展示类PPT

---

## 🔧 核心技术栈

- **Python 3.13+**
- **python-pptx**: PPT文件生成
- **PIL/Pillow**: 图片处理和格式转换
- **PyYAML**: 配置文件管理

---

## ⚠️ 关键挑战与解决方案

### 挑战1: 图片格式不兼容

**问题**: 小红书图片是WEBP格式，扩展名却是.jpg，python-pptx无法直接使用。

**解决方案**:
```python
from PIL import Image
import tempfile

def convert_to_jpeg(image_path: str) -> tuple:
    """转换图片为JPEG格式"""
    img = Image.open(image_path)

    # 强制转换为RGB（处理WEBP、RGBA等情况）
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # 保存到临时文件（关键：delete=False）
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file, format='JPEG', quality=95, optimize=True)
    temp_file.close()

    # 跟踪临时文件以便后续清理
    return temp_file.name

# 在PPT保存后清理临时文件
def _cleanup_temp_files(temp_files):
    for temp_file in temp_files:
        os.unlink(temp_file)
```

**关键要点**:
- 使用 `delete=False` 保留临时文件
- 在PPT保存后才清理临时文件
- 使用 `optimize=True` 提高图片质量

---

### 挑战2: Inches对象运算

**问题**: `float(Inches(2.75))` 返回EMUs值（2514600），不是2.75

**解决方案**:
```python
from pptx.util import Inches

# ❌ 错误：返回的是EMUs值，不是英寸
max_width_inches = float(max_width)  # 2514600，不是2.75！

# ✅ 正确：直接使用Inches对象的算术运算
def calculate_image_size(orig_width, orig_height, max_width, max_height):
    aspect_ratio = orig_width / orig_height

    if aspect_ratio > 1.0:
        actual_width = max_width
        actual_height = max_width / aspect_ratio  # Inches对象除法
    else:
        actual_height = max_height
        actual_width = max_height * aspect_ratio  # Inches对象乘法

    return actual_width, actual_height
```

**关键知识点**:
- `Inches(2.75)` 内部存储为 2514600 EMUs (2.75 × 914400)
- `float(Inches(2.75))` 返回 2514600.0，不是 2.75
- `int(Inches(2.75))` 返回 2514600
- Inches对象支持 `+`, `-`, `*`, `/` 运算，自动处理EMU转换

---

### 挑战3: 图片重复

**问题**: 数据中存在重复note_id，导致图片重复使用。

**解决方案**:
```python
from collections import defaultdict

def deduplicate_notes(data):
    """去重：保留每个note_id中点赞数最高的记录"""
    # 按note_id分组
    note_groups = defaultdict(list)
    for note in data:
        note_groups[note['note_id']].append(note)

    # 每组保留点赞数最高的
    deduplicated = []
    for note_id, group in note_groups.items():
        best = max(group, key=lambda x: safe_int(x.get('liked_count', 0)))
        deduplicated.append(best)

    # 重新排序
    deduplicated.sort(key=lambda x: safe_int(x.get('liked_count', 0)), reverse=True)
    return deduplicated

def safe_int(value, default=0):
    """安全转换为int，处理空值和异常"""
    try:
        if value is None or value == '':
            return default
        return int(value)
    except (ValueError, TypeError):
        return default
```

---

### 挑战4: 排版不统一

**问题**: 字体大小10种、间距值29个、文本框宽度不一致。

**解决方案**: 创建统一的设计系统（YAML配置）

**配置文件**:
```yaml
# config/luxury_theme.yaml
colors:
  primary: "#B8860B"        # 暗金色
  text_title: "#2C2C2C"     # 标题
  text_body: "#666666"      # 正文

fonts:
  title: 54pt               # 封面标题
  heading: 36pt             # 页面标题
  body: 18pt                # 正文
  caption: 14pt             # 图片说明

spacing:
  paragraph_spacing: 14     # Pt
  card_gap: 0.25            # Inches
  image_gap: 0.375          # Inches

layout:
  slide_width: 13.333       # 16:9标准
  slide_height: 7.5
  content_width: 11.833
  margin_horizontal: 0.75
```

**主题系统类**:
```python
import yaml

class ThemeSystem:
    def __init__(self, config_file):
        self.config = yaml.safe_load(open(config_file))
        self._init_colors()
        self._init_fonts()
        self._init_spacing()

    def apply_title_style(self, text_frame):
        """统一的标题样式"""
        for paragraph in text_frame.paragraphs:
            paragraph.font.size = self.get_font_size('heading')
            paragraph.font.name = self.get_font_family('title')
            paragraph.font.color.rgb = self.get_color('text_title')

    def apply_body_style(self, text_frame):
        """统一的正文样式"""
        for paragraph in text_frame.paragraphs:
            paragraph.font.size = self.get_font_size('body')
            paragraph.font.color.rgb = self.get_color('text_body')
```

---

## 🏗️ 项目架构

```
项目/
├── config/
│   └── luxury_theme.yaml          # 主题配置
├── data_manager.py                # 数据管理模块
├── theme_system.py                # 主题系统模块
├── ppt_builder.py                 # PPT生成器
└── main.py                        # 主程序
```

### 核心模块

#### 1. DataManager
```python
class DataManager:
    def __init__(self, json_file):
        self.raw_data = self._load_json()
        self.deduplicated_data = None

    def deduplicate_notes(self):
        """数据去重"""

    def get_top_notes(self, n):
        """获取前N条高赞笔记"""

    def get_statistics(self):
        """获取统计信息"""
```

#### 2. ImageManager
```python
class ImageManager:
    def __init__(self, images_dir):
        self.images_dir = Path(images_dir)
        self.used_note_ids = set()
        self.image_cache = {}

    def get_image_path(self, note_id):
        """获取笔记的封面图路径"""

    def mark_as_used(self, note_id):
        """标记为已使用"""

    def is_used(self, note_id):
        """检查是否已使用"""
```

#### 3. ThemeSystem
```python
class ThemeSystem:
    def __init__(self, config_file):
        self.config = yaml.safe_load(open(config_file))

    def get_color(self, key):
        """获取颜色"""

    def get_font_size(self, key):
        """获取字体大小"""

    def apply_title_style(self, text_frame):
        """应用标题样式"""

    def apply_body_style(self, text_frame):
        """应用正文样式"""
```

#### 4. PPTBuilder
```python
class PPTBuilder:
    def __init__(self, json_file, images_dir, config_file, output_file):
        self.data_manager = DataManager(json_file)
        self.image_manager = ImageManager(images_dir)
        self.theme = ThemeSystem(config_file)

    def convert_to_jpeg(self, image_path):
        """图片格式转换"""

    def calculate_image_size(self, orig_w, orig_h, max_w, max_h):
        """计算保持比例的尺寸"""

    def add_cover_slide(self):
        """添加封面页"""

    def add_content_slide(self, title, content):
        """添加内容页"""

    def add_image_showcase_slide(self, title, notes):
        """添加图片展示页"""

    def build(self):
        """构建完整PPT"""

    def save(self):
        """保存PPT并清理临时文件"""
```

---

## 📝 最佳实践

### 图片处理
```python
# ✅ 使用临时文件（delete=False）
temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
img.save(temp_file, format='JPEG', quality=95, optimize=True)

# 跟踪临时文件
self.temp_files.append(temp_file.name)

# 在PPT保存后清理
def _cleanup_temp_files(self):
    for temp_file in self.temp_files:
        os.unlink(temp_file)
```

### Inches对象使用
```python
# ✅ 直接使用Inches对象运算
actual_width = max_height * aspect_ratio
actual_height = max_width / aspect_ratio
x_centered = x + (img_width - actual_width) / 2
```

### 样式统一
```python
# ✅ 使用主题系统
theme = ThemeSystem(config_file)
theme.apply_title_style(text_frame)
theme.apply_body_style(text_frame)
```

### 数据去重
```python
# ✅ 使用safe_int处理空值和异常值
def safe_int(value, default=0):
    try:
        if value is None or value == '':
            return default
        return int(value)
    except (ValueError, TypeError):
        return default
```

---

## 🐛 常见问题

### 问题1: 图片显示为空白
**原因**: 临时文件被过早删除或图片格式不兼容
**解决**: 使用delete=False，在PPT保存后才清理

### 问题2: 图片尺寸异常
**原因**: Inches对象被错误地转换为float
**解决**: 直接使用Inches对象运算

### 问题3: 图片重复
**原因**: 数据中存在重复ID
**解决**: 数据去重 + ImageManager跟踪

---

## 🚀 快速开始

### 步骤1: 准备数据
```json
// data.json
[
  {
    "note_id": "123456",
    "title": "笔记标题",
    "liked_count": 1000,
    "content": "笔记内容"
  }
]
```

### 步骤2: 创建主题配置
```yaml
# config/my_theme.yaml
colors:
  primary: "#B8860B"

fonts:
  heading: 36pt
  body: 18pt
```

### 步骤3: 创建PPT生成器
```python
from pptx import Presentation
from pptx.util import Inches, Pt

class MyPPTBuilder:
    def __init__(self, json_file, images_dir, config_file, output_file):
        self.data_manager = DataManager(json_file)
        self.image_manager = ImageManager(images_dir)
        self.theme = ThemeSystem(config_file)
        self.prs = Presentation()

    def build(self):
        # 添加幻灯片
        pass

    def save(self):
        self.prs.save(self.output_file)
```

### 步骤4: 运行生成
```python
builder = MyPPTBuilder('data.json', 'images/', 'config/my_theme.yaml', 'output.pptx')
builder.build()
builder.save()
```

---

## 📚 参考资源

- **python-pptx文档**: https://python-pptx.readthedocs.io/
- **Pillow文档**: https://pillow.readthedocs.io/
- **PyYAML文档**: https://pyyaml.org/

---

**经验提取完成！复用性：⭐⭐⭐⭐⭐**

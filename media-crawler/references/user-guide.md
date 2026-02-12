# MediaCrawler Skill 使用指南

> **完整指南** - 从安装到数据分析的全流程

---

## 目录

1. [快速开始](#快速开始)
2. [环境准备](#环境准备)
3. [基础使用](#基础使用)
4. [数据转换](#数据转换)
5. [常见问题](#常见问题)
6. [最佳实践](#最佳实践)

---

## 快速开始

### 5 分钟快速上手

```bash
# 1. 检查环境
python3 ~/.claude/skills/media-crawler/scripts/check_environment.py

# 2. 采集小红书数据
python3 ~/.claude/skills/media-crawler/scripts/run_crawler.py \
  --platform xhs --keywords "睡眠仪"

# 3. 查看数据
ls ~/MediaCrawler/data/xhs/json/
```

---

## 环境准备

### 1. 安装 MediaCrawler

```bash
# 克隆项目
cd ~
git clone https://github.com/NanmiCoder/MediaCrawler.git

# 进入目录
cd MediaCrawler
```

### 2. 创建虚拟环境

```bash
# 使用 Python 3.11 创建虚拟环境
python3.11 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 3. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置（可选）
vim .env
```

### 4. 验证环境

```bash
# 运行环境检查
python3 ~/.claude/skills/media-crawler/scripts/check_environment.py
```

---

## 基础使用

### 采集小红书数据

```bash
# 基本采集
python3 ~/.claude/skills/media-crawler/scripts/run_crawler.py \
  --platform xhs --keywords "睡眠仪"

# 多关键词采集
python3 ~/.claude/skills/media-crawler/scripts/run_crawler.py \
  --platform xhs --keywords "睡眠仪" "左点" "助眠"

# 自定义采集数量
python3 ~/.claude/skills/media-crawler/scripts/run_crawler.py \
  --platform xhs --keywords "睡眠仪" --max 100
```

### 采集抖音数据

```bash
python3 ~/.claude/skills/media-crawler/scripts/run_crawler.py \
  --platform douyin --keywords "产品名"
```

### 采集微博数据

```bash
python3 ~/.claude/skills/media-crawler/scripts/run_crawler.py \
  --platform weibo --keywords "话题"
```

### 采集 B站数据

```bash
python3 ~/.claude/skills/media-crawler/scripts/run_crawler.py \
  --platform bilibili --keywords "UP主"
```

---

## 数据转换

### JSON 转 Excel

```bash
# 使用 data-cleaner skill 转换
# 或者使用 pandas 手动转换

python3 << 'EOF'
import pandas as pd
import json
from pathlib import Path

# 读取最新的 JSON 文件
json_dir = Path("~/MediaCrawler/data/xhs/json").expanduser()
json_files = list(json_dir.glob("search_contents_*.json"))
json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

with open(json_files[0], "r", encoding="utf-8") as f:
    data = json.load(f)

# 转换为 DataFrame
df = pd.DataFrame(data)

# 保存为 Excel
output = json_files[0].with_suffix(".xlsx")
df.to_excel(output, index=False)
print(f"✓ 保存到: {output}")
EOF
```

---

## 常见问题

### Q1: Python 版本不对？

**原因**：MediaCrawler 需要 Python 3.11，但系统使用其他版本

**解决**：
```bash
# 安装 Python 3.11
brew install python@3.11  # macOS

# 重新创建虚拟环境
cd ~/MediaCrawler
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Q2: 扫码登录超时？

**原因**：超过 15 秒未扫码

**解决**：
- 重新运行脚本
- 准备好手机扫码
- 保持网络畅通

### Q3: 采集数据为空？

**可能原因**：
1. 关键词无结果 → 更换关键词
2. 触发限流 → 等待 30 分钟后重试
3. 登录失效 → 重新扫码登录

### Q4: Playwright 浏览器未安装？

**解决**：
```bash
cd ~/MediaCrawler
source .venv/bin/activate
playwright install chromium
```

---

## 最佳实践

### 1. 采集前准备

- [ ] 确认关键词有效（先手动搜索验证）
- [ ] 设置合理的采集数量（50-100）
- [ ] 准备好扫码登录
- [ ] 检查网络连接

### 2. 采集中监控

- 观察终端输出
- 发现错误及时查看 `troubleshooting.md`
- 触发限流立即停止

### 3. 采集后处理

- 验证数据完整性
- 转换为 Excel 格式便于分析
- 备份重要数据

---

## 集成工作流

### 采集 → 分析 → 上传飞书

```bash
# 1. 采集数据
python3 ~/.claude/skills/media-crawler/scripts/run_crawler.py \
  --platform xhs --keywords "产品名"

# 2. 转换为 Excel
# （使用 data-cleaner 或手动转换）

# 3. 上传到飞书
python3 ~/.claude/skills/feishu-automation-v2/scripts/feishu_user_auto.py \
  import-data --app-token <TOKEN> --table-id <TABLE_ID> --excel data.xlsx
```

---

**更新时间**: 2026-02-11
**版本**: v1.0.0

---
name: media-crawler
description: 社交媒体数据采集工具 - 支持关键词搜索和 URL 链接采集。自动环境检查、配置管理、扫码登录提醒。当用户提到"采集"、"爬虫"、"MediaCrawler"、"小红书数据"、"抖音数据"、"小红书链接"、"URL 采集"时使用。
version: 1.1.0
created: 2026-02-11
updated: 2026-02-11
---

# MediaCrawler 采集 Skill v1.1

> **核心理念**：零学习成本采集社交媒体数据
> 自动环境检查 + 智能配置管理 + 扫码登录提醒 + URL 链接采集

---

## 🚀 快速开始

### 两种采集模式

**模式 1：关键词搜索**（常用）
```bash
# 采集小红书数据
python3 ~/.claude/skills/media-crawler/scripts/run_crawler.py --platform xhs --keywords "睡眠仪"

# 采集抖音数据
python3 ~/.claude/skills/media-crawler/scripts/run_crawler.py --platform douyin --keywords "产品名"

# 采集微博数据
python3 ~/.claude/skills/media-crawler/scripts/run_crawler.py --platform weibo --keywords "话题"
```

**模式 2：URL 链接采集**（指定笔记）
```bash
# 从文件读取小红书链接并采集
python3 ~/.claude/skills/media-crawler/scripts/process_xhs_links.py \
  --input ~/.claude/skills/feishu-bot/data/collections/2026-02-11/xiaohongshu_links.txt

# 支持短链接自动解析（xhslink.com）
# 支持完整链接（需包含 xsec_token 参数以获得最佳效果）
```

---

## 📋 支持的平台

| 平台 | 参数 | 数据类型 | 状态 |
|------|------|---------|------|
| 小红书 | `xhs` | 笔记、评论、用户 | ✅ 稳定 |
| 抖音 | `douyin` | 视频、评论、用户 | ✅ 稳定 |
| 微博 | `weibo` | 博文、评论、用户 | ✅ 稳定 |
| B站 | `bilibili` | 视频、评论、用户 | ✅ 稳定 |
| 百度 | `baidu` | 搜索结果 | ✅ 稳定 |
| 快手 | `kuaishou` | 视频、评论 | ⚠️ 实验性 |
| 知乎 | `zhihu` | 回答、文章 | ⚠️ 实验性 |

---

## 🎯 URL 链接采集（新增）

### 支持的链接格式

- **完整链接**：`https://www.xiaohongshu.com/explore/...?xsec_token=...`
- **短链接**：`https://xhslink.com/o/xxxxx` （自动解析）

### 使用方式

```bash
python3 ~/.claude/skills/media-crawler/scripts/process_xhs_links.py \
  --input <链接文件路径>
```

### 输入文件格式

每行一个链接（支持带其他文字自动提取）：
```
http://xhslink.com/o/9BIu7Qm6rEy
春节就送这个！解决长辈"睡不好"的难题 http://xhslink.com/o/xxxxx
https://www.xiaohongshu.com/explore/64b95d01000000000c034587?xsec_token=...
```

### 处理流程

1. **读取链接**：从文件中提取小红书链接
2. **解析短链接**：xhslink.com → 完整 URL
3. **配置采集**：自动设置 MediaCrawler 为 detail 模式
4. **执行采集**：批量采集指定链接
5. **输出数据**：`~/MediaCrawler/data/xhs/json/`

### 重要说明

- **xsec_token 参数**：完整 URL 包含此参数时采集成功率更高
- **登录要求**：首次使用需扫码登录
- **采集模式**：使用 MediaCrawler 的 detail 模式（帖子详情采集）

---

## ⚙️ 核心功能

### 1. 自动环境检查 ⭐

每次运行前自动检查：
- ✅ Python 版本（需要 3.11）
- ✅ 虚拟环境（~/MediaCrawler/.venv）
- ✅ MediaCrawler 目录
- ✅ 配置文件完整性

**无需手动检查，脚本会提示所有问题！**

### 2. 智能配置管理

自动处理配置文件：
- ✅ 自动备份原始配置
- ✅ 参数化修改（关键词、数量、平台）
- ✅ 采集完成后自动恢复
- ✅ 支持多关键词批量采集

### 3. 扫码登录提醒

清晰的登录提示：
```
⚠️  请在浏览器中完成登录...
📱 扫描二维码登录（15秒内有效）
💡 登录后采集自动开始，无需其他操作
```

### 4. 数据自动转换

智能数据清洗：
- ✅ "万"字处理：1.5万 → 15000
- ✅ 时间戳转换：毫秒 → 标准格式
- ✅ 空值处理：NaN → 空字符串
- ✅ TOP N 排序：按互动量自动排序

---

## 📂 数据输出

### 目录结构

```
~/MediaCrawler/data/
├── xhs/                    # 小红书数据
│   └── json/
│       └── search_contents_*.json
├── douyin/                 # 抖音数据
│   └── json/
├── weibo/                  # 微博数据
    └── json/
```

### 数据格式

每条记录包含：
- 基础信息：ID、标题、内容、作者
- 互动数据：点赞、评论、收藏、分享
- 媒体内容：封面、视频 URL
- 元数据：时间、IP、标签、关键词

---

## 🔧 高级用法

### 模式 1：多关键词采集

```bash
# 采集多个关键词（用空格分隔）
python3 scripts/run_crawler.py --platform xhs \
  --keywords "睡眠仪" "左点" "助眠" "白噪音"
```

### 模式 2：URL 链接采集

```bash
# 从文件批量采集小红书链接
python3 ~/.claude/skills/media-crawler/scripts/process_xhs_links.py \
  --input ~/.claude/skills/feishu-bot/data/collections/2026-02-11/xiaohongshu_links.txt
```

### 自定义采集数量

```bash
# 采集 100 条（默认 50）
python3 scripts/run_crawler.py --platform xhs \
  --keywords "睡眠仪" --max 100
```

### 仅检查环境（不采集）

```bash
python3 scripts/check_environment.py
```

### 数据转换工具

```bash
# 将采集的 JSON 转换为 Excel
python3 scripts/to_excel.py --input ~/MediaCrawler/data/xhs/json/
```

---

## 📚 参考文档

| 文档 | 内容 | 何时查看 |
|------|------|---------|
| `user-guide.md` | 完整使用指南 | 首次使用 |
| `troubleshooting.md` | 问题排查 | 遇到错误 |
| `platform-details.md` | 各平台详细说明 | 了解平台差异 |
| `experience-log.md` | 经验积累日志 | 持续更新 |

---

## ⚠️ 重要注意事项

### 1. 首次使用

首次使用需要扫码登录：
- 运行脚本后会自动打开浏览器
- 扫描二维码登录
- 15秒内有效
- 登录后可保持会话（无需每次扫码）

### 2. 环境隔离

MediaCrawler 需要 Python 3.11，与大秘书系统（Python 3.13.7）隔离：
- ✅ 虚拟环境：`~/MediaCrawler/.venv`
- ✅ 脚本自动激活正确环境
- ⚠️ 不要手动 `pip install` 到主环境

### 3. 采集速度

- 小红书：约 1-2 条/秒
- 抖音：约 0.5-1 条/秒
- 建议：单次不超过 200 条
- 超量采集可能触发限流

### 4. 数据合规

- ✅ 仅用于个人学习研究
- ✅ 遵守平台服务条款
- ❌ 不得用于商业用途
- ❌ 不得恶意攻击平台

---

## 🚨 常见问题

### Q1: 环境检查失败？

**原因**：Python 版本不对或虚拟环境缺失

**解决**：
```bash
# 检查 Python 版本
python3 --version  # 应显示 3.11.x

# 如果不对，重新创建虚拟环境
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

### Q4: 数据格式不对？

**检查**：
```bash
# 验证 JSON 格式
cat ~/MediaCrawler/data/xhs/json/search_contents_*.json | jq .
```

### Q5: URL 采集失败？

**可能原因**：
1. **缺少 xsec_token**：短链接解析后可能不包含此参数
   - 解决：在浏览器中打开链接获取完整 URL
2. **链接已失效**：笔记已被删除或设为私密
   - 解决：验证链接是否可访问
3. **登录问题**：MediaCrawler 需要有效的登录状态
   - 解决：重新扫码登录

### Q6: 短链接解析失败？

**原因**：网络问题或链接已过期

**解决**：
```bash
# 手动测试短链接
curl -I http://xhslink.com/o/9BIu7Qm6rEy

# 或直接在浏览器中打开获取完整 URL
```

---

## 🎯 最佳实践

### 1. 采集前准备

**关键词搜索模式**：
- [ ] 确认关键词有效（先手动搜索验证）
- [ ] 设置合理的采集数量（50-100）
- [ ] 准备好扫码登录
- [ ] 检查网络连接

**URL 链接采集模式**：
- [ ] 收集目标笔记链接（支持短链接）
- [ ] 确认链接格式正确
- [ ] 准备好扫码登录
- [ ] 检查链接文件路径

### 2. 采集中监控

- 观察终端输出
- 发现错误及时查看 `troubleshooting.md`
- 触发限流立即停止
- URL 采集时注意短链接解析状态

### 3. 采集后处理

- 验证数据完整性
- 转换为 Excel 格式便于分析
- 备份重要数据
- 检查是否有采集失败的链接（URL 模式）

---

## 🔄 与其他 Skill 集成

### 数据分析 Agent

```bash
# 采集 → 分析
python3 scripts/run_crawler.py --platform xhs --keywords "产品名"
# 采集完成后自动分析
```

### 飞书自动化 Agent

```bash
# 采集 → 上传飞书
python3 scripts/run_crawler.py --platform xhs --keywords "产品名"
python3 scripts/to_excel.py --input ~/MediaCrawler/data/xhs/json/
# 然后使用飞书自动化导入
```

**URL 采集模式**：
```bash
# 从飞书收集的链接 → 采集 → 上传飞书
python3 ~/.claude/skills/media-crawler/scripts/process_xhs_links.py \
  --input ~/.claude/skills/feishu-bot/data/collections/2026-02-11/xiaohongshu_links.txt
# 采集完成后使用飞书自动化导入
```

---

**记住**：这个 Skill 会随着使用不断进化，每次遇到新问题都会记录到 `experience-log.md`！

# MediaCrawler 问题排查手册

> **遇到错误？先看这里！**

---

## 目录

1. [环境问题](#环境问题)
2. [登录问题](#登录问题)
3. [采集问题](#采集问题)
4. [数据问题](#数据问题)
5. [性能问题](#性能问题)

---

## 环境问题

### ❌ 错误：Python 版本不匹配

**错误信息**：
```
⚠️  Python 版本不匹配，需要 3.11.x，当前 3.13.7
```

**原因**：
- MediaCrawler 需要 Python 3.11
- 系统使用其他版本

**解决方案**：
```bash
# 1. 安装 Python 3.11
brew install python@3.11  # macOS
# 或下载: https://www.python.org/downloads/

# 2. 重新创建虚拟环境
cd ~/MediaCrawler
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 验证
python3 --version  # 应显示 3.11.x
```

### ❌ 错误：虚拟环境不存在

**错误信息**：
```
❌ 虚拟环境不存在: ~/MediaCrawler/.venv/bin/python
```

**解决方案**：
```bash
cd ~/MediaCrawler
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### ❌ 错误：依赖包缺失

**错误信息**：
```
ModuleNotFoundError: No module named 'playwright'
```

**解决方案**：
```bash
cd ~/MediaCrawler
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

---

## 登录问题

### ❌ 错误：扫码登录超时

**错误信息**：
```
⚠️  登录超时，请重新运行
```

**原因**：
- 超过 15 秒未扫码

**解决方案**：
1. 重新运行脚本
2. 准备好手机扫码
3. 保持网络畅通
4. 扫码后等待确认

### ❌ 错误：登录失败

**错误信息**：
```
⚠️  登录失败，请重试
```

**可能原因**：
- 网络问题
- 账号异常
- 验证码过期

**解决方案**：
1. 检查网络连接
2. 确认账号状态正常
3. 重新扫码登录
4. 等待 30 秒后重试

---

## 采集问题

### ❌ 错误：采集数据为空

**错误信息**：
```
⚠️  未找到采集数据
```

**可能原因**：
1. 关键词无搜索结果
2. 触发平台限流
3. 登录失效

**解决方案**：
```bash
# 1. 验证关键词
# 先手动搜索确认关键词有结果

# 2. 检查登录状态
# 重新运行脚本，重新扫码登录

# 3. 等待限流恢复
# 等待 30 分钟后重试

# 4. 减少采集数量
python3 scripts/run_crawler.py --platform xhs --keywords "测试" --max 20
```

### ❌ 错误：触发限流

**错误信息**：
```
⚠️  触发限流，请稍后重试
```

**解决方案**：
1. 立即停止采集
2. 等待 30-60 分钟
3. 减少采集数量
4. 避免频繁请求

---

## 数据问题

### ❌ 错误：JSON 解析失败

**错误信息**：
```
JSONDecodeError: Expecting value
```

**可能原因**：
- JSON 文件损坏
- 采集未完成

**解决方案**：
```bash
# 1. 检查 JSON 文件
cat ~/MediaCrawler/data/xhs/json/search_contents_*.json | jq .

# 2. 如果损坏，重新采集
# 3. 检查磁盘空间
df -h
```

### ❌ 错误："万"字未转换

**问题**：
- 数据中包含 "1.5万" 这样的字符串

**解决方案**：
```python
def parse_count(count_str):
    """处理 '万' 字"""
    if isinstance(count_str, str):
        if "万" in count_str:
            return float(count_str.replace("万", "")) * 10000
        return int(count_str.replace(",", ""))
    return int(count_str) if count_str else 0

# 使用
likes = parse_count("1.5万")  # 15000
```

---

## 性能问题

### ⚠️ 采集速度慢

**原因**：
- 网络延迟
- 平台限制
- 采集数量过多

**优化方案**：
```bash
# 1. 减少采集数量
--max 30  # 从 50 减少到 30

# 2. 使用多关键词分开采集
# 而不是一次采集多个关键词

# 3. 避开高峰时段
# 选择早晨或深夜采集
```

### ⚠️ 内存占用高

**原因**：
- 采集数据量大
- 浏览器缓存

**解决方案**：
```bash
# 1. 限制采集数量
--max 50

# 2. 定期清理数据
# 删除旧的 JSON 文件

# 3. 重启采集
# 关闭浏览器，重新运行
```

---

## 快速诊断

### 运行环境检查

```bash
python3 ~/.claude/skills/media-crawler/scripts/check_environment.py
```

### 查看日志

```bash
# MediaCrawler 日志
cat ~/MediaCrawler/logs/*.log

# 浏览器日志
ls ~/MediaCrawler/browser_cache/
```

---

## 获取帮助

如果以上方案都无法解决问题：

1. 查看 MediaCrawler 官方文档
2. 搜索 issue
3. 记录错误信息，寻求帮助

---

**更新时间**: 2026-02-11
**版本**: v1.0.0

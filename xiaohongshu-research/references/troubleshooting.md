# 小红书调研技能 - 问题排查

**文档版本**：v1.0.0
**更新时间**：2026-03-02

---

## 常见问题

### 问题 1: MediaCrawler 采集失败

**症状**：
- 采集进程启动失败
- 返回错误码非0
- 没有生成JSON文件

**可能原因**：
1. MediaCrawler 目录不存在
2. uv 未正确安装
3. 网络连接问题
4. 浏览器启动失败

**解决方案**：
```bash
# 1. 检查MediaCrawler路径
ls -la ~/MediaCrawler

# 2. 检查uv是否安装
which uv

# 3. 重启采集
python -m skills.xiaohongshu-research --keywords "测试" --count 5
```

---

### 问题 2: 数据处理失败

**症状**：
- JSON数据读取失败
- pandas 处理出错
- KeyError 或 AttributeError

**可能原因**：
1. JSON 文件格式错误
2. 数据字段缺失
3. 数据类型不匹配

**解决方案**：
```python
# 1. 检查JSON数据结构
import json
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(data[0].keys())  # 查看第一个对象的字段

# 2. 添加错误处理
try:
    df = pd.DataFrame(data)
except KeyError as e:
    print(f"  字段错误: {e}")
    print(f"  可用字段: {df.columns.tolist()}")
except Exception as e:
    print(f"  处理失败: {e}")
```

---

### 问题 3: Excel生成失败

**症状**：
- openpyxl 写入失败
- 文件权限错误
- 内存不足

**可能原因**：
1. 输出目录不存在
2. 没有写入权限
3. 数据量过大

**解决方案**：
```bash
# 1. 检查输出目录权限
ls -la 00.每日工作/

# 2. 清理旧文件
rm -f 00.每日工作/*/数据表.xlsx

# 3. 减少数据量或分批处理
python -m skills.xiaohongshu-research --keywords "茯苓" --count 10
```

---

### 问题 4: 媒体文件处理失败

**症状**：
- 文件复制失败
- 路径不存在
- 权限错误

**可能原因**：
1. note_id 在 MediaCrawler 中不存在
2. 图像/视频目录结构异常

**解决方案**：
```python
# 1. 检查媒体目录结构
ls -la ~/MediaCrawler/data/xhs/images/

# 2. 验证 note_id
note_id = "69a4f0df000000001d011591"
ls -la ~/MediaCrawler/data/xhs/images/{note_id}/

# 3. 检查是否需要清空缓存
python -m skills.xiaohongshu-research --keywords "茯苓" --clear-cache
```

---

### 问题 5: 报告生成失败

**症状**：
- MD文件写入失败
- 中文编码问题
- 模板变量未替换

**解决方案**：
```python
# 1. 指定UTF-8编码
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. 检查模板变量
print(keywords)  # 应该显示 "茯苓"
```

---

## 调试技巧

### 启用调试输出

在脚本中添加 `-v` 或 `--verbose` 参数：

```python
# 在 parser 中添加
parser.add_argument('-v', '--verbose', action='store_true',
                   help='启用详细输出')

# 在代码中使用
if args.verbose:
    print(f"  Processing: {note_id}")
```

### 检查中间数据

```python
# 保存中间数据用于调试
import pickle

# 保存DataFrame
df_top.to_pickle('temp/debug_data.pkl')

# 恢复
with open('temp/debug_data.pkl', 'rb') as f:
    df_top = pickle.load(f)
```

---

## 获取支持

如果遇到以上问题未解决，可以：

1. 查看MediaCrawler文档：`~/MediaCrawler/README.md`
2. 查看数据分析Agent文档：`05_SYSTEM_DOCS/agents/数据分析Agent.md`
3. 检查系统全局经验：`05_SYSTEM_DOCS/global_brain/GLOBAL_LESSONS.md`

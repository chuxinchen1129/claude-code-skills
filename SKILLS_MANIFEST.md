# 技能清单

## 打包的技能

这些技能是自定义/第三方技能，需要手动安装到 `~/.agents/skills/` 目录。

### 安装方法

```bash
# 解压到技能目录
tar -xzf mcp-skills-*.tar.gz -C ~/.agents/skills/

# 或逐个复制
cp -r browser-auto ~/.agents/skills/
cp -r browser-auto-v2 ~/.agents/skills/
cp -r casual-cron ~/.agents/skills/
cp -r find-skills ~/.agents/skills/
```

### 技能说明

| 技能 | 描述 |
|------|------|
| browser-auto | 浏览器自动化（登录、表单、验证码） |
| browser-auto-v2 | 浏览器自动化 v2 |
| casual-cron | Cron 任务调度 |
| find-skills | 技能发现工具 |

### Tavily 技能

以下技能来自 Tavily，需要单独安装：

```bash
npx skills add -y -g tavily-ai/skills
```

- search (网页搜索)
- research (深度研究)
- extract (内容提取)
- crawl (网站爬取)
- tavily-best-practices (最佳实践)

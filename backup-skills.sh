#!/bin/bash
# 技能打包脚本 - 将自定义技能打包为可迁移的压缩包

set -e

SKILLS_DIR="$HOME/.agents/skills"
BACKUP_DIR="$HOME/mcp-skills-backup"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ARCHIVE_NAME="mcp-skills-${TIMESTAMP}.tar.gz"

echo "═══════════════════════════════════════════════════════════"
echo "              技能打包工具"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 创建备份目录
mkdir -p "$BACKUP_DIR"

echo "📦 打包自定义技能..."
echo ""

# 定义要打包的技能（排除 Tavily 技能，因为它们可以重新安装）
CUSTOM_SKILLS=(
    "browser-auto"
    "browser-auto-v2"
    "casual-cron"
    "find-skills"
)

# 创建临时目录
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# 复制技能
for skill in "${CUSTOM_SKILLS[@]}"; do
    if [ -d "$SKILLS_DIR/$skill" ]; then
        echo "  + $skill"
        cp -r "$SKILLS_DIR/$skill" "$TEMP_DIR/"
    else
        echo "  ⚠️  $skill 不存在，跳过"
    fi
done

# 添加技能清单
echo ""
echo "📄 生成技能清单..."
cat > "$TEMP_DIR/SKILLS_MANIFEST.md" << 'EOF'
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
EOF

# 创建压缩包
echo ""
echo "📦 创建压缩包..."
tar -czf "$BACKUP_DIR/$ARCHIVE_NAME" -C "$TEMP_DIR" .

# 复制清单
cp "$TEMP_DIR/SKILLS_MANIFEST.md" "$BACKUP_DIR/"

echo ""
echo "✅ 打包完成！"
echo ""
echo "压缩包: $BACKUP_DIR/$ARCHIVE_NAME"
echo "清单:   $BACKUP_DIR/SKILLS_MANIFEST.md"
echo ""
echo "═══════════════════════════════════════════════════════════"

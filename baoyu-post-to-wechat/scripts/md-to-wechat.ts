import fs from 'node:fs';
import path from 'node:path';
import { mkdir, writeFile } from 'node:fs/promises';
import os from 'node:os';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import https from 'node:https';
import http from 'node:http';
import { spawnSync } from 'node:child_process';
import process from 'node:process';

// 导入技能发现系统
import { SkillDiscovery, FormatterSkill } from './skill-discovery.js';

interface ImageInfo {
  placeholder: string;
  localPath: string;
  originalPath: string;
}

interface ParsedResult {
  title: string;
  author: string;
  summary: string;
  htmlPath: string;
  contentImages: ImageInfo[];
}

function downloadFile(url: string, destPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;
    const file = fs.createWriteStream(destPath);

    const request = protocol.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (response) => {
      if (response.statusCode === 301 || response.statusCode === 302) {
        const redirectUrl = response.headers.location;
        if (redirectUrl) {
          file.close();
          fs.unlinkSync(destPath);
          downloadFile(redirectUrl, destPath).then(resolve).catch(reject);
          return;
        }
      }

      if (response.statusCode !== 200) {
        file.close();
        fs.unlinkSync(destPath);
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }

      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    });

    request.on('error', (err) => {
      file.close();
      fs.unlink(destPath, () => {});
      reject(err);
    });

    request.setTimeout(30000, () => {
      request.destroy();
      reject(new Error('Download timeout'));
    });
  });
}

function getImageExtension(urlOrPath: string): string {
  const match = urlOrPath.match(/\.(jpg|jpeg|png|gif|webp)(\?|$)/i);
  return match ? match[1]!.toLowerCase() : 'png';
}

async function resolveImagePath(imagePath: string, baseDir: string, tempDir: string): Promise<string> {
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    const hash = createHash('md5').update(imagePath).digest('hex').slice(0, 8);
    const ext = getImageExtension(imagePath);
    const localPath = path.join(tempDir, `remote_${hash}.${ext}`);

    if (!fs.existsSync(localPath)) {
      console.error(`[md-to-wechat] Downloading: ${imagePath}`);
      await downloadFile(imagePath, localPath);
    }
    return localPath;
  }

  if (path.isAbsolute(imagePath)) {
    return imagePath;
  }

  return path.resolve(baseDir, imagePath);
}

function parseFrontmatter(content: string): { frontmatter: Record<string, string>; body: string } {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, body: content };

  const frontmatter: Record<string, string> = {};
  const lines = match[1]!.split('\n');
  for (const line of lines) {
    const colonIdx = line.indexOf(':');
    if (colonIdx > 0) {
      const key = line.slice(0, colonIdx).trim();
      let value = line.slice(colonIdx + 1).trim();
      if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      frontmatter[key] = value;
    }
  }

  return { frontmatter, body: match[2]! };
}

export async function convertMarkdown(markdownPath: string, options?: { title?: string; theme?: string }): Promise<ParsedResult> {
  const baseDir = path.dirname(markdownPath);
  const content = fs.readFileSync(markdownPath, 'utf-8');
  const theme = options?.theme ?? 'default';

  const { frontmatter, body } = parseFrontmatter(content);

  let title = options?.title ?? frontmatter.title ?? '';
  let bodyWithoutTitle = body;
  if (!title) {
    const lines = body.split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      const headingMatch = trimmed.match(/^#{1,2}\s+(.+)$/);
      if (headingMatch) {
        title = headingMatch[1]!;
        bodyWithoutTitle = body.replace(/^#{1,2}\s+.+\r?\n?/, '');
      }
      break;
    }
  } else {
    bodyWithoutTitle = body.replace(/^#{1,2}\s+.+\r?\n?/, '');
  }
  if (!title) title = path.basename(markdownPath, path.extname(markdownPath));
  const author = frontmatter.author || '';
  let summary = frontmatter.description || frontmatter.summary || '';

  if (!summary) {
    const lines = bodyWithoutTitle.split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      if (trimmed.startsWith('#')) continue;
      if (trimmed.startsWith('![')) continue;
      if (trimmed.startsWith('>')) continue;
      if (trimmed.startsWith('-') || trimmed.startsWith('*')) continue;
      if (/^\d+\./.test(trimmed)) continue;

      const cleanText = trimmed
        .replace(/\*\*(.+?)\*\*/g, '$1')
        .replace(/\*(.+?)\*/g, '$1')
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
        .replace(/`([^`]+)`/g, '$1');

      if (cleanText.length > 20) {
        summary = cleanText.length > 120 ? cleanText.slice(0, 117) + '...' : cleanText;
        break;
      }
    }
  }

  const images: Array<{ src: string; placeholder: string }> = [];
  let imageCounter = 0;

  const modifiedBody = bodyWithoutTitle.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, src) => {
    const placeholder = `WECHATIMGPH_${++imageCounter}`;
    images.push({ src, placeholder });
    return placeholder;
  });

  const modifiedMarkdown = `---\n${Object.entries(frontmatter).map(([k, v]) => `${k}: ${v}`).join('\n')}\n---\n${modifiedBody}`;

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'wechat-article-images-'));
  const tempMdPath = path.join(tempDir, 'temp-article.md');
  await writeFile(tempMdPath, modifiedMarkdown, 'utf-8');

  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
  const renderScript = path.join(__dirname, 'md', 'render.ts');

  console.error(`[md-to-wechat] Rendering markdown with theme: ${theme}`);

  const result = spawnSync('npx', ['-y', 'bun', renderScript, tempMdPath, '--theme', theme], {
    stdio: ['inherit', 'pipe', 'pipe'],
    cwd: baseDir,
  });

  if (result.status !== 0) {
    const stderr = result.stderr?.toString() || '';
    throw new Error(`Render failed: ${stderr}`);
  }

  const htmlPath = tempMdPath.replace(/\.md$/i, '.html');
  if (!fs.existsSync(htmlPath)) {
    throw new Error(`HTML file not generated: ${htmlPath}`);
  }

  const contentImages: ImageInfo[] = [];
  for (const img of images) {
    const localPath = await resolveImagePath(img.src, baseDir, tempDir);
    contentImages.push({
      placeholder: img.placeholder,
      localPath,
      originalPath: img.src,
    });
  }

  return {
    title,
    author,
    summary,
    htmlPath,
    contentImages,
  };
}

function printUsage(): never {
  console.log(`Convert Markdown to WeChat-ready HTML with image placeholders

Usage:
  npx -y bun md-to-wechat.ts <markdown_file> [options]

Options:
  --title <title>     Override title
  --theme <name>      Theme name (default, grace, simple, wuxin, petcircle)
  --skill <name>      Use specific formatter skill (auto-detect if not specified)
  --list-formatters   List all available formatter skills
  --help              Show this help

Skill Auto-Discovery:
  The system automatically scans for formatter skills in:
  - ~/.claude/skills/*-formatter/
  - ~/Desktop/DMS/skills/*-formatter/
  - ~/.claude/技能库/*-formatter/

  Priority order (configured in formatter-priority.yaml):
  1. wechat-formatter (wuxin, petcircle themes)
  2. baoyu-markdown-to-html (default, grace, simple themes)

Output JSON format:
{
  "title": "Article Title",
  "author": "Author Name",
  "summary": "Article summary",
  "htmlPath": "/tmp/wechat-article-images/temp-article.html",
  "contentImages": [
    {
      "placeholder": "WECHATIMGPH_1",
      "localPath": "/tmp/wechat-image/img.png",
      "originalPath": "imgs/image.png"
    }
  ]
}

Examples:
  # Auto-detect and use highest priority formatter
  npx -y bun md-to-wechat.ts article.md

  # Use specific formatter with theme
  npx -y bun md-to-wechat.ts article.md --skill wechat-formatter --theme wuxin
  npx -y bun md-to-wechat.ts article.md --skill wechat-formatter --theme petcircle

  # List all available formatters
  npx -y bun md-to-wechat.ts --list-formatters
`);
  process.exit(0);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    printUsage();
  }

  // 处理 --list-formatters 参数
  if (args.includes('--list-formatters') || args.includes('-l')) {
    const discovery = new SkillDiscovery();
    const list = await discovery.listFormatters();
    console.log(list);
    process.exit(0);
  }

  let markdownPath: string | undefined;
  let title: string | undefined;
  let theme: string | undefined;
  let skillName: string | undefined;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i]!;
    if (arg === '--title' && args[i + 1]) {
      title = args[++i];
    } else if (arg === '--theme' && args[i + 1]) {
      theme = args[++i];
    } else if (arg === '--skill' && args[i + 1]) {
      skillName = args[++i];
    } else if (!arg.startsWith('-')) {
      markdownPath = arg;
    }
  }

  // 如果没有指定文件，显示帮助
  if (!markdownPath && !skillName) {
    printUsage();
  }

  // 如果只是列出格式化器，不继续处理
  if (args.includes('--list-formatters')) {
    return;
  }

  if (!markdownPath) {
    console.error('Error: Markdown file path is required');
    process.exit(1);
  }

  if (!fs.existsSync(markdownPath)) {
    console.error(`Error: File not found: ${markdownPath}`);
    process.exit(1);
  }

  // 技能发现和选择
  let effectiveTheme = theme;
  let effectiveSkill = skillName;

  if (!effectiveSkill || !effectiveTheme) {
    const discovery = new SkillDiscovery();
    const selectedSkill = await discovery.selectFormatter(effectiveSkill, effectiveTheme);

    if (!selectedSkill) {
      console.error('Error: No suitable formatter skill found');
      console.error('Please install one of the following:');
      console.error('  - wechat-formatter: ~/.claude/skills/wechat-formatter/');
      console.error('  - baoyu-markdown-to-html: https://github.com/JimLiu/baoyu-skills');
      process.exit(1);
    }

    if (!effectiveSkill) {
      effectiveSkill = selectedSkill.name;
      console.error(`[md-to-wechat] Auto-selected formatter: ${selectedSkill.name}`);
    }

    if (!effectiveTheme && selectedSkill.themes.length > 0) {
      effectiveTheme = selectedSkill.themes[0];
      console.error(`[md-to-wechat] Using theme: ${effectiveTheme}`);
    }
  }

  // 主题映射（baoyu 主题 → wechat-formatter 主题）
  const themeMapping: Record<string, string> = {
    'default': 'wuxin',
    'grace': 'wuxin',
    'simple': 'petcircle',
  };

  // 如果使用 wechat-formatter 且提供了 baoyu 主题，进行映射
  if (effectiveSkill === 'wechat-formatter' && effectiveTheme && themeMapping[effectiveTheme]) {
    console.error(`[md-to-wechat] Mapping baoyu theme '${effectiveTheme}' to '${themeMapping[effectiveTheme]}'`);
    effectiveTheme = themeMapping[effectiveTheme];
  }

  // 使用选择的格式化器
  const result = await convertMarkdown(markdownPath, { title, theme: effectiveTheme });
  console.log(JSON.stringify(result, null, 2));
}

await main().catch((err) => {
  console.error(`Error: ${err instanceof Error ? err.message : String(err)}`);
  process.exit(1);
});

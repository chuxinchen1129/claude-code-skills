/**
 * 技能发现系统 - 自动发现符合标准契约的格式化器技能
 *
 * 功能：
 * - 扫描技能目录
 * - 检测标准接口契约
 * - 加载优先级配置
 * - 按优先级选择格式化器
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

/**
 * 格式化器技能信息
 */
export interface FormatterSkill {
  /** 技能名称 */
  name: string;
  /** 技能路径 */
  skillPath: string;
  /** 优先级（数字越小优先级越高） */
  priority: number;
  /** 支持的主题列表 */
  themes: string[];
  /** 中文名称（可选） */
  themesCn?: string[];
  /** 技能能力 */
  capabilities: string[];
  /** 命令行调用方式 */
  command: string;
  /** 是否支持 JSON 输出 */
  supportsJsonOutput: boolean;
}

/**
 * 优先级配置文件格式
 */
interface PriorityConfig {
  formatters: Array<{
    name: string;
    priority: number;
    path: string;
    themes: string[];
    themes_cn?: string[];
  }>;
}

/**
 * 技能发现类
 */
export class SkillDiscovery {
  private readonly searchPaths: string[];
  private readonly configPath: string;
  private cache: FormatterSkill[] | null = null;

  constructor() {
    // 技能搜索路径
    this.searchPaths = this.expandHomePaths([
      '~/.claude/skills/',
      '~/Desktop/DMS/skills/',
      '~/.claude/技能库/',
    ]);

    // 优先级配置文件路径
    this.configPath = path.join(os.homedir(), '.claude', 'skills', 'formatter-priority.yaml');
  }

  /**
   * 展开路径中的 ~ 符号
   */
  private expandHomePaths(paths: string[]): string[] {
    const home = os.homedir();
    return paths.map(p => p.replace(/^~/, home));
  }

  /**
   * 发现所有符合契约的格式化器技能
   */
  async discoverAll(): Promise<FormatterSkill[]> {
    if (this.cache) {
      return this.cache;
    }

    const skills: FormatterSkill[] = [];

    // 1. 扫描所有技能目录
    for (const searchPath of this.searchPaths) {
      if (!fs.existsSync(searchPath)) continue;

      const entries = fs.readdirSync(searchPath, { withFileTypes: true });
      for (const entry of entries) {
        if (!entry.isDirectory()) continue;

        const skillPath = path.join(searchPath, entry.name);
        const skillMdPath = path.join(skillPath, 'SKILL.md');

        // 检查是否有 SKILL.md
        if (!fs.existsSync(skillMdPath)) continue;

        // 检测是否符合契约
        const skill = await this.checkContract(skillPath, skillMdPath);
        if (skill) {
          skills.push(skill);
        }
      }
    }

    // 2. 加载优先级配置并排序
    const prioritizedSkills = this.applyPriorityConfig(skills);

    // 3. 缓存结果
    this.cache = prioritizedSkills;

    return prioritizedSkills;
  }

  /**
   * 检测技能是否符合标准接口契约
   */
  private async checkContract(skillPath: string, skillMdPath: string): Promise<FormatterSkill | null> {
    const content = fs.readFileSync(skillMdPath, 'utf-8');

    // 严格的检测：必须有 capabilities 字段且包含 markdown-to-html
    // 更好的方式：解析 YAML frontmatter 检查 capabilities
    const frontmatterMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    let hasMarkdownToHtml = false;
    let hasJsonOutput = false;

    if (frontmatterMatch) {
      const frontmatter = frontmatterMatch[1]!;
      // 检查 capabilities 字段中是否包含 markdown-to-html
      // 支持 YAML 格式：capabilities: \n  - markdown-to-html
      const capabilitiesMatch = frontmatter.match(/capabilities:\s*\n[^-]*-\s*markdown-to-html/mi);
      hasMarkdownToHtml = !!capabilitiesMatch;

      // 检查 capabilities 字段中是否包含 json-output
      const jsonOutputMatch = frontmatter.match(/capabilities:\s*\n[^-]*-\s*json-output/mi);
      hasJsonOutput = !!jsonOutputMatch;
    }

    if (!hasMarkdownToHtml) return null;

    // 解析 frontmatter 获取技能名称
    const name = this.extractName(content) || path.basename(skillPath);

    // 检测命令行调用方式
    const command = this.detectCommand(skillPath);
    if (!command) return null;

    // 检测支持的主题
    const themes = this.extractThemes(content);

    return {
      name,
      skillPath,
      priority: 999, // 默认低优先级，会被配置覆盖
      themes,
      themesCn: this.extractThemesCn(content),
      capabilities: ['markdown-to-html'],
      command,
      supportsJsonOutput: hasJsonOutput,
    };
  }

  /**
   * 从 SKILL.md 中提取技能名称
   */
  private extractName(content: string): string | null {
    // 尝试从 frontmatter 提取
    const nameMatch = content.match(/^name:\s*(.+)$/m);
    if (nameMatch) return nameMatch[1]!.trim();

    // 尝试从 description 提取
    const descMatch = content.match(/^description:\s*(.+)$/m);
    if (descMatch) return descMatch[1]!.trim();

    return null;
  }

  /**
   * 检测命令行调用方式
   */
  private detectCommand(skillPath: string): string | null {
    const scriptsPath = path.join(skillPath, 'scripts');

    // 查找 Python 脚本
    if (fs.existsSync(scriptsPath)) {
      const pyFiles = fs.readdirSync(scriptsPath)
        .filter(f => f.endsWith('.py'))
        .map(f => path.join(scriptsPath, f));

      for (const pyFile of pyFiles) {
        const content = fs.readFileSync(pyFile, 'utf-8');
        if (content.includes('json') || content.includes('--json')) {
          return `python ${pyFile}`;
        }
      }
    }

    // 查找 TypeScript 脚本
    const tsFiles = fs.readdirSync(skillPath)
      .filter(f => f.endsWith('.ts'))
      .map(f => path.join(skillPath, f));

    for (const tsFile of tsFiles) {
      const content = fs.readFileSync(tsFile, 'utf-8');
      if (content.includes('json') || content.includes('--json')) {
        return `npx -y bun ${tsFile}`;
      }
    }

    return null;
  }

  /**
   * 提取支持的主题
   */
  private extractThemes(content: string): string[] {
    const themes: string[] = [];

    // 匹配 wechat-formatter 的主题
    const wuxinMatch = content.match(/wuxin|悟昕/i);
    if (wuxinMatch) themes.push('wuxin');

    const petcircleMatch = content.match(/petcircle|宠圈|宠商圈/i);
    if (petcircleMatch) themes.push('petcircle');

    // 匹配 baoyu 的主题
    const defaultMatch = content.match(/\bdefault\b/i);
    if (defaultMatch) themes.push('default');

    const graceMatch = content.match(/\bgrace\b/i);
    if (graceMatch) themes.push('grace');

    const simpleMatch = content.match(/\bsimple\b/i);
    if (simpleMatch) themes.push('simple');

    return themes.length > 0 ? themes : ['default'];
  }

  /**
   * 提取主题中文名称
   */
  private extractThemesCn(content: string): string[] {
    const themesCn: string[] = [];

    if (content.includes('悟昕')) themesCn.push('悟昕');
    if (content.includes('宠圈') || content.includes('宠商圈')) themesCn.push('宠圈');

    return themesCn;
  }

  /**
   * 应用优先级配置
   */
  private applyPriorityConfig(skills: FormatterSkill[]): FormatterSkill[] {
    // 尝试加载配置文件
    if (!fs.existsSync(this.configPath)) {
      // 没有配置文件，按名称排序
      return skills.sort((a, b) => a.name.localeCompare(b.name));
    }

    try {
      let configContent = fs.readFileSync(this.configPath, 'utf-8');

      // 展开路径中的 ~ 符号
      configContent = configContent.replace(/~\//g, os.homedir() + '/');

      // 简单的 YAML 解析（只解析我们需要的格式）
      const config = this.parseSimpleYaml(configContent) as PriorityConfig;

      // 创建优先级映射
      const priorityMap = new Map<string, number>();
      const themeMap = new Map<string, string[]>();
      const themeCnMap = new Map<string, string[]>();

      for (const formatter of config.formatters || []) {
        priorityMap.set(formatter.name, formatter.priority);
        if (formatter.themes) themeMap.set(formatter.name, formatter.themes);
        if (formatter.themes_cn) themeCnMap.set(formatter.name, formatter.themes_cn);
      }

      // 应用配置
      const configuredSkills = skills.map(skill => {
        const configuredPriority = priorityMap.get(skill.name);
        const configuredThemes = themeMap.get(skill.name);
        const configuredThemesCn = themeCnMap.get(skill.name);

        return {
          ...skill,
          priority: configuredPriority ?? skill.priority,
          themes: configuredThemes ?? skill.themes,
          themesCn: configuredThemesCn ?? skill.themesCn,
        };
      });

      // 按优先级排序
      return configuredSkills.sort((a, b) => a.priority - b.priority);
    } catch (error) {
      console.error(`[SkillDiscovery] Failed to load priority config: ${error}`);
      return skills.sort((a, b) => a.name.localeCompare(b.name));
    }
  }

  /**
   * 简单的 YAML 解析器（只解析我们需要的格式）
   */
  private parseSimpleYaml(content: string): unknown {
    const result: Record<string, unknown> = { formatters: [] };
    const lines = content.split('\n');
    let currentFormatter: Record<string, unknown> | null = null;
    let inArray = false;

    for (const line of lines) {
      const trimmed = line.trim();

      // 跳过注释和空行
      if (!trimmed || trimmed.startsWith('#')) continue;

      // formatters:
      if (trimmed.startsWith('formatters:')) {
        inArray = true;
        continue;
      }

      // - name: xxx
      const listItemMatch = line.match(/^\s*-\s*name:\s*(.+)$/);
      if (listItemMatch) {
        if (currentFormatter) {
          (result.formatters as Array<Record<string, unknown>>).push(currentFormatter);
        }
        currentFormatter = { name: listItemMatch[1]!.trim() };
        continue;
      }

      // 子属性
      // 匹配格式：key: value（不 trim，保留缩进信息）
      const propertyMatch = line.match(/^(\s*)(\w+):\s*(.+)$/);

      if (propertyMatch && currentFormatter) {
        const key = propertyMatch[2]!;
        let value: unknown = propertyMatch[3]!.trim();

        // 处理数组格式（themes 和 themes_cn）
        if ((key === 'themes' || key === 'themes_cn') && typeof value === 'string') {
          const arrayItems: string[] = [];
          const arrayMatch = (value as string).match(/^\[(.*)\]$/);
          if (arrayMatch) {
            arrayItems.push(...arrayMatch[1]!.split(',').map(s => s.trim()));
          }
          value = arrayItems;
        }

        // 转换数字
        if (key === 'priority' && typeof value === 'string') {
          value = parseInt(value as string, 10);
        }

        currentFormatter[key] = value;
      }
    }

    if (currentFormatter) {
      (result.formatters as Array<Record<string, unknown>>).push(currentFormatter);
    }

    return result;
  }

  /**
   * 按优先级选择格式化器
   */
  async selectFormatter(skillName?: string, theme?: string): Promise<FormatterSkill | null> {
    const skills = await this.discoverAll();

    // 如果指定了技能名称
    if (skillName) {
      const skill = skills.find(s => s.name === skillName || s.name.includes(skillName));
      if (skill) return skill;
    }

    // 如果指定了主题，查找支持该主题的格式化器
    if (theme) {
      const skill = skills.find(s => s.themes.includes(theme));
      if (skill) return skill;
    }

    // 返回优先级最高的
    return skills[0] || null;
  }

  /**
   * 列出所有可用格式化器（用于 CLI 输出）
   */
  async listFormatters(): Promise<string> {
    const skills = await this.discoverAll();

    if (skills.length === 0) {
      return 'No formatter skills found.';
    }

    const lines: string[] = [];
    lines.push('Available formatter skills:');
    lines.push('');

    for (const skill of skills) {
      const themes = skill.themes.join(', ');
      const themesCn = skill.themesCn?.join(', ');
      const cnInfo = themesCn ? ` (${themesCn})` : '';

      lines.push(`  ${skill.name} [priority: ${skill.priority}]`);
      lines.push(`    Themes: ${themes}${cnInfo}`);
      lines.push(`    Command: ${skill.command}`);
      lines.push('');
    }

    return lines.join('\n');
  }

  /**
   * 清除缓存
   */
  clearCache(): void {
    this.cache = null;
  }
}

/**
 * CLI 入口
 */
async function main(): Promise<void> {
  const args = process.argv.slice(2);

  const discovery = new SkillDiscovery();

  if (args.includes('--list') || args.includes('-l')) {
    const list = await discovery.listFormatters();
    console.log(list);
    return;
  }

  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
Skill Discovery - 自动发现格式化器技能

Usage:
  npx -y bun skill-discovery.ts [options]

Options:
  --list, -l     列出所有可用的格式化器技能
  --help, -h     显示此帮助信息

Examples:
  npx -y bun skill-discovery.ts --list
`);
    return;
  }

  // 默认行为：列出所有格式化器
  const list = await discovery.listFormatters();
  console.log(list);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(err => {
    console.error(`Error: ${err instanceof Error ? err.message : String(err)}`);
    process.exit(1);
  });
}
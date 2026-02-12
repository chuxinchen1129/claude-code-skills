---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
license: Complete terms in LICENSE.txt
---

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific domains or tasks.

### What Skills Provide

1. **Specialized workflows** - Multi-step procedures for specific domains
2. **Tool integrations** - Instructions for working with specific file formats or APIs
3. **Domain expertise** - Company-specific knowledge, schemas, business logic
4. **Bundled resources** - Scripts, references, and assets for complex tasks

## Core Principles

### Concise is Key

The context window is a public good. Default assumption: Claude is already very smart. Only add context Claude doesn't already have.

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

- **High freedom**: Text-based instructions when multiple approaches are valid
- **Medium freedom**: Pseudocode or scripts with parameters
- **Low freedom**: Specific scripts with few parameters for error-prone operations

### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/ - Executable code
    ├── references/ - Documentation
    └── assets/ - Files for output
```

#### SKILL.md (required)

**Frontmatter** (YAML):
- `name`: The skill name
- `description`: Primary triggering mechanism - when to use the skill

**Body** (Markdown): Instructions and guidance

#### Bundled Resources (optional)

**scripts/**: Executable code for tasks requiring deterministic reliability

**references/**: Documentation loaded as needed (schemas, API docs, policies)

**assets/**: Files used in output (templates, logos, fonts)

### Progressive Disclosure

Three-level loading system:
1. **Metadata** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude

**Patterns**:
- High-level guide with references
- Domain-specific organization
- Conditional details

## Skill Creation Process

1. **Understand the skill** with concrete examples
2. **Plan reusable contents** (scripts, references, assets)
3. **Initialize the skill** (run init_skill.py)
4. **Edit the skill** (implement resources and write SKILL.md)
5. **Package the skill** (run package_skill.py)
6. **Iterate** based on real usage

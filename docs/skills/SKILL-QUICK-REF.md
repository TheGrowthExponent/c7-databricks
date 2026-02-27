# SKILL.md Format Quick Reference

## 🚀 Quick Start

### 1. Get Today's Date (REQUIRED FIRST)
```bash
# Linux/macOS
date +%Y-%m-%d

# Windows PowerShell
Get-Date -Format "yyyy-MM-dd"
```

### 2. Copy Template
```bash
cp docs/skills/SKILL-TEMPLATE.md docs/skills/[category]/SKILL.md
```

### 3. Add Required Frontmatter

```yaml
---
title: "[Category] Skills"
description: "Brief description (max 500 chars)"
category: "category-slug"
tags: ["tag1", "tag2", "tag3", "tag4", "tag5"]
priority: "high|medium|low"
skills_count: 5
last_updated: YYYY-MM-DD  # Use date from step 1
version: "1.0.0"
status: "active|partial|draft"
---
```

---

## ✅ Required Fields

| Field | Format | Example |
|-------|--------|---------|
| `title` | Quoted string | `"AI & Agents Skills"` |
| `description` | Quoted string (max 500) | `"Build intelligent applications..."` |
| `category` | Lowercase-hyphenated | `"ai-agents"` |
| `tags` | Array of strings | `["ai", "agents", "rag"]` |
| `last_updated` | YYYY-MM-DD | `2026-02-27` |
| `version` | Quoted semver | `"1.0.0"` |

---

## ⭐ Recommended Fields

| Field | Values | Example |
|-------|--------|---------|
| `priority` | high/medium/low | `"high"` |
| `skills_count` | Number | `5` |
| `status` | active/partial/draft | `"partial"` |

---

## 🚫 Common Mistakes

### ❌ Missing Quotes
```yaml
title: AI & Agents Skills  # WRONG
```
```yaml
title: "AI & Agents Skills"  # CORRECT
```

### ❌ Wrong Date Format
```yaml
last_updated: 02/27/2026  # WRONG
```
```yaml
last_updated: 2026-02-27  # CORRECT
```

### ❌ Category Doesn't Match Directory
```yaml
# In ai-agents/SKILL.md
category: "ai_agents"  # WRONG
```
```yaml
# In ai-agents/SKILL.md
category: "ai-agents"  # CORRECT
```

### ❌ Hardcoded Date
```yaml
# Without checking CLI first
last_updated: 2026-02-27  # WRONG
```
```bash
# Get date from CLI FIRST
$ date +%Y-%m-%d
2026-02-27

# Then use in YAML
last_updated: 2026-02-27  # CORRECT
```

---

## 📋 Validation Checklist

- [ ] File starts with `---`
- [ ] All required fields present
- [ ] All strings are quoted
- [ ] Category matches directory name
- [ ] Date from CLI (not hardcoded)
- [ ] Date in YYYY-MM-DD format
- [ ] Version is quoted semver
- [ ] Tags array has 5-15 items
- [ ] No YAML syntax errors
- [ ] Blank line after closing `---`

---

## 🔗 Full Documentation

- **Complete Guide**: [SKILL-FORMAT-GUIDE.md](SKILL-FORMAT-GUIDE.md)
- **Template**: [SKILL-TEMPLATE.md](SKILL-TEMPLATE.md)
- **Implementation**: [../../SKILL-FORMAT-IMPLEMENTATION.md](../../SKILL-FORMAT-IMPLEMENTATION.md)
- **Date Rule**: [../../.zed/rules.md](../../.zed/rules.md) (DATE-CLI-001)

---

## 📝 Example: Complete Frontmatter

```yaml
---
title: "AI & Agents Skills"
description: "Build intelligent applications with AI agents, vector search, and natural language interfaces"
category: "ai-agents"
tags:
  [
    "ai",
    "agents",
    "vector-search",
    "rag",
    "model-serving",
    "genie",
    "chatbots",
    "semantic-search",
    "llm",
  ]
priority: "high"
skills_count: 5
last_updated: 2026-02-27
version: "1.0.0"
status: "partial"
---

# AI & Agents Skills

Your content starts here...
```

---

## 🎯 Remember

1. **Always** get date from CLI first (Rule DATE-CLI-001)
2. **Always** use quotes around strings
3. **Always** match category to directory name
4. **Always** use YYYY-MM-DD date format
5. **Always** validate YAML syntax before committing

---

**Quick Tip**: If Context7 shows "Missing or invalid frontmatter", check:
1. File starts with `---`
2. All required fields present
3. YAML syntax is valid (quotes, commas, indentation)
4. Date format is correct

---

**Last Updated**: 2026-02-27
**Version**: 1.0.0

# SKILL.md Format Guide for Context7

## 📋 Overview

This guide defines the required format for all `SKILL.md` files in the c7-databricks repository to ensure proper parsing by Context7's documentation system.

**Last Updated**: 2026-02-27
**Version**: 1.0.0
**Status**: Active

---

## 🎯 Purpose

Context7 requires specific YAML frontmatter in all `SKILL.md` files to:
- Enable proper indexing and searchability
- Provide metadata for AI assistants
- Support version tracking and categorization
- Facilitate filtering by tags and priority
- Ensure consistent documentation structure

---

## ✅ Required Format

### 1. YAML Frontmatter (REQUIRED)

Every `SKILL.md` file **MUST** start with YAML frontmatter enclosed by `---` delimiters:

```markdown
---
title: "Skill Category Name"
description: "Brief description of the skill category"
category: "category-slug"
tags: ["tag1", "tag2", "tag3"]
priority: "high|medium|low"
skills_count: 5
last_updated: 2026-02-27
version: "1.0.0"
status: "active|partial|draft"
---
```

### 2. Frontmatter Fields

#### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | String | Display title of the skill document | `"AI & Agents Skills"` |
| `description` | String | Brief description (max 500 chars) | `"Build intelligent applications..."` |
| `category` | String | Category slug (lowercase-hyphenated) | `"ai-agents"` |
| `tags` | Array | List of relevant keywords | `["ai", "agents", "rag"]` |
| `last_updated` | Date | ISO 8601 date (YYYY-MM-DD) | `2026-02-27` |
| `version` | String | Semantic version | `"1.0.0"` |

#### Recommended Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `priority` | String | Priority level: high/medium/low | `"high"` |
| `skills_count` | Number | Number of skills in document | `5` |
| `status` | String | Documentation status | `"active"` |

#### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `author` | String | Document maintainer | `"Databricks Team"` |
| `maintainer` | String | Current maintainer | `"Context7 Documentation Team"` |

---

## 📝 Complete Example

Here's a complete example of a properly formatted `SKILL.md` file:

```markdown
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

This directory contains skills and patterns for building AI applications and agents on Databricks.

## 📚 Skills Overview

### High Priority Skills

#### 1. Databricks Agent Bricks

**Status**: ⚠️ Not yet documented
**Priority**: HIGH
**Description**: Build production-ready AI agents using Databricks Agent Bricks framework

**Key Topics**:

- Agent creation and deployment
- Tool integration and function calling
- Agent monitoring and debugging

... (rest of content)
```

---

## 🔍 Field Guidelines

### Title Field

- Use title case
- Be descriptive but concise (max 100 characters)
- Include "Skills" suffix for category overviews
- Examples:
  - ✅ `"AI & Agents Skills"`
  - ✅ `"MLflow Skills"`
  - ✅ `"Data Engineering Skills"`
  - ❌ `"ai agents"` (not title case)
  - ❌ `"Skills"` (too vague)

### Description Field

- Write 1-2 sentences (max 500 characters)
- Focus on what users will learn/accomplish
- Avoid marketing language
- Examples:
  - ✅ `"Build intelligent applications with AI agents, vector search, and natural language interfaces"`
  - ✅ `"ETL pipelines, data processing, and workflow orchestration on Databricks"`
  - ❌ `"The best AI skills ever!"` (marketing)
  - ❌ `"Skills"` (not descriptive)

### Category Field

- Use lowercase with hyphens
- Match directory name
- Be specific and consistent
- Examples:
  - ✅ `"ai-agents"`
  - ✅ `"data-engineering"`
  - ✅ `"mlflow"`
  - ❌ `"AI Agents"` (not lowercase)
  - ❌ `"ai_agents"` (use hyphens, not underscores)

### Tags Field

- Use array format with brackets
- Lowercase, hyphenated keywords
- Include 5-15 relevant tags
- Order: specific → general
- Examples:
  ```yaml
  tags:
    [
      "ai",
      "agents",
      "vector-search",
      "rag",
      "model-serving",
    ]
  ```

### Last Updated Field

- **CRITICAL**: Always use CLI to get current date
- Format: ISO 8601 (YYYY-MM-DD)
- Never hardcode dates
- Get date using:
  ```bash
  # Linux/macOS
  date +%Y-%m-%d

  # Windows PowerShell
  Get-Date -Format "yyyy-MM-dd"
  ```
- Examples:
  - ✅ `2026-02-27`
  - ❌ `02/27/2026` (wrong format)
  - ❌ `February 27, 2026` (wrong format)

### Version Field

- Use semantic versioning (major.minor.patch)
- Start new documents at `"1.0.0"`
- Increment appropriately:
  - Patch (1.0.1): Minor fixes, typos
  - Minor (1.1.0): New examples, sections
  - Major (2.0.0): Restructuring, breaking changes
- Always use string format with quotes
- Examples:
  - ✅ `"1.0.0"`
  - ✅ `"2.1.3"`
  - ❌ `1.0.0` (missing quotes)
  - ❌ `"v1.0.0"` (don't include 'v' prefix)

### Priority Field

- Use one of three values:
  - `"high"`: Urgent, frequently requested
  - `"medium"`: Important but not urgent
  - `"low"`: Nice to have, rare use cases
- Lowercase only
- Always quoted
- Examples:
  - ✅ `"high"`
  - ❌ `"HIGH"` (not lowercase)
  - ❌ `high` (missing quotes)

### Status Field

- Use one of:
  - `"active"`: Complete, well-maintained
  - `"partial"`: Incomplete, needs enhancement
  - `"draft"`: In progress, not ready
- Lowercase only
- Always quoted
- Examples:
  - ✅ `"active"`
  - ✅ `"partial"`
  - ❌ `"Active"` (not lowercase)

---

## 🚫 Common Mistakes

### Missing Frontmatter

❌ **Wrong**:
```markdown
# AI & Agents Skills

This directory contains...
```

✅ **Correct**:
```markdown
---
title: "AI & Agents Skills"
description: "Build intelligent applications..."
category: "ai-agents"
tags: ["ai", "agents"]
last_updated: 2026-02-27
version: "1.0.0"
---

# AI & Agents Skills

This directory contains...
```

### Invalid YAML Syntax

❌ **Wrong**:
```yaml
---
title: AI & Agents Skills  # Missing quotes
tags: [ai agents]  # Missing quotes in array
last_updated: 02/27/2026  # Wrong date format
---
```

✅ **Correct**:
```yaml
---
title: "AI & Agents Skills"
tags: ["ai", "agents"]
last_updated: 2026-02-27
---
```

### Inconsistent Category Names

❌ **Wrong**:
```yaml
category: "AI_Agents"    # Underscore instead of hyphen
category: "ai agents"    # Space instead of hyphen
category: "AIAgents"     # No separator
```

✅ **Correct**:
```yaml
category: "ai-agents"
```

### Hardcoded Dates

❌ **Wrong**:
```yaml
last_updated: 2026-02-27  # Hardcoded without checking
```

✅ **Correct**:
```bash
# First get the date from CLI
$ date +%Y-%m-%d
2026-02-27

# Then use it in YAML
last_updated: 2026-02-27
```

---

## 📋 Validation Checklist

Before committing a `SKILL.md` file, verify:

- [ ] Frontmatter starts and ends with `---` on separate lines
- [ ] All required fields present: `title`, `description`, `category`, `tags`, `last_updated`, `version`
- [ ] Title is quoted and descriptive (max 100 chars)
- [ ] Description is quoted and concise (max 500 chars)
- [ ] Category matches directory name (lowercase-hyphenated)
- [ ] Tags array has 5-15 relevant keywords
- [ ] Last updated date retrieved from CLI (not hardcoded)
- [ ] Date format is ISO 8601 (YYYY-MM-DD)
- [ ] Version uses semantic versioning with quotes
- [ ] Priority is one of: high, medium, low (if present)
- [ ] Status is one of: active, partial, draft (if present)
- [ ] No syntax errors in YAML (check indentation)
- [ ] Frontmatter is followed by blank line before content

---

## 🔧 Tools & Scripts

### Get Today's Date

**Linux/macOS:**
```bash
date +%Y-%m-%d
```

**Windows PowerShell:**
```powershell
Get-Date -Format "yyyy-MM-dd"
```

**Windows CMD:**
```cmd
echo %date:~10,4%-%date:~4,2%-%date:~7,2%
```

### Validate YAML Frontmatter

Use online YAML validators or Python:

```python
import yaml

frontmatter = """
---
title: "AI & Agents Skills"
description: "Build intelligent applications"
category: "ai-agents"
tags: ["ai", "agents"]
last_updated: 2026-02-27
version: "1.0.0"
---
"""

# Extract YAML between --- delimiters
yaml_content = frontmatter.split('---')[1]

# Validate
try:
    data = yaml.safe_load(yaml_content)
    print("✅ Valid YAML")
    print(data)
except yaml.YAMLError as e:
    print(f"❌ Invalid YAML: {e}")
```

---

## 📖 Context7 Parsing Behavior

### What Context7 Checks

1. **Presence of frontmatter**: File must start with `---`
2. **Valid YAML syntax**: No syntax errors
3. **Required fields**: Must have title, description, category
4. **Date format**: Must be ISO 8601 (YYYY-MM-DD)
5. **Array format**: Tags must be valid YAML array

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Missing or invalid frontmatter" | No `---` delimiters or missing fields | Add complete frontmatter |
| YAML parsing error | Syntax error in frontmatter | Check quotes, commas, indentation |
| Invalid date format | Date not in YYYY-MM-DD | Use `date +%Y-%m-%d` |

### After Fixing

After adding/fixing frontmatter:
1. Commit changes to Git
2. Push to GitHub
3. Context7 will re-parse on next sync (automatic)
4. Check Context7 dashboard for success

---

## 🎓 Examples by Category

### Overview File (docs/skills/SKILL.md)

```yaml
---
title: "Databricks Skills Reference"
description: "A comprehensive guide to skills and patterns for building on Databricks"
category: "overview"
tags: ["skills", "patterns", "databricks", "reference"]
skills_count: 24
last_updated: 2026-02-27
version: "1.0.0"
status: "active"
---
```

### Category File (ai-agents/SKILL.md)

```yaml
---
title: "AI & Agents Skills"
description: "Build intelligent applications with AI agents, vector search, and natural language interfaces"
category: "ai-agents"
tags: ["ai", "agents", "vector-search", "rag", "model-serving"]
priority: "high"
skills_count: 5
last_updated: 2026-02-27
version: "1.0.0"
status: "partial"
---
```

### Specialty File (mlflow/SKILL.md)

```yaml
---
title: "MLflow Skills"
description: "Experiment tracking, model management, and observability for ML workflows"
category: "mlflow"
tags: ["mlflow", "experiment-tracking", "model-registry", "tracing"]
priority: "medium"
skills_count: 8
last_updated: 2026-02-27
version: "1.0.0"
status: "partial"
---
```

---

## 🚀 Quick Start Workflow

### Creating a New SKILL.md

1. **Copy the template:**
   ```bash
   cp docs/skills/SKILL-TEMPLATE.md docs/skills/new-category/SKILL.md
   ```

2. **Get today's date:**
   ```bash
   date +%Y-%m-%d
   # Output: 2026-02-27
   ```

3. **Update frontmatter:**
   - Replace placeholders with actual values
   - Use the date from step 2
   - Set appropriate priority and status

4. **Fill in content:**
   - Add skill descriptions
   - Include code examples
   - Add best practices

5. **Validate:**
   - Check YAML syntax
   - Verify all required fields
   - Test date format

6. **Commit:**
   ```bash
   git add docs/skills/new-category/SKILL.md
   git commit -m "docs: add new-category skills documentation"
   git push
   ```

### Updating Existing SKILL.md

1. **Get today's date:**
   ```bash
   date +%Y-%m-%d
   ```

2. **Update frontmatter:**
   - Update `last_updated` field with new date
   - Increment `version` if needed
   - Update `status` if changed

3. **Make content changes**

4. **Commit with descriptive message:**
   ```bash
   git commit -m "docs: update ai-agents skills with new examples"
   ```

---

## 📚 Reference Documents

### Internal References

- [SKILL.md Template](SKILL-TEMPLATE.md) - Use as starting point
- [Date Rule Documentation](.zed/rules.md) - DATE-CLI-001 rule
- [Main Skills Overview](SKILL.md) - Example of complete document

### External References

- [YAML Specification](https://yaml.org/spec/1.2/spec.html)
- [ISO 8601 Date Format](https://en.wikipedia.org/wiki/ISO_8601)
- [Semantic Versioning](https://semver.org/)
- [Context7 Documentation](https://context7.mintlify.dev/docs/adding-libraries)

---

## 🤝 Contributing

When contributing SKILL.md files:

1. **Always use the template** from `SKILL-TEMPLATE.md`
2. **Follow this format guide** exactly
3. **Get date from CLI** - never hardcode
4. **Validate YAML** before committing
5. **Test locally** if possible
6. **Update version** appropriately
7. **Add descriptive commit messages**

---

## 🔍 Troubleshooting

### Context7 Not Parsing File

**Symptom**: File shows "Missing or invalid frontmatter" in logs

**Diagnosis**:
```bash
# Check if frontmatter exists
head -n 20 docs/skills/category/SKILL.md

# Validate YAML
python -c "import yaml; yaml.safe_load(open('docs/skills/category/SKILL.md').read().split('---')[1])"
```

**Solutions**:
1. Ensure file starts with `---` on line 1
2. Check for YAML syntax errors (quotes, commas)
3. Verify all required fields present
4. Confirm proper indentation (2 spaces)

### Date Format Errors

**Symptom**: Date not recognized or parsing errors

**Check**:
```bash
# Verify date format
grep "last_updated:" docs/skills/category/SKILL.md
# Should output: last_updated: 2026-02-27
```

**Fix**:
```bash
# Get correct format
TODAY=$(date +%Y-%m-%d)
echo $TODAY

# Update file with correct date
```

### YAML Syntax Errors

**Common Issues**:
- Missing quotes around strings
- Wrong array syntax
- Incorrect indentation
- Missing colons

**Validation**:
```python
import yaml

with open('docs/skills/category/SKILL.md') as f:
    content = f.read()
    yaml_part = content.split('---')[1]

try:
    yaml.safe_load(yaml_part)
    print("✅ Valid")
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## 📞 Support

For questions about SKILL.md format:

1. Review this guide thoroughly
2. Check existing SKILL.md files as examples
3. Validate YAML syntax
4. Check Context7 parsing logs
5. Consult [Context7 Documentation](https://context7.mintlify.dev/)

---

## 📊 Summary

### Must Have (Required)

- ✅ YAML frontmatter with `---` delimiters
- ✅ `title` field (quoted string, max 100 chars)
- ✅ `description` field (quoted string, max 500 chars)
- ✅ `category` field (lowercase-hyphenated)
- ✅ `tags` array (5-15 keywords)
- ✅ `last_updated` date (ISO 8601: YYYY-MM-DD)
- ✅ `version` field (semantic versioning)

### Should Have (Recommended)

- ⭐ `priority` field (high/medium/low)
- ⭐ `skills_count` field (number of skills)
- ⭐ `status` field (active/partial/draft)

### Nice to Have (Optional)

- 💡 `author` field
- 💡 `maintainer` field
- 💡 Custom metadata fields

---

**Remember**: Context7 parsing is strict. Follow this guide exactly to ensure your SKILL.md files are properly indexed and searchable.

---

**Last Updated**: 2026-02-27
**Version**: 1.0.0
**Maintainer**: Context7 Documentation Team

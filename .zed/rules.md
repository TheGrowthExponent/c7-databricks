# Custom Rules for c7-databricks Repository

This document contains custom rules and workflows for the Databricks Documentation Accuracy Validation Agent.

---

## Rule 1: Get Today's Date from CLI Before Adding Last Updated Dates

**Rule ID:** `DATE-CLI-001`
**Priority:** High
**Category:** File Metadata Management
**Status:** Active

### Purpose

Ensure accurate and consistent "Last Updated" timestamps in documentation files by retrieving the current date from the system CLI before applying it to files.

### When This Rule Applies

- Before adding or updating "Last Updated" metadata in any documentation file
- Before generating automated documentation updates
- Before committing changes that include timestamp modifications
- During batch file updates that require consistent dating

### Required Steps

#### 1. Retrieve Current Date from CLI

**Windows (PowerShell):**

```powershell
Get-Date -Format "yyyy-MM-dd"
```

**Windows (Command Prompt):**

```cmd
echo %date:~10,4%-%date:~4,2%-%date:~7,2%
```

**Linux/macOS (Bash/sh):**

```bash
date +%Y-%m-%d
```

#### 2. Validate Date Format

- Ensure the date follows ISO 8601 format: `YYYY-MM-DD`
- Verify the date is valid (not a future date or obviously incorrect)
- Example valid date: `2026-02-27`

#### 3. Apply Date to Files

Once the date is retrieved and validated:

**For Markdown Files:**

```markdown
---
title: Document Title
last_updated: 2026-02-27
---
```

**For JSON Metadata:**

```json
{
  "lastUpdated": "2026-02-27",
  "modifiedBy": "agent"
}
```

**For Python Docstrings:**

```python
"""
Module description.

Last Updated: 2026-02-27
"""
```

### Workflow Example

```bash
# Step 1: Get today's date
$ date +%Y-%m-%d
2026-02-27

# Step 2: Apply to documentation file
# Update the frontmatter or metadata section with: last_updated: 2026-02-27

# Step 3: Commit with descriptive message
git commit -m "docs: update last_updated date to 2026-02-27 in [filename]"
```

### Automation Script (Optional)

For batch updates, create a helper script:

**update_dates.sh:**

```bash
#!/bin/bash
TODAY=$(date +%Y-%m-%d)
echo "Today's date: $TODAY"
echo "Ready to update files with this date."
```

**update_dates.ps1:**

```powershell
$TODAY = Get-Date -Format "yyyy-MM-dd"
Write-Host "Today's date: $TODAY"
Write-Host "Ready to update files with this date."
```

### Validation Checklist

Before committing files with updated dates:

- [ ] Date retrieved from CLI (not hardcoded)
- [ ] Date format is `YYYY-MM-DD`
- [ ] Date is accurate (matches current system date)
- [ ] All files in the batch use the same date (consistency)
- [ ] Commit message includes the date applied
- [ ] No future dates accidentally applied

### Anti-Patterns (DO NOT DO)

❌ **Hardcoding dates without CLI verification:**

```markdown
last_updated: 2026-02-27 # Don't assume the date
```

❌ **Using inconsistent date formats:**

```markdown
last_updated: 02/27/2026 # Wrong format
last_updated: February 27, 2026 # Wrong format
last_updated: 27-02-2026 # Wrong format
```

❌ **Using different dates in the same commit:**

```markdown
# file1.md

last_updated: 2026-02-27

# file2.md (same commit)

last_updated: 2026-02-26 # Inconsistent!
```

### Integration with Validation System

The validation system should check:

1. All `last_updated` fields use ISO 8601 format
2. Dates are not in the future
3. Dates are reasonable (not older than repository creation)
4. Batch updates use consistent dates

### Related Rules

- `GIT-COMMIT-001`: Commit message standards
- `METADATA-001`: File metadata requirements
- `VALIDATION-001`: Pre-commit validation checks

### References

- ISO 8601 Date Format: https://en.wikipedia.org/wiki/ISO_8601
- Git Best Practices: https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project

---

## Rule 2: [Future Rule Placeholder]

Additional rules can be added below as needed.

---

## Rule Management

### Adding New Rules

1. Create a new section with a unique Rule ID
2. Include all required sections: Purpose, When This Rule Applies, Required Steps, etc.
3. Update this section with a reference to the new rule
4. Notify team members of the new rule

### Modifying Existing Rules

1. Update the rule content
2. Add a changelog entry at the bottom of the rule
3. Update the Status field if needed (Active, Deprecated, Under Review)

### Rule Status Values

- **Active**: Currently enforced
- **Draft**: Under development, not yet enforced
- **Under Review**: Being evaluated for changes
- **Deprecated**: No longer enforced, kept for reference

---

**Last Updated:** 2026-02-27
**Maintained By:** Databricks Documentation Accuracy Validation Agent
**Version:** 1.0.0

# 🚀 Agent Quick Reference Card

**For:** AI Assistants working on c7-databricks repository  
**Purpose:** Quick access to critical guidelines and rules

---

## ⚡ CRITICAL RULES (NEVER BREAK THESE)

### 🎯 The Three Commandments
1. **FOLLOW THE PLAN** → `docs/plan.md` is law. Ask before deviating.
2. **VERIFY EVERYTHING** → Check https://docs.databricks.com before writing.
3. **ASK WHEN UNSURE** → Better to ask than to guess wrong.

### ❌ NEVER Do This
- ❌ Make up information or guess
- ❌ Deviate from `docs/plan.md` without approval
- ❌ Include real tokens/credentials in examples
- ❌ Use outdated or unverified content
- ❌ Skip the validation checklist
- ❌ Leave broken links or non-working code

### ✅ ALWAYS Do This
- ✅ Verify against official Databricks docs
- ✅ Include source URLs in documentation
- ✅ Test all code examples
- ✅ Use environment variables for credentials
- ✅ Include error handling in examples
- ✅ Follow existing formatting patterns

---

## 📋 BEFORE WRITING ANY CONTENT

```
□ Check docs/plan.md - Is this task in the plan?
□ Find official source - What's the Databricks URL?
□ Verify current - Is this the latest version?
□ Check deprecation - Is this feature deprecated?
□ Review existing - What patterns are already used?
```

---

## 🔍 VALIDATION CHECKLIST

### Required for Every Document
- [ ] Official Databricks source URL included
- [ ] All API endpoints verified as current
- [ ] All code examples are runnable
- [ ] Error handling included in examples
- [ ] No hardcoded credentials
- [ ] Proper markdown formatting for Context7
- [ ] Cross-references to related docs
- [ ] Version compatibility noted

---

## 📚 ESSENTIAL SOURCES

### Primary (Always Check First)
- **Main Docs:** https://docs.databricks.com/
- **API Ref:** https://docs.databricks.com/api/
- **Python SDK:** https://docs.databricks.com/dev-tools/python-sdk.html
- **REST API:** https://docs.databricks.com/api/workspace/introduction
- **SQL Ref:** https://docs.databricks.com/sql/language-manual/

### Repository Files
- **The Plan:** `docs/plan.md` ← Your Bible
- **Status:** `PROJECT-STATUS.md` ← Current progress
- **Validation:** `VALIDATION-SYSTEM-DELIVERY.md` ← How to validate
- **Full Guide:** `.github/DATABRICKS-ACCURACY-AGENT.md` ← Complete instructions

---

## 🚦 WHEN TO ASK USER

### 🔴 STOP & ASK (Critical)
- Official docs contradict each other
- Can't verify critical information
- Need to deviate from plan
- Security concerns found
- Breaking changes detected

### 🟡 ASK SOON (Important)
- Found better approach than plan
- Discovered pattern inconsistency
- Need clarification on requirements
- Found gaps in existing docs

### 🟢 CONTINUE & MENTION (Minor)
- Found typos or minor issues
- Have optimization suggestions
- Noticed improvement opportunities

---

## 💻 CODE EXAMPLE REQUIREMENTS

### ✅ GOOD Example Template
```python
# Import required libraries
from databricks.sdk import WorkspaceClient
import os

# Initialize with environment variables (SECURE)
w = WorkspaceClient(
    host=os.getenv('DATABRICKS_HOST'),
    token=os.getenv('DATABRICKS_TOKEN')
)

try:
    # Main operation with clear comments
    result = w.jobs.list()
    
    # Process results
    for job in result:
        print(f"Job: {job.settings.name}")
        
except Exception as e:
    # Error handling included
    print(f"Error: {e}")
    # Add recovery logic here
```

### ❌ BAD Example (Never Do This)
```python
# NO imports
# NO error handling
# HARDCODED credentials
w = WorkspaceClient(host="https://my.databricks.com", token="dapi123...")
jobs = w.jobs.list()  # What if this fails?
```

---

## 📝 MARKDOWN FORMATTING FOR CONTEXT7

### Code Blocks (CRITICAL FORMAT)
```
Always use file path after triple backticks:
```/dev/null/example.py#L1-10
code here
```
```

### Headings (Proper Hierarchy)
```
# H1 - Document Title (one per file)
## H2 - Major Sections
### H3 - Subsections
#### H4 - Details
```

### Links (Always Verify)
```
[Link Text](https://docs.databricks.com/path)
```

---

## 🎯 PRIORITY LEVELS

| Priority | Fix Time | Examples |
|----------|----------|----------|
| **P0 Critical** | Immediately | Wrong API endpoint, security issue, broken code |
| **P1 High** | 24 hours | Missing required param, no error handling |
| **P2 Medium** | 1 week | Missing optional param, minor formatting |
| **P3 Low** | When possible | Additional examples, style improvements |

---

## 🔧 VALIDATION COMMANDS

```bash
# Before committing - check your work
python scripts/validate.py --mode pr

# Full validation - comprehensive check
python scripts/validate.py --mode full

# Check specific file
python scripts/validate.py --file docs/api/clusters.md

# Generate report
python scripts/validate.py --report
```

---

## 📊 QUALITY GATES (Must Pass)

```
✓ Accuracy Rate: ≥95%
✓ Critical Issues: 0
✓ High Priority Issues: ≤2
✓ Broken Links: 0
✓ Code Syntax: 100% correct
```

---

## 🎓 DECISION FLOWCHART

```
New Task
  ↓
Is it in docs/plan.md?
  ↓
 YES → Continue
  ↓
Can I find official Databricks docs?
  ↓
 YES → Continue
  ↓
Can I verify ALL details?
  ↓
 YES → Write content
  ↓
Does code work with error handling?
  ↓
 YES → Run validation
  ↓
All checks pass?
  ↓
 YES → Complete ✓

If ANY step is NO → ASK USER
```

---

## 🔐 SECURITY CHECKLIST

```
□ No hardcoded tokens/passwords/keys
□ Environment variables used for secrets
□ Security best practices documented
□ Proper authentication methods shown
□ Unity Catalog governance mentioned
```

---

## 📖 DOCUMENTATION STRUCTURE

```
Each Document Must Have:
├── Title (H1)
├── Purpose/Overview
├── Prerequisites
├── Official Source URL
├── Main Content
│   ├── Explanation
│   ├── Working Examples
│   └── Error Handling
├── Common Pitfalls
├── Related Topics
└── Version Info
```

---

## 🤝 COLLABORATION

### Commit Message Format
```
[Type] Brief description

- Detail 1
- Detail 2

Verified: [source URL]
```

Types: `feat`, `fix`, `docs`, `validate`, `refactor`

---

## 🎯 SUCCESS CHECKLIST (Per Task)

```
□ Followed docs/plan.md
□ Verified with official sources
□ All code examples tested
□ Error handling included
□ No security issues
□ Validation passed
□ Cross-references updated
□ PROJECT-STATUS.md updated
□ Ready for review
```

---

## 💡 QUICK TIPS

1. **Before starting:** Read the plan section for your task
2. **While writing:** Keep official docs open in browser
3. **After writing:** Run validation before asking for review
4. **If stuck:** Check full agent guide → `.github/DATABRICKS-ACCURACY-AGENT.md`
5. **When unsure:** ASK! Don't guess.

---

## 🚨 EMERGENCY CONTACTS

### Critical Issues Found?
1. Stop work immediately
2. Document the issue clearly
3. Tag issue with priority (P0)
4. Escalate to user
5. Wait for guidance

### Escalation Template
```markdown
## ESCALATION: [Brief Issue]

**Priority:** P0/P1/P2/P3
**Impact:** [What's affected]
**Issue:** [Clear description]
**Checked:** [Sources verified]
**Options:** [Possible solutions]
**Recommendation:** [Your suggestion]
**Question:** [Specific decision needed]
```

---

## 📈 METRICS TO TRACK

Track in `PROJECT-STATUS.md`:
- Files created/updated today
- Validation results
- Issues found and fixed
- Phase completion %
- Quality gates status

---

## 🎯 AGENT MANTRA

```
"I verify before I write.
 I follow the plan unless approved to deviate.
 I ask when uncertain.
 I maintain 100% accuracy.
 I leave documentation better than I found it."
```

---

## 📞 NEED HELP?

1. **Quick Answer:** Check this card
2. **Detailed Guide:** `.github/DATABRICKS-ACCURACY-AGENT.md`
3. **Project Plan:** `docs/plan.md`
4. **Current Status:** `PROJECT-STATUS.md`
5. **Validation System:** `VALIDATION-SYSTEM-DELIVERY.md`
6. **Still Stuck:** Ask the user!

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  

**Remember: Quality > Speed | Accuracy > Completeness | Ask > Guess**

---

*Print this. Pin it. Refer to it. Your guide to 100% accuracy.*
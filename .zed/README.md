# Zed Editor Configuration for c7-databricks

This directory contains Zed editor configuration for the **Databricks Documentation Accuracy Validation Agent** system.

---

## 📋 Overview

This configuration ensures that any AI assistant working in this project through Zed automatically:

1. Loads the agent initialization protocol
2. Follows the project plan strictly
3. Maintains 100% accuracy standards
4. Validates all work before committing

---

## 📁 Files in This Directory

### `settings.json`

**Purpose:** Project-specific Zed settings with AI assistant instructions

**Key Features:**

- **`assistant_instructions`**: Comprehensive initialization prompt that loads automatically
- **Code formatting**: Standardized formatting rules for consistency
- **File type mappings**: Proper syntax highlighting for all file types
- **Git integration**: Inline blame and git gutter enabled
- **Validation requirements**: Quality gates enforced before commits

### `prompt.md`

**Purpose:** Detailed AI assistant initialization and reference guide

**Contents:**

- Complete activation protocol overview
- The Three Commandments
- Critical rules (ALWAYS/NEVER)
- Code example standards
- Validation workflows
- Official source URLs
- Escalation procedures
- Security standards

### `rules.md`

**Purpose:** Custom rules and workflows for the repository

**Contents:**

- **Rule DATE-CLI-001**: Get Today's Date from CLI Before Adding Last Updated Dates
- Workflow examples and validation checklists
- Anti-patterns and best practices
- Integration with validation system
- Rule management guidelines

**Key Rule:** Before adding or updating "Last Updated" metadata in any documentation file, always retrieve the current date from the system CLI using:

- Windows (PowerShell): `Get-Date -Format "yyyy-MM-dd"`
- Linux/macOS/Git Bash: `date +%Y-%m-%d`

### `get-date.sh`

**Purpose:** Quick reference script to get today's date in ISO 8601 format

**Usage:**

```bash
./get-date.sh
```

**Output:** Displays current date in `YYYY-MM-DD` format for use in `last_updated` fields

### `get-date.ps1`

**Purpose:** PowerShell version of date retrieval script

**Usage:**

```powershell
.\get-date.ps1
```

**Output:** Displays current date in `YYYY-MM-DD` format with usage examples

---

## 🔧 How It Works

### 1. Automatic Loading

When you open this project in Zed, the AI assistant automatically receives:

- Full initialization instructions from `settings.json`
- Project-specific context and requirements
- Links to key reference files
- Quality standards and validation commands

### 2. Agent Activation

The AI assistant is instructed to:

1. Read `.github/AGENT-ACTIVATION.md` (mandatory first step)
2. Complete all 6 activation phases
3. Take the Agent Oath
4. Confirm readiness before starting work

### 3. Continuous Enforcement

Throughout the session:

- The assistant follows `docs/plan.md` strictly
- All information is verified against official Databricks sources
- Code examples are tested and secured
- Validation is run before commits
- Uncertainties are escalated to the user

---

## 🎯 The Three Commandments

These rules are embedded in the AI assistant configuration:

1. **FOLLOW THE PLAN**
   - `docs/plan.md` is law
   - Ask before deviating

2. **VERIFY EVERYTHING**
   - Check https://docs.databricks.com/ first
   - Include source URLs

3. **ASK WHEN UNSURE**
   - Don't guess, confirm
   - Escalate immediately

---

## 📜 Custom Rules & Helper Scripts

### Rule DATE-CLI-001: Get Today's Date from CLI

**Purpose:** Ensure accurate and consistent "Last Updated" timestamps in documentation files

**Quick Reference:**

```bash
# Get today's date (Linux/macOS/Git Bash)
date +%Y-%m-%d

# Get today's date (PowerShell)
Get-Date -Format "yyyy-MM-dd"
```

**Helper Scripts:**

- **Bash:** `.zed/get-date.sh` - Run to get today's date
- **PowerShell:** `.zed/get-date.ps1` - Run to get today's date with examples

**When to Use:**

- Before adding or updating `last_updated` metadata in any documentation file
- Before generating automated documentation updates
- Before committing changes that include timestamp modifications
- During batch file updates that require consistent dating

**Validation Checklist:**

- [ ] Date retrieved from CLI (not hardcoded)
- [ ] Date format is `YYYY-MM-DD` (ISO 8601)
- [ ] Date is accurate (matches current system date)
- [ ] All files in the batch use the same date
- [ ] Commit message includes the date applied
- [ ] No future dates accidentally applied

**Full Documentation:** See `rules.md` for complete details, examples, and anti-patterns

---

## 📊 Quality Gates

The configuration enforces these standards:

- ✅ Accuracy Rate: ≥95%
- ✅ Critical Issues: 0
- ✅ High Priority Issues: ≤2
- ✅ Broken Links: 0
- ✅ Code Syntax: 100% correct

---

## 🚀 Using This Configuration

### For Developers Using Zed AI Assistant

When you open this project in Zed and start the AI assistant:

1. **The assistant will automatically:**
   - Load the initialization instructions
   - Know it must read activation protocol
   - Understand the project structure
   - Follow quality standards

2. **First message from assistant should be:**

   ```
   AGENT ACTIVATED - READY FOR WORK
   (or working through activation phases)
   ```

3. **If assistant doesn't mention activation:**
   - Remind it to read `.github/AGENT-ACTIVATION.md`
   - Ask it to confirm the Three Commandments
   - Ensure it knows about `docs/plan.md`

### For Other AI Assistants

If using AI assistants outside Zed:

1. Manually share `.github/AGENT-ACTIVATION.md`
2. Reference `.github/AGENT-QUICK-REF.md` for daily use
3. Ensure assistant reads `docs/plan.md` before starting

---

## 🔍 Validation Workflow

The configuration includes validation commands:

```bash
# Before committing (MANDATORY)
python scripts/validate.py --mode pr

# Full validation
python scripts/validate.py --mode full

# Check specific file
python scripts/validate.py --file docs/api/clusters.md
```

---

## 📚 Key Reference Files

The configuration directs the AI assistant to these files:

### Must Read (In Order):

1. `.github/AGENT-ACTIVATION.md` - Initialization protocol
2. `docs/plan.md` - Project roadmap
3. `PROJECT-STATUS.md` - Current progress
4. `.github/DATABRICKS-ACCURACY-AGENT.md` - Full operational guide
5. `.github/AGENT-QUICK-REF.md` - Daily reference

---

## 🔐 Security Standards Enforced

The configuration ensures:

- ❌ No hardcoded credentials in examples
- ✅ Environment variables for sensitive data
- ✅ Security best practices documented
- ✅ Unity Catalog governance referenced

---

## 📖 Official Sources

The assistant is configured to verify against:

- **Main:** https://docs.databricks.com/
- **API:** https://docs.databricks.com/api/
- **Python SDK:** https://docs.databricks.com/dev-tools/python-sdk.html
- **REST API:** https://docs.databricks.com/api/workspace/introduction
- **SQL:** https://docs.databricks.com/sql/language-manual/

---

## ⚙️ Modifying This Configuration

### To Update Assistant Instructions:

Edit `settings.json` → `assistant_instructions.initialization`

**Important:**

- Keep The Three Commandments visible
- Maintain critical rules section
- Always reference activation protocol
- Include validation commands

### To Update Reference Guide:

Edit `prompt.md`

**Structure:**

- Mandatory initialization (top)
- Critical rules
- Workflows
- Code examples
- Escalation procedures

---

## 🎓 Agent Mantra

Embedded in the configuration:

```
"I verify before I write.
 I follow the plan unless approved to deviate.
 I ask when uncertain.
 I maintain 100% accuracy.
 I leave documentation better than I found it."
```

---

## ✅ Success Criteria

The configuration ensures every task:

- [ ] Follows `docs/plan.md`
- [ ] Verified with official sources
- [ ] Code examples tested
- [ ] Error handling included
- [ ] No security issues
- [ ] Validation passed
- [ ] Cross-references updated
- [ ] PROJECT-STATUS.md updated

---

## 🚨 Troubleshooting

### If AI Assistant Doesn't Follow Guidelines:

1. **Confirm activation:**
   - Ask: "Have you read .github/AGENT-ACTIVATION.md?"
   - Ask: "What are The Three Commandments?"

2. **Reset if needed:**
   - Close and reopen Zed
   - Clear AI assistant context
   - Manually share `.github/AGENT-ACTIVATION.md`

3. **Report issues:**
   - Document what guideline wasn't followed
   - Update `settings.json` to emphasize that rule
   - Consider adding to `prompt.md`

---

## 📈 Continuous Improvement

This configuration is a living document:

- Update based on lessons learned
- Add new validation patterns discovered
- Refine instructions for clarity
- Incorporate user feedback

---

## 🌟 Why This Configuration Exists

**The Problem:**

- AI assistants may not follow project standards
- Documentation accuracy can degrade
- Code examples might be insecure
- Plan deviations can occur silently

**The Solution:**

- Automatic initialization on project open
- Clear, embedded guidelines
- Mandatory activation protocol
- Continuous quality enforcement

**The Result:**

- 100% accurate documentation
- Plan adherence guaranteed
- Production-ready code examples
- Consistent quality standards

---

## 📞 Support

For questions about this configuration:

1. Review `.github/README.md` for agent system overview
2. Check `AGENT-SYSTEM-DELIVERY.md` for complete documentation
3. Consult `.github/DATABRICKS-ACCURACY-AGENT.md` for operational details

---

**Version:** 1.1.0
**Last Updated:** 2026-02-27
**Status:** Production-Ready ✅

**Changelog:**

- v1.1.0 (2026-02-27): Added custom rules section (DATE-CLI-001) and helper scripts
- v1.0.0 (2026-02-27): Initial configuration

---

_This Zed configuration ensures every AI assistant working on this project maintains the highest standards of accuracy and follows the established plan without deviation._

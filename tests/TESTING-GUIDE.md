# Databricks Documentation Testing & Validation Guide

Comprehensive guide for testing and validating the Databricks documentation repository to ensure 100% accuracy against official Databricks sources.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Validation System](#validation-system)
4. [Running Tests](#running-tests)
5. [Understanding Results](#understanding-results)
6. [Scheduled Validation](#scheduled-validation)
7. [Quality Gates](#quality-gates)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Overview

### What Gets Validated

The validation system checks documentation accuracy against official Databricks sources:

- ✅ **API Documentation** - Endpoints, parameters, request/response formats
- ✅ **Code Examples** - Syntax, imports, best practices
- ✅ **Configuration Values** - Keys, defaults, types
- ✅ **SDK References** - Method signatures, class names, types
- ✅ **SQL Syntax** - Delta Lake, Unity Catalog, functions
- ✅ **Feature Availability** - Versions, tiers, prerequisites
- ✅ **Security Practices** - Authentication, secrets management
- ✅ **Deprecated Features** - Outdated APIs, methods, patterns

### Official Sources

All validation is performed against these authoritative sources:

- **Primary**: https://docs.databricks.com
- **API Reference**: https://docs.databricks.com/api/workspace/introduction
- **Python SDK**: https://databricks-sdk-py.readthedocs.io/
- **SQL Manual**: https://docs.databricks.com/sql/language-manual/
- **Release Notes**: https://docs.databricks.com/release-notes/

### Validation Methods

**1. Automated AI Validation** (Recommended)
- Uses AI agents (Claude, GPT-4) to systematically compare documentation
- Fully automated with detailed reports
- Requires API key

**2. Semi-Automated Validation**
- Generates validation requests for manual AI review
- Copy/paste to your AI assistant
- No API key required

**3. Manual Validation**
- Use the validation prompt as a checklist
- Manually verify each item
- Time-intensive but thorough

---

## Quick Start

### Prerequisites

```bash
# Install Python 3.8+
python --version

# Navigate to validation directory
cd tests/validation

# Install dependencies
pip install -r requirements.txt
```

### Set Up API Key (for automated validation)

**Option 1: Anthropic Claude** (Recommended)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Option 2: OpenAI GPT-4**
```bash
export OPENAI_API_KEY="sk-..."
```

### Run Your First Validation

**On Linux/Mac:**
```bash
bash validate-now.sh
```

**On Windows:**
```cmd
validate-now.bat
```

**Or directly with Python:**
```bash
# Automated validation
python agent_validator.py --provider anthropic --scope full --interactive

# Manual validation request
python run_validation.py --scope full
```

---

## Validation System

### Architecture

```
tests/validation/
├── VALIDATION_AGENT_PROMPT.md      # AI agent instructions
├── validation-config.json           # Configuration settings
├── agent_validator.py               # Automated validation runner
├── run_validation.py                # Manual validation request generator
├── validate-now.sh                  # Quick run script (Linux/Mac)
├── validate-now.bat                 # Quick run script (Windows)
├── requirements.txt                 # Python dependencies
└── results/                         # Validation reports
    ├── validation-report-*.md       # Human-readable reports
    ├── validation-report-*.json     # Machine-readable data
    └── validation-raw-*.md          # Detailed findings
```

### Configuration

Edit `validation-config.json` to customize:

```json
{
  "validation_rules": {
    "api_documentation": {
      "enabled": true,
      "severity_mapping": {
        "endpoint_mismatch": "critical",
        "required_parameter_missing": "critical"
      }
    }
  },
  "quality_gates": {
    "minimum_accuracy_score": 85,
    "maximum_critical_issues": 0,
    "maximum_high_issues": 5
  }
}
```

### Validation Scopes

| Scope | Files Validated | Use Case |
|-------|-----------------|----------|
| `full` | All documentation | Weekly comprehensive check |
| `api` | `docs/api/*.md` | After API updates |
| `sdk` | `docs/sdk/*.md` | After SDK version changes |
| `sql` | `docs/sql/*.md` | SQL syntax verification |
| `examples` | `examples/**/*.py` | Code example validation |

---

## Running Tests

### Method 1: Interactive Script (Easiest)

**Linux/Mac:**
```bash
cd tests/validation
bash validate-now.sh
```

**Windows:**
```cmd
cd tests\validation
validate-now.bat
```

Follow the prompts to select:
1. Validation mode (automated/manual)
2. AI provider (if automated)
3. Validation scope

### Method 2: Direct Python Commands

**Full Automated Validation:**
```bash
python agent_validator.py \
  --provider anthropic \
  --scope full \
  --batch-size 3 \
  --interactive
```

**Validate Specific Scope:**
```bash
# API documentation only
python agent_validator.py --provider anthropic --scope api

# SDK documentation only
python agent_validator.py --provider anthropic --scope sdk

# SQL examples only
python agent_validator.py --provider anthropic --scope sql
```

**Validate Specific Files:**
```bash
python agent_validator.py \
  --provider anthropic \
  --files "docs/api/clusters-api.md" "docs/api/jobs-api.md"
```

**Generate Manual Validation Request:**
```bash
python run_validation.py --scope full
# Copy output from results/validation-request-*.txt to your AI assistant
```

### Method 3: GitHub Actions (CI/CD)

Validation runs automatically on:
- **Schedule**: Every Monday at 9 AM UTC
- **Push**: When docs are updated on main branch
- **Pull Request**: When docs are changed in PR

**Manual Trigger:**
1. Go to GitHub Actions tab
2. Select "Documentation Validation" workflow
3. Click "Run workflow"
4. Choose scope and provider
5. Click "Run workflow" button

---

## Understanding Results

### Report Files

After validation, find reports in `tests/validation/results/`:

```
validation-report-20240115-093045.md      # Executive summary
validation-report-20240115-093045.json    # Machine-readable
validation-raw-20240115-093045-batch1.md  # Detailed batch 1
validation-raw-20240115-093045-batch2.md  # Detailed batch 2
```

### Accuracy Scores

| Score | Status | Meaning |
|-------|--------|---------|
| 95-100% | 🟢 EXCELLENT | Production ready |
| 90-95% | 🟡 GOOD | Minor issues only |
| 85-90% | 🟠 NEEDS IMPROVEMENT | Several issues to fix |
| <85% | 🔴 REQUIRES ATTENTION | Significant problems |

### Issue Severity

**🔴 CRITICAL** - Fix immediately
- API breaking changes
- Incorrect required parameters
- Security vulnerabilities
- Syntax errors in code examples

**🟠 HIGH** - Fix within 7 days
- Deprecated feature usage
- Missing important information
- Version compatibility issues
- Incorrect method signatures

**🟡 MEDIUM** - Fix within 30 days
- Incomplete documentation
- Minor parameter mismatches
- Missing optional fields
- Outdated examples

**🔵 LOW** - Fix as time permits
- Formatting inconsistencies
- Typos
- Style improvements
- Comment updates

### Reading a Report

Example report structure:

```markdown
# Databricks Documentation Validation Report

**Status**: 🟡 GOOD
**Accuracy Score**: 92.5%

## Executive Summary
- Critical Issues: 0
- High Priority Issues: 4
- Medium Priority Issues: 9
- Low Priority Issues: 15

## Detailed Findings

### File: docs/api/jobs-api.md
**Status**: ⚠️ NEEDS UPDATES
**Accuracy Score**: 88%

#### Issue 1: Deprecated API Version Reference
- **Severity**: 🟠 High
- **Location**: Lines 23-25
- **Description**: References Jobs API 2.0, should use 2.1
- **Recommended Action**: Update to API 2.1
- **Official Source**: https://docs.databricks.com/api/...
```

### Quality Gates

Validation checks these gates:

| Gate | Default | Description |
|------|---------|-------------|
| Minimum Accuracy | 85% | Overall accuracy must exceed this |
| Max Critical | 0 | No critical issues allowed |
| Max High | 5 | Limited high-priority issues |

**Status Indicators:**
- ✅ PASS - Meets requirements
- ❌ FAIL - Does not meet requirements

---

## Scheduled Validation

### Recommended Schedule

| Frequency | Use Case |
|-----------|----------|
| **Weekly** | Standard maintenance |
| **Pre-release** | Before documentation releases |
| **Post-update** | After Databricks platform updates |
| **On-demand** | When issues are suspected |

### Setup Scheduled Validation

**Option 1: GitHub Actions** (Recommended)

Already configured in `.github/workflows/validate-documentation.yml`:
- Runs every Monday at 9 AM UTC
- Can be manually triggered
- Automatic on PR and push to main

**Option 2: Cron Job (Linux/Mac)**

```bash
# Edit crontab
crontab -e

# Add this line (runs every Monday at 9 AM)
0 9 * * 1 cd /path/to/c7-databricks/tests/validation && bash validate-now.sh < <(echo "1\n1\n1")
```

**Option 3: Windows Task Scheduler**

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Databricks Doc Validation"
4. Trigger: Weekly, Monday, 9:00 AM
5. Action: Start a program
   - Program: `cmd.exe`
   - Arguments: `/c cd C:\path\to\c7-databricks\tests\validation && validate-now.bat`
6. Finish and enable

**Option 4: Python Schedule Library**

Create `scheduled_validation.py`:

```python
import schedule
import time
from agent_validator import AIAgentValidator

def run_validation():
    validator = AIAgentValidator(provider="anthropic")
    validator.validate(scope="full")

schedule.every().monday.at("09:00").do(run_validation)

while True:
    schedule.run_pending()
    time.sleep(60)
```

Run continuously:
```bash
python scheduled_validation.py
```

---

## Quality Gates

### Configuring Gates

Edit `validation-config.json`:

```json
{
  "quality_gates": {
    "minimum_accuracy_score": 85,
    "maximum_critical_issues": 0,
    "maximum_high_issues": 5,
    "fail_on_security_issues": true,
    "fail_on_breaking_changes": true
  }
}
```

### Using Gates in CI/CD

**Fail Build on Gate Failure:**

```bash
python agent_validator.py --provider anthropic --scope full
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "Quality gates failed"
  exit 1
fi
```

**Block PR Merge:**

In `.github/workflows/validate-documentation.yml`:

```yaml
- name: Check quality gates
  if: github.event_name == 'pull_request'
  run: |
    if [ "$CRITICAL" -gt 0 ]; then
      echo "Critical issues found"
      exit 1
    fi
```

### Customizing Gates by Scope

Different gates for different scopes:

```json
{
  "quality_gates_by_scope": {
    "api": {
      "minimum_accuracy_score": 95,
      "maximum_critical_issues": 0
    },
    "examples": {
      "minimum_accuracy_score": 90,
      "maximum_high_issues": 3
    }
  }
}
```

---

## Troubleshooting

### Common Issues

**1. API Key Not Found**

```
Error: API key not found. Set ANTHROPIC_API_KEY environment variable.
```

**Solution:**
```bash
export ANTHROPIC_API_KEY="your-api-key"
# Or add to ~/.bashrc or ~/.zshrc
```

**2. Import Error**

```
ModuleNotFoundError: No module named 'anthropic'
```

**Solution:**
```bash
pip install -r requirements.txt
# Or specifically:
pip install anthropic
```

**3. Rate Limiting**

```
Error 429: Rate limit exceeded
```

**Solution:**
- Reduce batch size: `--batch-size 2`
- Add delays in `agent_validator.py`
- Validate smaller scopes separately

**4. Token Limit Exceeded**

```
Error: Token limit exceeded
```

**Solution:**
- Use smaller batch sizes: `--batch-size 1`
- Validate specific files instead of full scope
- Break validation into multiple runs

**5. Permission Denied (Scripts)**

```
Permission denied: ./validate-now.sh
```

**Solution:**
```bash
chmod +x validate-now.sh
```

### Debugging

**Enable Verbose Logging:**

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Test API Connection:**

```bash
python -c "import anthropic; client = anthropic.Anthropic(); print('OK')"
```

**Validate Configuration:**

```bash
python -c "import json; json.load(open('validation-config.json')); print('Valid')"
```

---

## Best Practices

### 1. Regular Validation

**Weekly Schedule:**
- Monday: Full validation
- Track trends over time
- Address issues incrementally

**Event-Based:**
- Before releases
- After Databricks updates
- When official docs change

### 2. Prioritize Fixes

**Fix Order:**
1. 🔴 Critical - Immediately (user-breaking)
2. 🟠 High - Within 7 days (usability)
3. 🟡 Medium - Within 30 days (completeness)
4. 🔵 Low - As time permits (polish)

### 3. Track Metrics

**Monitor Over Time:**
```bash
# View accuracy trends
for file in results/validation-report-*.json; do
  echo -n "$(basename $file): "
  python -c "import json; print(json.load(open('$file'))['total_accuracy'])"
done
```

### 4. Document Changes

When fixing issues:
```markdown
Fix: Update Jobs API from 2.0 to 2.1

- Updated all endpoint references
- Added new parameters (timeout_seconds, etc.)
- Included migration notes

Resolves: VAL-20240115-093045-Issue-4
Source: https://docs.databricks.com/api/workspace/jobs
```

### 5. Incremental Validation

For large repos:
```bash
# Day 1: APIs
python agent_validator.py --provider anthropic --scope api

# Day 2: SDK
python agent_validator.py --provider anthropic --scope sdk

# Day 3: Examples
python agent_validator.py --provider anthropic --scope examples
```

### 6. Cost Management

**Estimate Costs:**
- Claude: ~$0.15-$0.30 per full validation
- GPT-4: ~$0.50-$0.75 per full validation

**Optimize:**
- Validate changed files only
- Use appropriate batch sizes
- Schedule during off-peak hours

### 7. Integration with Workflow

**Pre-commit Hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit
if git diff --cached --name-only | grep -q "^docs/"; then
  echo "Documentation changed, running validation..."
  cd tests/validation
  python run_validation.py --scope custom --files $(git diff --cached --name-only | grep "^docs/")
fi
```

**Documentation Review Checklist:**
- [ ] Validation report reviewed
- [ ] Critical issues resolved
- [ ] High priority issues addressed or documented
- [ ] Official sources verified
- [ ] Code examples tested
- [ ] Links verified

---

## API Cost Estimation

### Anthropic Claude

- **Model**: Claude Sonnet 4.5
- **Pricing**: ~$3/M input tokens, ~$15/M output tokens
- **Typical Full Validation**: 50K input + 5K output tokens
- **Cost**: $0.15 - $0.30 per run

### OpenAI GPT-4

- **Model**: GPT-4 Turbo
- **Pricing**: ~$10/M input tokens, ~$30/M output tokens
- **Typical Full Validation**: 50K input + 5K output tokens
- **Cost**: $0.50 - $0.75 per run

### Monthly Budget

Assuming weekly full validations:
- **Claude**: ~$1.20/month
- **GPT-4**: ~$3.00/month

---

## Contributing

### Improving Validation

**Add Custom Validation Rules:**

Edit `validation-config.json`:
```json
{
  "custom_validations": [
    {
      "name": "Check DBR Versions",
      "enabled": true,
      "pattern": "DBR \\d+\\.\\d+",
      "verify_against": "https://docs.databricks.com/release-notes/runtime/",
      "severity": "medium"
    }
  ]
}
```

**Enhance Agent Prompt:**

Edit `VALIDATION_AGENT_PROMPT.md` to:
- Add new validation criteria
- Customize output format
- Add domain-specific checks

**Extend Validator:**

```python
class CustomValidator(AIAgentValidator):
    def validate_custom(self, files):
        # Add custom validation logic
        pass
```

---

## Resources

### Documentation
- [Validation Agent Prompt](validation/VALIDATION_AGENT_PROMPT.md)
- [Configuration Reference](validation/validation-config.json)
- [Sample Report](validation/results/SAMPLE-REPORT.md)

### Official Sources
- [Databricks Documentation](https://docs.databricks.com)
- [Python SDK Docs](https://databricks-sdk-py.readthedocs.io/)
- [Release Notes](https://docs.databricks.com/release-notes/)

### AI Providers
- [Anthropic Claude](https://www.anthropic.com)
- [OpenAI GPT-4](https://openai.com)

---

## Summary

The Databricks Documentation Validation System ensures your documentation remains accurate by:

1. **Automated Comparison** - AI agents compare against official sources
2. **Comprehensive Checks** - APIs, code, config, security, versions
3. **Actionable Reports** - Detailed findings with line numbers and fixes
4. **Quality Gates** - Enforce accuracy standards
5. **Scheduled Runs** - Continuous validation via GitHub Actions/cron
6. **Cost Effective** - ~$1-3/month for weekly validation

**Get Started:**
```bash
cd tests/validation
bash validate-now.sh
```

**Questions?** Check the README or review sample reports in `results/`.

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Maintained By**: Documentation Team
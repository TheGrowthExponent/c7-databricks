# Databricks Documentation Validation - Quick Reference

One-page reference for common validation commands and workflows.

---

## 🚀 Quick Start

### First Time Setup

```bash
cd tests/validation
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
```

### Run Validation Now

**Easiest Method:**
```bash
bash validate-now.sh      # Linux/Mac
validate-now.bat          # Windows
```

**Direct Command:**
```bash
python agent_validator.py --provider anthropic --scope full --interactive
```

---

## 📋 Common Commands

### Automated Validation

```bash
# Full repository
python agent_validator.py --provider anthropic --scope full

# API docs only
python agent_validator.py --provider anthropic --scope api

# SDK docs only
python agent_validator.py --provider anthropic --scope sdk

# Specific files
python agent_validator.py --provider anthropic --files "docs/api/*.md"

# With OpenAI instead
python agent_validator.py --provider openai --scope full
```

### Manual Validation

```bash
# Generate validation request
python run_validation.py --scope full

# Find request file
ls -lt results/validation-request-*.txt | head -1

# Copy to AI assistant, then save response
```

### View Results

```bash
# Latest report
ls -t results/validation-report-*.md | head -1 | xargs cat | less

# All reports
ls results/validation-report-*.md

# JSON data
cat results/validation-report-*.json | python -m json.tool
```

---

## 🎯 Validation Scopes

| Scope | Command | Files Validated |
|-------|---------|-----------------|
| **Full** | `--scope full` | All documentation |
| **API** | `--scope api` | `docs/api/*.md` |
| **SDK** | `--scope sdk` | `docs/sdk/*.md` |
| **SQL** | `--scope sql` | `docs/sql/*.md` |
| **Examples** | `--scope examples` | `examples/**/*` |

---

## 🔑 Environment Variables

```bash
# Anthropic Claude (recommended)
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI GPT-4
export OPENAI_API_KEY="sk-..."

# Permanent setup (Linux/Mac)
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc

# Permanent setup (Windows)
setx ANTHROPIC_API_KEY "your-key"
```

---

## 📊 Understanding Results

### Accuracy Scores

| Score | Status | Action |
|-------|--------|--------|
| 95-100% | 🟢 EXCELLENT | Maintain quality |
| 90-95% | 🟡 GOOD | Minor fixes |
| 85-90% | 🟠 NEEDS WORK | Address issues |
| <85% | 🔴 CRITICAL | Immediate action |

### Issue Severity

- 🔴 **CRITICAL** - Fix immediately (breaks user code)
- 🟠 **HIGH** - Fix within 7 days (usability impact)
- 🟡 **MEDIUM** - Fix within 30 days (improvements)
- 🔵 **LOW** - Fix as time permits (polish)

### Quality Gates

- ✅ **Minimum Accuracy**: 85%
- ✅ **Max Critical Issues**: 0
- ✅ **Max High Issues**: 5

---

## 🔧 Troubleshooting

### API Key Issues

```bash
# Check if set
echo $ANTHROPIC_API_KEY

# Test connection
python -c "import anthropic; anthropic.Anthropic(); print('OK')"
```

### Module Not Found

```bash
pip install -r requirements.txt
# Or specifically:
pip install anthropic openai
```

### Rate Limiting

```bash
# Reduce batch size
python agent_validator.py --provider anthropic --scope full --batch-size 2

# Validate incrementally
python agent_validator.py --provider anthropic --scope api
python agent_validator.py --provider anthropic --scope sdk
```

### Permission Denied

```bash
chmod +x validate-now.sh
```

---

## 📅 Scheduled Validation

### GitHub Actions (Automatic)

Already configured! Runs:
- Every Monday at 9 AM UTC
- On push to main branch (docs changes)
- On pull requests (docs changes)
- Manual trigger via Actions tab

### Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add line (Monday 9 AM)
0 9 * * 1 cd /path/to/c7-databricks/tests/validation && bash validate-now.sh
```

### Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Weekly, Monday, 9 AM
4. Action: Start program
5. Program: `cmd.exe`
6. Arguments: `/c cd C:\path\to\tests\validation && validate-now.bat`

---

## 🎯 Common Workflows

### Pre-Release Validation

```bash
cd tests/validation
python agent_validator.py --provider anthropic --scope full --interactive
# Review report
# Fix critical/high issues
# Re-run validation
```

### Post-Update Check

```bash
# After Databricks platform update
python agent_validator.py --provider anthropic --scope api
# Check for API changes
```

### PR Validation

```bash
# Validate only changed files
git diff --name-only origin/main | grep "^docs/" > /tmp/changed_docs.txt
python agent_validator.py --provider anthropic --files $(cat /tmp/changed_docs.txt)
```

### Weekly Maintenance

```bash
# Monday morning routine
cd tests/validation
bash validate-now.sh
# Review results
# Create issues for findings
# Track progress
```

---

## 💰 Cost Estimates

**Anthropic Claude:**
- Per validation: $0.15 - $0.30
- Weekly (4x/month): ~$1.20/month

**OpenAI GPT-4:**
- Per validation: $0.50 - $0.75
- Weekly (4x/month): ~$3.00/month

---

## 📖 Files & Directories

```
tests/validation/
├── VALIDATION_AGENT_PROMPT.md   # AI instructions
├── validation-config.json        # Configuration
├── agent_validator.py            # Automated runner
├── run_validation.py             # Manual generator
├── validate-now.sh              # Quick script
├── requirements.txt             # Dependencies
└── results/                     # Reports
    ├── validation-report-*.md   # Summary
    ├── validation-report-*.json # Data
    └── validation-raw-*.md      # Details
```

---

## 🆘 Getting Help

### Check Logs

```bash
# View last validation
tail -100 results/validation-report-*.md | less

# Check errors
python agent_validator.py --provider anthropic --scope api 2>&1 | tee validation.log
```

### Verify Setup

```bash
# Python version
python --version  # Should be 3.8+

# Dependencies installed
pip list | grep -E "anthropic|openai"

# Configuration valid
python -c "import json; json.load(open('validation-config.json'))"

# API key set
env | grep -E "ANTHROPIC|OPENAI"
```

### Review Documentation

- [Full Testing Guide](../TESTING-GUIDE.md)
- [Validation README](README.md)
- [Sample Report](results/SAMPLE-REPORT.md)
- [Agent Prompt](VALIDATION_AGENT_PROMPT.md)

---

## ⚡ Power User Tips

### Chain Multiple Validations

```bash
for scope in api sdk sql examples; do
  echo "Validating $scope..."
  python agent_validator.py --provider anthropic --scope $scope
  sleep 5
done
```

### Extract Key Metrics

```bash
# Get accuracy from latest report
python -c "import json; print(json.load(open('results/validation-report-*.json'))['total_accuracy'])"

# Count issues
grep -c "Severity: Critical" results/validation-report-*.md
```

### Custom Batch Sizes

```bash
# Large files - use small batches
python agent_validator.py --provider anthropic --scope full --batch-size 1

# Small files - use large batches
python agent_validator.py --provider anthropic --scope full --batch-size 5
```

### Validate Single File

```bash
python agent_validator.py --provider anthropic --files "docs/api/clusters-api.md"
```

---

## 📋 Checklist: Before Release

- [ ] Run full validation: `python agent_validator.py --provider anthropic --scope full`
- [ ] Accuracy score ≥ 85%
- [ ] Zero critical issues
- [ ] High issues ≤ 5
- [ ] Review detailed findings
- [ ] Fix or document exceptions
- [ ] Re-run validation after fixes
- [ ] Update CHANGELOG with validation results

---

## 🔗 Quick Links

- **Official Databricks Docs**: https://docs.databricks.com
- **API Reference**: https://docs.databricks.com/api/workspace/introduction
- **Python SDK**: https://databricks-sdk-py.readthedocs.io/
- **SQL Reference**: https://docs.databricks.com/sql/language-manual/

---

## 📱 One-Liners

```bash
# Full validation now
cd tests/validation && python agent_validator.py --provider anthropic --scope full

# View latest report
cat $(ls -t tests/validation/results/validation-report-*.md | head -1)

# Check if validation passed
python agent_validator.py --provider anthropic --scope full && echo "✅ PASSED" || echo "❌ FAILED"

# Get accuracy score
python -c "import json,glob; print(json.load(open(sorted(glob.glob('tests/validation/results/*.json'))[-1]))['total_accuracy'])"

# Install and validate
pip install anthropic && python tests/validation/agent_validator.py --provider anthropic --scope full
```

---

**Remember**: The goal is 100% accuracy against official Databricks documentation!

**Version**: 1.0.0
**Updated**: 2024-01-15
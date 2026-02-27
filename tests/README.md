# Databricks Documentation Testing & Validation

Comprehensive testing and validation system for ensuring 100% accuracy of Databricks documentation against official sources.

---

## 🎯 Overview

This testing system provides **automated AI-powered validation** that compares your documentation against official Databricks sources to ensure accuracy, completeness, and currency.

### What It Does

✅ **Validates API Documentation** - Endpoints, parameters, schemas
✅ **Checks Code Examples** - Syntax, imports, best practices
✅ **Verifies Configuration** - Keys, defaults, data types
✅ **Tests SQL Syntax** - Delta Lake, Unity Catalog, functions
✅ **Identifies Deprecated Features** - Outdated APIs and patterns
✅ **Enforces Security Best Practices** - Secrets, authentication, access control
✅ **Generates Detailed Reports** - Actionable findings with line numbers and fixes

### Key Benefits

- 🤖 **Automated**: AI agents do the heavy lifting
- 📊 **Comprehensive**: Checks all aspects of documentation
- 🎯 **Accurate**: Compares against official Databricks sources
- 📈 **Actionable**: Provides specific fixes with line numbers
- ⏱️ **Fast**: Full validation in ~15 minutes
- 💰 **Cost-Effective**: ~$1-3/month for weekly validation

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd tests/validation
pip install -r requirements.txt
```

### 2. Set Up API Key

**For Anthropic Claude (Recommended):**

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**For OpenAI GPT-4:**

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### 3. Run Validation

**Easiest Method:**

```bash
# Linux/Mac
bash validate-now.sh

# Windows
validate-now.bat
```

**Or Direct Command:**

```bash
python agent_validator.py --provider anthropic --scope full --interactive
```

### 4. Review Results

Reports are saved in `validation/results/`:

```bash
# View latest report
cat $(ls -t validation/results/validation-report-*.md | head -1)
```

---

## 📁 Directory Structure

```
tests/
├── README.md                           # This file
├── TESTING-GUIDE.md                    # Comprehensive testing guide
├── validation/                         # Validation system
│   ├── README.md                       # Validation system docs
│   ├── QUICK-REFERENCE.md             # Command quick reference
│   ├── EXAMPLE-USAGE.md               # Usage examples
│   ├── VALIDATION_AGENT_PROMPT.md     # AI agent instructions
│   ├── validation-config.json         # Configuration
│   ├── agent_validator.py             # Automated validator
│   ├── run_validation.py              # Manual request generator
│   ├── validate-now.sh                # Quick run script (Linux/Mac)
│   ├── validate-now.bat               # Quick run script (Windows)
│   ├── requirements.txt               # Dependencies
│   └── results/                       # Validation reports
│       ├── SAMPLE-REPORT.md           # Example report
│       └── validation-report-*.md     # Generated reports
└── .github/workflows/                 # CI/CD automation
    └── validate-documentation.yml     # GitHub Actions workflow
```

---

## 📚 Documentation

### Getting Started

- **[Quick Start](#-quick-start)** - Get up and running in 5 minutes
- **[validation/README.md](validation/README.md)** - Detailed validation guide
- **[validation/QUICK-REFERENCE.md](validation/QUICK-REFERENCE.md)** - Command cheat sheet

### Comprehensive Guides

- **[TESTING-GUIDE.md](TESTING-GUIDE.md)** - Complete testing and validation guide
- **[validation/EXAMPLE-USAGE.md](validation/EXAMPLE-USAGE.md)** - Real-world examples
- **[validation/SAMPLE-REPORT.md](validation/results/SAMPLE-REPORT.md)** - Example validation report

### Technical Reference

- **[validation/VALIDATION_AGENT_PROMPT.md](validation/VALIDATION_AGENT_PROMPT.md)** - AI agent instructions
- **[validation/validation-config.json](validation/validation-config.json)** - Configuration reference

---

## 🎮 Usage Examples

### Full Repository Validation

```bash
python validation/agent_validator.py --provider anthropic --scope full
```

### Validate Specific Areas

```bash
# API documentation only
python validation/agent_validator.py --provider anthropic --scope api

# SDK documentation only
python validation/agent_validator.py --provider anthropic --scope sdk

# SQL examples only
python validation/agent_validator.py --provider anthropic --scope sql
```

### Validate Specific Files

```bash
python validation/agent_validator.py \
  --provider anthropic \
  --files "docs/api/clusters-api.md" "docs/api/jobs-api.md"
```

### Manual Validation (No API Key Required)

```bash
# Generate validation request
python validation/run_validation.py --scope full

# Copy output to your AI assistant (Claude, ChatGPT, etc.)
# Review the AI's validation report
```

---

## 📊 Understanding Results

### Accuracy Scores

| Score   | Status                | Meaning                            |
| ------- | --------------------- | ---------------------------------- |
| 95-100% | 🟢 EXCELLENT          | Production ready, maintain quality |
| 90-95%  | 🟡 GOOD               | Minor issues, mostly cosmetic      |
| 85-90%  | 🟠 NEEDS IMPROVEMENT  | Several issues to address          |
| <85%    | 🔴 REQUIRES ATTENTION | Significant accuracy problems      |

### Issue Severity

- **🔴 CRITICAL** - Fix immediately (user-breaking errors)
- **🟠 HIGH** - Fix within 7 days (usability impact)
- **🟡 MEDIUM** - Fix within 30 days (improvements needed)
- **🔵 LOW** - Fix as time permits (polish and style)

### Quality Gates

Default thresholds for passing validation:

- ✅ Minimum Accuracy: **85%**
- ✅ Maximum Critical Issues: **0**
- ✅ Maximum High Issues: **5**

---

## 📅 Scheduled Validation

### GitHub Actions (Automatic)

Already configured in `.github/workflows/validate-documentation.yml`:

- ✅ Runs every Monday at 9 AM UTC
- ✅ Runs on push to main (when docs change)
- ✅ Runs on pull requests (when docs change)
- ✅ Can be manually triggered from Actions tab

### Local Scheduling

**Linux/Mac (Cron):**

```bash
crontab -e
# Add: 0 9 * * 1 cd /path/to/c7-databricks/tests/validation && bash validate-now.sh
```

**Windows (Task Scheduler):**

1. Open Task Scheduler
2. Create Basic Task: "Databricks Doc Validation"
3. Trigger: Weekly, Monday, 9:00 AM
4. Action: Start `validate-now.bat` from `tests/validation`

---

## 🔧 Configuration

### Edit Validation Rules

Edit `validation/validation-config.json`:

```json
{
  "quality_gates": {
    "minimum_accuracy_score": 85,
    "maximum_critical_issues": 0,
    "maximum_high_issues": 5
  },
  "validation_rules": {
    "api_documentation": { "enabled": true },
    "sdk_documentation": { "enabled": true },
    "code_examples": { "enabled": true }
  }
}
```

### Customize Validation Scope

```json
{
  "scope": {
    "include_paths": ["docs/**/*.md", "examples/**/*.py"],
    "exclude_paths": ["**/draft-*.md", "**/.backup/**"]
  }
}
```

---

## 🆘 Troubleshooting

### API Key Not Found

```bash
export ANTHROPIC_API_KEY="your-key-here"
echo $ANTHROPIC_API_KEY  # Verify it's set
```

### Module Not Found

```bash
pip install -r validation/requirements.txt
```

### Rate Limiting

```bash
# Reduce batch size
python validation/agent_validator.py --provider anthropic --scope full --batch-size 2
```

### Permission Denied

```bash
chmod +x validation/validate-now.sh
```

For more troubleshooting, see [TESTING-GUIDE.md](TESTING-GUIDE.md#troubleshooting).

---

## 💰 Cost Estimation

### Anthropic Claude (Recommended)

- **Per Validation**: $0.15 - $0.30
- **Weekly (4x/month)**: ~$1.20/month
- **Monthly (20x/month)**: ~$6.00/month

### OpenAI GPT-4

- **Per Validation**: $0.50 - $0.75
- **Weekly (4x/month)**: ~$3.00/month
- **Monthly (20x/month)**: ~$15.00/month

---

## 🔄 Validation Workflow

### Weekly Maintenance

```bash
# Monday: Run validation
cd tests/validation
bash validate-now.sh

# Review results
cat results/validation-report-*.md | less

# Create issues for findings
# Track and fix over the week

# Friday: Re-validate
python agent_validator.py --provider anthropic --scope full
```

### Pre-Release Checklist

- [ ] Run full validation
- [ ] Accuracy score ≥ 85%
- [ ] Zero critical issues
- [ ] High issues ≤ 5 (or documented)
- [ ] Review all findings
- [ ] Fix or document exceptions
- [ ] Re-run validation
- [ ] Update CHANGELOG

### Post-Update Validation

```bash
# After Databricks platform update
python validation/agent_validator.py --provider anthropic --scope api

# After SDK version change
python validation/agent_validator.py --provider anthropic --scope sdk
```

---

## 🎯 Best Practices

1. **Validate Regularly** - Weekly automated runs catch issues early
2. **Fix by Priority** - Critical → High → Medium → Low
3. **Track Metrics** - Monitor accuracy scores over time
4. **Document Changes** - Reference validation reports in commits
5. **Automate** - Use GitHub Actions for continuous validation
6. **Review Reports** - Don't just run—actually review findings
7. **Update Promptly** - Fix issues within severity time windows

---

## 🤝 Contributing

### Improve Validation System

- Add custom validation rules in `validation-config.json`
- Enhance AI prompt in `VALIDATION_AGENT_PROMPT.md`
- Extend validator in `agent_validator.py`

### Report Issues

- Validation incorrectly flagging correct docs? Let us know
- Official Databricks docs outdated? Verify and update config
- Found better validation approaches? Share your improvements

---

## 📖 Additional Resources

### Official Databricks Documentation

- **Main Docs**: https://docs.databricks.com
- **API Reference**: https://docs.databricks.com/api/workspace/introduction
- **Python SDK**: https://databricks-sdk-py.readthedocs.io/
- **SQL Reference**: https://docs.databricks.com/sql/language-manual/
- **Release Notes**: https://docs.databricks.com/release-notes/

### AI Providers

- **Anthropic Claude**: https://www.anthropic.com
- **OpenAI GPT-4**: https://openai.com

---

## 📞 Support

### Getting Help

1. Check [TESTING-GUIDE.md](TESTING-GUIDE.md) for comprehensive documentation
2. Review [validation/README.md](validation/README.md) for validation details
3. See [validation/QUICK-REFERENCE.md](validation/QUICK-REFERENCE.md) for commands
4. Look at [validation/EXAMPLE-USAGE.md](validation/EXAMPLE-USAGE.md) for examples

### Common Issues

- **Setup**: See [Quick Start](#-quick-start)
- **Configuration**: See [Configuration](#-configuration)
- **Troubleshooting**: See [Troubleshooting](#-troubleshooting)
- **Usage Examples**: See [Usage Examples](#-usage-examples)

---

## 📈 Success Metrics

Track your documentation quality:

```bash
# View accuracy trend
for f in validation/results/validation-report-*.json; do
  echo "$(basename $f): $(python -c "import json; print(json.load(open('$f'))['total_accuracy'])")%"
done

# Count total issues over time
grep -h "Total Issues:" validation/results/validation-report-*.md
```

### Target Metrics

- **Accuracy**: Maintain ≥ 90%
- **Critical Issues**: Always 0
- **High Issues**: ≤ 3
- **Validation Frequency**: Weekly minimum
- **Fix Time**: Critical <24h, High <7d

---

## 🎉 Quick Wins

Get immediate value:

1. **Run First Validation** (5 minutes)

   ```bash
   cd tests/validation && bash validate-now.sh
   ```

2. **Review Critical Issues** (10 minutes)

   ```bash
   grep -A 10 "Critical" validation/results/validation-report-*.md
   ```

3. **Fix Top 3 Issues** (30 minutes)
   - Update incorrect API endpoints
   - Fix deprecated code examples
   - Correct configuration values

4. **Re-validate** (5 minutes)

   ```bash
   python validation/agent_validator.py --provider anthropic --scope full
   ```

5. **See Improvement** (1 minute)
   - Compare before/after accuracy scores
   - Celebrate the increase! 🎉

---

## ✨ Summary

The Databricks Documentation Testing & Validation system ensures your documentation is:

- ✅ **Accurate** - Matches official Databricks sources
- ✅ **Current** - Uses latest APIs, SDKs, and patterns
- ✅ **Secure** - Follows security best practices
- ✅ **Complete** - No missing parameters or features
- ✅ **Reliable** - Validated regularly and automatically

**Start now:**

```bash
cd tests/validation && bash validate-now.sh
```

---

**Version**: 1.0.0
**Last Updated**: 2026-02-27
**Maintained By**: Documentation Team
**License**: MIT

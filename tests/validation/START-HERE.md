# 🚀 Databricks Documentation Validation - START HERE

**Welcome!** This is your AI-powered documentation validation system.

---

## ⚡ Quick Start (5 Minutes)

### 1️⃣ Install Dependencies
```bash
cd tests/validation
pip install -r requirements.txt
```

### 2️⃣ Set Your API Key

**Choose ONE:**

```bash
# Option A: Anthropic Claude (Recommended - cheaper, faster)
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Option B: OpenAI GPT-4 (Alternative)
export OPENAI_API_KEY="sk-your-key-here"
```

**Get an API key:**
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/api-keys

### 3️⃣ Run Your First Validation

**Easiest way:**
```bash
bash validate-now.sh          # Linux/Mac
validate-now.bat              # Windows CMD
.\validate-now.ps1            # Windows PowerShell
```

**Or directly:**
```bash
python agent_validator.py --provider anthropic --scope full --interactive
```

### 4️⃣ View Results
```bash
cat results/validation-report-*.md
```

**Done!** 🎉

---

## 📊 What You Get

After validation completes (~15 minutes), you'll receive:

✅ **Accuracy Score** - Overall quality rating (0-100%)  
✅ **Issue Count** - Categorized by severity (Critical/High/Medium/Low)  
✅ **Detailed Findings** - Specific issues with line numbers  
✅ **Official Sources** - Links to Databricks documentation  
✅ **Recommended Fixes** - Exact changes needed  
✅ **Quality Gate Status** - Pass/fail against standards  

---

## 🎯 Validation Checks

The system validates:

- ✅ **API Endpoints** - URLs, parameters, schemas
- ✅ **Code Examples** - Syntax, imports, best practices
- ✅ **SDK References** - Method signatures, types
- ✅ **SQL Syntax** - Delta Lake, Unity Catalog
- ✅ **Configuration** - Keys, defaults, values
- ✅ **Security** - Secrets management, auth patterns
- ✅ **Versions** - Compatibility, deprecations

**Compared against:** Official Databricks documentation at docs.databricks.com

---

## 📁 File Overview

```
tests/validation/
├── START-HERE.md              ← You are here!
│
├── Quick Scripts (Run These)
│   ├── validate-now.sh        ← Linux/Mac
│   ├── validate-now.bat       ← Windows CMD
│   └── validate-now.ps1       ← Windows PowerShell
│
├── Core System
│   ├── agent_validator.py     ← Automated validator
│   ├── run_validation.py      ← Manual request generator
│   └── validation-config.json ← Configuration
│
├── Documentation
│   ├── QUICK-REFERENCE.md     ← Command cheat sheet
│   ├── EXAMPLE-USAGE.md       ← Real examples
│   ├── SETUP-CHECKLIST.md     ← Detailed setup
│   └── README.md              ← Full guide
│
└── Results
    └── results/               ← Reports saved here
        └── SAMPLE-REPORT.md   ← Example output
```

---

## 💡 Common Commands

```bash
# Full validation
python agent_validator.py --provider anthropic --scope full

# API docs only
python agent_validator.py --provider anthropic --scope api

# SDK docs only
python agent_validator.py --provider anthropic --scope sdk

# Specific files
python agent_validator.py --provider anthropic --files "docs/api/clusters-api.md"

# Generate manual request (no API key needed)
python run_validation.py --scope full

# View latest report
cat $(ls -t results/validation-report-*.md | head -1)
```

---

## 🔄 Scheduled Validation

### GitHub Actions (Recommended)
Already configured! Runs automatically:
- ✅ Every Monday at 9 AM UTC
- ✅ On push to main (when docs change)
- ✅ On pull requests
- ✅ Manual trigger available

**Setup:**
1. Go to GitHub → Settings → Secrets
2. Add `ANTHROPIC_API_KEY` secret
3. Done! It will run automatically

### Local Scheduling

**Linux/Mac (Cron):**
```bash
crontab -e
# Add: 0 9 * * 1 cd /path/to/tests/validation && bash validate-now.sh
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task: "Doc Validation"
3. Trigger: Weekly, Monday, 9 AM
4. Action: Run `validate-now.bat`

---

## 📖 Need Help?

### Quick Help
- **Commands:** [QUICK-REFERENCE.md](QUICK-REFERENCE.md)
- **Examples:** [EXAMPLE-USAGE.md](EXAMPLE-USAGE.md)
- **Setup:** [SETUP-CHECKLIST.md](SETUP-CHECKLIST.md)

### Detailed Help
- **Full Guide:** [../TESTING-GUIDE.md](../TESTING-GUIDE.md)
- **Architecture:** [../ARCHITECTURE.md](../ARCHITECTURE.md)
- **System Docs:** [README.md](README.md)

### Troubleshooting

**API Key Not Found:**
```bash
export ANTHROPIC_API_KEY="your-key"
echo $ANTHROPIC_API_KEY  # Verify it's set
```

**Module Not Found:**
```bash
pip install -r requirements.txt
```

**Permission Denied:**
```bash
chmod +x validate-now.sh
```

---

## 💰 Cost

- **Per Validation:** $0.15 - $0.30 (Claude) or $0.50 - $0.75 (GPT-4)
- **Weekly (4 runs):** $1 - $3/month
- **GitHub Actions:** FREE (included)

---

## 🎯 Next Steps

1. ✅ Run your first validation (follow steps above)
2. 📊 Review the results
3. 🔧 Fix any critical issues found
4. ⏰ Set up scheduled validation
5. 🔄 Re-run weekly to maintain quality

---

## 🎉 You're Ready!

Run this command now:

```bash
bash validate-now.sh
```

And watch your documentation get validated! 🚀

---

**Questions?** Check [QUICK-REFERENCE.md](QUICK-REFERENCE.md) for all commands  
**Need details?** Read the [full guide](README.md)  
**See example?** Look at [SAMPLE-REPORT.md](results/SAMPLE-REPORT.md)

**Happy Validating!** ✨
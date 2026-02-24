# Validation System Setup Checklist

Quick setup guide to get the documentation validation system running.

---

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies ✓

```bash
cd tests/validation
pip install -r requirements.txt
```

**Verify:**
```bash
python -c "import anthropic; print('✓ Anthropic installed')"
# OR
python -c "import openai; print('✓ OpenAI installed')"
```

---

### Step 2: Set API Key ✓

**Choose one provider:**

**Option A: Anthropic Claude (Recommended)**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Option B: OpenAI GPT-4**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**Verify:**
```bash
echo $ANTHROPIC_API_KEY  # Should show your key
# OR
echo $OPENAI_API_KEY
```

**Make it permanent (optional):**
```bash
# Linux/Mac
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc

# Windows PowerShell
[Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your-key', 'User')
```

---

### Step 3: Test Configuration ✓

```bash
python -c "
import os
import sys
key = os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('OPENAI_API_KEY')
if key:
    print('✓ API key configured')
    sys.exit(0)
else:
    print('✗ API key not found')
    sys.exit(1)
"
```

---

### Step 4: Run First Validation ✓

```bash
# Interactive mode (easiest)
bash validate-now.sh          # Linux/Mac
validate-now.bat              # Windows CMD
.\validate-now.ps1            # Windows PowerShell

# OR direct command
python agent_validator.py --provider anthropic --scope full --interactive
```

---

### Step 5: Review Results ✓

```bash
# View latest report
ls -lt results/validation-report-*.md | head -1 | xargs cat | less

# Check accuracy score
python -c "
import json
import glob
reports = sorted(glob.glob('results/*.json'))
if reports:
    data = json.load(open(reports[-1]))
    print(f'Accuracy: {data.get(\"total_accuracy\", 0)}%')
    print(f'Critical: {data.get(\"total_critical\", 0)}')
    print(f'High: {data.get(\"total_high\", 0)}')
"
```

---

## 📋 Complete Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API key obtained (Anthropic or OpenAI)
- [ ] API key set in environment
- [ ] Configuration verified
- [ ] First validation run completed
- [ ] Results reviewed
- [ ] GitHub Actions configured (optional)
- [ ] Scheduled validation set up (optional)

---

## 🔧 GitHub Actions Setup (Optional)

### Enable Automated Validation

1. **Add Secret to GitHub:**
   - Go to repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`)
   - Value: Your API key
   - Click "Add secret"

2. **Verify Workflow:**
   - Go to Actions tab
   - Find "Documentation Validation" workflow
   - Should show as enabled

3. **Manual Test:**
   - Click "Run workflow" button
   - Select scope: `full`
   - Select provider: `anthropic`
   - Click "Run workflow"
   - Wait for completion (~15 minutes)
   - Download and review artifacts

4. **Check PR Integration:**
   - Create test PR with doc change
   - Verify validation runs automatically
   - Check that comment is posted
   - Confirm status check appears

**GitHub Actions Checklist:**
- [ ] Repository secret added
- [ ] Workflow appears in Actions tab
- [ ] Manual trigger works
- [ ] Scheduled run is enabled
- [ ] PR validation works
- [ ] Artifacts are generated
- [ ] Issues created on critical findings

---

## 🔄 Weekly Validation Setup

### Option 1: GitHub Actions (Recommended)

Already configured! Runs every Monday at 9 AM UTC.

- [ ] Verify workflow schedule in `.github/workflows/validate-documentation.yml`
- [ ] Enable workflow if disabled
- [ ] Set up notification preferences

### Option 2: Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add this line (Monday 9 AM)
0 9 * * 1 cd /path/to/c7-databricks/tests/validation && bash validate-now.sh
```

**Checklist:**
- [ ] Cron job added
- [ ] Correct path set
- [ ] Script executable (`chmod +x validate-now.sh`)
- [ ] Test with: `bash validate-now.sh`

### Option 3: Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Databricks Documentation Validation"
4. Trigger: Weekly, Monday, 9:00 AM
5. Action: Start a program
   - Program: `cmd.exe`
   - Arguments: `/c cd C:\path\to\tests\validation && validate-now.bat`
   - Start in: `C:\path\to\tests\validation`
6. Finish and enable

**Checklist:**
- [ ] Task created in Task Scheduler
- [ ] Correct path configured
- [ ] Test manually from scheduler
- [ ] Verify it runs at scheduled time

---

## 🧪 Verification Tests

### Test 1: Manual Validation Request
```bash
python run_validation.py --scope api
# Should generate request file in results/
```
**Expected:** ✓ File created in `results/validation-request-*.txt`

### Test 2: Automated Validation
```bash
python agent_validator.py --provider anthropic --scope api
# Should run and generate report
```
**Expected:** ✓ Report created in `results/validation-report-*.md`

### Test 3: Configuration Valid
```bash
python -c "import json; json.load(open('validation-config.json')); print('✓ Config valid')"
```
**Expected:** ✓ Config valid

### Test 4: API Connection
```bash
python -c "
import anthropic
client = anthropic.Anthropic()
print('✓ API connection OK')
"
```
**Expected:** ✓ API connection OK

---

## 🎯 First Validation Goals

After your first validation:

1. **Review the accuracy score** - Aim for 85%+
2. **Check for critical issues** - Should be 0
3. **Identify high-priority items** - Plan to fix within 7 days
4. **Create tracking issues** - For medium/low priority items
5. **Schedule next validation** - Set up weekly runs

---

## ❗ Troubleshooting

### API Key Not Working

```bash
# Check if set
env | grep -E "ANTHROPIC|OPENAI"

# Test API directly
python -c "
import anthropic
try:
    client = anthropic.Anthropic()
    print('✓ API key valid')
except Exception as e:
    print(f'✗ Error: {e}')
"
```

### Module Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify installation
pip list | grep -E "anthropic|openai"
```

### Permission Errors

```bash
# Make scripts executable
chmod +x validate-now.sh

# Check file permissions
ls -la validate-now.sh
```

### Rate Limiting

```bash
# Use smaller batch size
python agent_validator.py --provider anthropic --scope api --batch-size 2

# Or validate incrementally
python agent_validator.py --provider anthropic --scope api
python agent_validator.py --provider anthropic --scope sdk
python agent_validator.py --provider anthropic --scope sql
```

---

## 📚 Next Steps

Once setup is complete:

1. **Read the guides:**
   - [Full Testing Guide](../TESTING-GUIDE.md)
   - [Quick Reference](QUICK-REFERENCE.md)
   - [Example Usage](EXAMPLE-USAGE.md)

2. **Review sample output:**
   - [Sample Report](results/SAMPLE-REPORT.md)

3. **Customize configuration:**
   - Edit `validation-config.json`
   - Adjust quality gates
   - Enable/disable validation types

4. **Set up integrations:**
   - GitHub Actions (automated)
   - Slack notifications (optional)
   - Jira integration (optional)

---

## 🎉 Success Criteria

Your validation system is ready when:

- ✅ First validation completes successfully
- ✅ Reports are generated in `results/`
- ✅ Accuracy score is calculated
- ✅ Issues are properly categorized
- ✅ You can interpret the findings
- ✅ Scheduled runs are configured
- ✅ Team is notified of setup

---

## 💡 Quick Commands Reference

```bash
# Run validation now
bash validate-now.sh

# View latest report
cat $(ls -t results/validation-report-*.md | head -1)

# Check accuracy
python -c "import json,glob; print(json.load(open(sorted(glob.glob('results/*.json'))[-1]))['total_accuracy'])"

# Count issues
grep -c "Severity: Critical" results/validation-report-*.md

# List all reports
ls -lt results/validation-report-*.md

# Clean old results
find results/ -name "validation-*" -mtime +90 -delete
```

---

## 📞 Support

If you get stuck:

1. Check [TESTING-GUIDE.md](../TESTING-GUIDE.md)
2. Review [README.md](README.md)
3. See [QUICK-REFERENCE.md](QUICK-REFERENCE.md)
4. Check workflow logs (if using GitHub Actions)

---

**Setup Time:** ~5 minutes  
**First Validation:** ~15 minutes  
**Total Time to Production:** ~30 minutes  

**Let's get started!** 🚀
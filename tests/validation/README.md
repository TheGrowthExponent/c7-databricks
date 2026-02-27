# Databricks Documentation Validation System

A comprehensive, AI-powered validation system that ensures your Databricks documentation is 100% accurate by comparing it against official Databricks documentation sources.

## Overview

This validation system uses AI agents (Claude, GPT-4, etc.) to systematically verify documentation accuracy, including:

- ✅ API endpoint accuracy
- ✅ Code example correctness
- ✅ Configuration values
- ✅ Feature availability
- ✅ Version compatibility
- ✅ Security best practices
- ✅ Deprecated feature detection

## Quick Start

### Prerequisites

```bash
# Install required packages
pip install anthropic  # For Claude API
# OR
pip install openai     # For OpenAI GPT-4

# Set API key (choose one)
export ANTHROPIC_API_KEY="your-api-key-here"
export OPENAI_API_KEY="your-api-key-here"
```

### Method 1: Automated Validation (Recommended)

Run fully automated validation using AI API:

```bash
# Full validation with Claude
python agent_validator.py --provider anthropic --scope full

# Validate specific scope
python agent_validator.py --provider anthropic --scope api

# Validate specific files
python agent_validator.py --provider anthropic --files "docs/api/*.md"

# Interactive mode with confirmation
python agent_validator.py --provider anthropic --scope full --interactive
```

### Method 2: Semi-Automated Validation

Generate validation request, then manually provide to AI:

```bash
# Generate validation request
python run_validation.py --scope full

# Follow on-screen instructions to:
# 1. Copy the generated validation request
# 2. Provide it to your AI assistant
# 3. Save the response
```

## Usage Examples

### Validate All Documentation

```bash
# Using Anthropic Claude (recommended)
python agent_validator.py --provider anthropic --scope full --interactive

# Using OpenAI GPT-4
python agent_validator.py --provider openai --scope full
```

### Validate Specific Areas

```bash
# API documentation only
python agent_validator.py --provider anthropic --scope api

# SDK documentation only
python agent_validator.py --provider anthropic --scope sdk

# SQL examples only
python agent_validator.py --provider anthropic --scope sql
```

### Validate Specific Files

```bash
# Single file
python agent_validator.py --provider anthropic --files "docs/api/clusters-api.md"

# Multiple files
python agent_validator.py --provider anthropic --files "docs/api/*.md" "docs/sdk/*.md"

# Pattern matching
python agent_validator.py --provider anthropic --files "docs/**/api*.md"
```

### Custom Batch Sizes

Control the number of files validated per API call:

```bash
# Smaller batches (more accurate, more API calls)
python agent_validator.py --provider anthropic --scope full --batch-size 2

# Larger batches (fewer API calls, may hit token limits)
python agent_validator.py --provider anthropic --scope full --batch-size 5
```

## Scheduled Validation

### Using Cron (Linux/Mac)

```bash
# Run every Monday at 9 AM
0 9 * * 1 cd /path/to/c7-databricks && python tests/validation/agent_validator.py --provider anthropic --scope full

# Add to crontab
crontab -e
# Then add the line above
```

### Using Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to Weekly (Monday, 9:00 AM)
4. Action: Start a program
5. Program: `python`
6. Arguments: `tests/validation/agent_validator.py --provider anthropic --scope full`
7. Start in: `C:\path\to\c7-databricks`

### Using GitHub Actions

Create `.github/workflows/validate-docs.yml`:

```yaml
name: Documentation Validation

on:
  schedule:
    - cron: "0 9 * * 1" # Every Monday at 9 AM UTC
  workflow_dispatch: # Manual trigger

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          pip install anthropic

      - name: Run validation
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python tests/validation/agent_validator.py --provider anthropic --scope full

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: validation-results
          path: tests/validation/results/
```

## Understanding Results

### Report Location

Validation reports are saved in `tests/validation/results/`:

```
results/
├── validation-report-20240115-093045.md      # Human-readable summary
├── validation-report-20240115-093045.json    # Machine-readable data
├── validation-raw-20240115-093045-batch1.md  # Detailed batch 1 analysis
├── validation-raw-20240115-093045-batch2.md  # Detailed batch 2 analysis
└── validation-request-20240115-093045.txt    # Original request
```

### Accuracy Scores

- **95-100%** 🟢 EXCELLENT - Documentation is highly accurate
- **90-95%** 🟡 GOOD - Minor issues, mostly cosmetic
- **85-90%** 🟠 NEEDS IMPROVEMENT - Several issues to address
- **<85%** 🔴 REQUIRES ATTENTION - Significant accuracy problems

### Issue Severity

- **🔴 CRITICAL** - Breaking errors that will cause user failures (fix immediately)
- **🟠 HIGH** - Significant issues impacting usability (fix within 7 days)
- **🟡 MEDIUM** - Minor inconsistencies (fix within 30 days)
- **🔵 LOW** - Cosmetic or style issues (fix as time permits)

### Quality Gates

The validation checks against these quality gates:

| Gate                | Default Threshold | Description                           |
| ------------------- | ----------------- | ------------------------------------- |
| Minimum Accuracy    | 85%               | Overall accuracy score must meet this |
| Max Critical Issues | 0                 | No critical issues allowed            |
| Max High Issues     | 5                 | Limited high-priority issues          |

## Configuration

### Edit `validation-config.json`

Customize validation behavior:

```json
{
  "schedule": {
    "frequency": "weekly",
    "day": "monday",
    "time": "09:00"
  },
  "quality_gates": {
    "minimum_accuracy_score": 85,
    "maximum_critical_issues": 0,
    "maximum_high_issues": 5
  },
  "agent_configuration": {
    "model": "claude-sonnet-4.5",
    "temperature": 0.1,
    "max_tokens": 4000
  }
}
```

### Key Configuration Options

- `scope.validation_types` - Types of validation to perform
- `official_sources` - Official Databricks documentation URLs
- `validation_rules` - Enable/disable specific checks
- `severity_levels` - Customize severity definitions
- `accuracy_thresholds` - Define accuracy grade thresholds
- `reporting.notification` - Configure notifications

## Advanced Usage

### Custom Validation Prompt

Modify `VALIDATION_AGENT_PROMPT.md` to customize:

- Validation criteria
- Output format
- Specific checks to perform
- Focus areas

### Process Existing Agent Response

If you already have an agent validation response:

```bash
python run_validation.py --process-response path/to/response.md
```

### Integration with CI/CD

```bash
# Run validation and fail build if quality gates not met
python agent_validator.py --provider anthropic --scope full
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "Documentation validation failed!"
  exit 1
fi
```

### Filter by Validation Type

Edit `validation-config.json` to focus on specific validation types:

```json
{
  "scope": {
    "validation_types": ["api_accuracy", "code_syntax", "security_best_practices"]
  }
}
```

## Troubleshooting

### API Key Issues

```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY

# Test API connection
python -c "import anthropic; client = anthropic.Anthropic(); print('Connection OK')"
```

### Rate Limiting

If you hit API rate limits:

1. Reduce `batch_size` parameter
2. Increase delay in `agent_validator.py` (line ~483)
3. Validate smaller scopes in separate runs

### Token Limits

If you hit token limits:

1. Reduce `batch_size` to 1-2 files
2. Reduce `max_tokens` in config
3. Validate shorter files first

### Import Errors

```bash
# Install missing dependencies
pip install anthropic openai

# Verify installation
python -c "import anthropic; print('OK')"
```

## Best Practices

### 1. Regular Validation

Run validation:

- **Weekly**: Automated scheduled runs
- **Pre-release**: Before major documentation updates
- **Post-update**: After Databricks platform updates
- **On-demand**: When official docs are updated

### 2. Incremental Validation

For large repositories:

```bash
# Day 1: API docs
python agent_validator.py --provider anthropic --scope api

# Day 2: SDK docs
python agent_validator.py --provider anthropic --scope sdk

# Day 3: Examples
python agent_validator.py --provider anthropic --scope examples
```

### 3. Track Trends

Compare validation results over time:

```bash
# Check accuracy trends
ls -lt tests/validation/results/validation-report-*.json | head -5
```

### 4. Prioritize Fixes

Focus on:

1. Critical issues first (user-breaking)
2. High priority issues (usability impact)
3. Security-related issues
4. API/SDK accuracy issues

### 5. Document Changes

When fixing issues:

- Reference validation report ID
- Include official documentation URL
- Note the specific change made

## API Cost Estimation

### Anthropic Claude

- Model: Claude Sonnet 4.5
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens
- Typical validation: 50,000 input + 5,000 output tokens
- **Estimated cost per full validation**: $0.15 - $0.30

### OpenAI GPT-4

- Model: GPT-4 Turbo
- Input: ~$10 per million tokens
- Output: ~$30 per million tokens
- Typical validation: 50,000 input + 5,000 output tokens
- **Estimated cost per full validation**: $0.50 - $0.75

## Support & Feedback

### Getting Help

1. Check validation logs in console output
2. Review detailed batch reports in `results/`
3. Verify configuration in `validation-config.json`
4. Ensure API keys are properly set

### Reporting Issues

When validation finds incorrect issues:

1. Check official Databricks documentation yourself
2. Verify the validation is actually wrong
3. Update the validation prompt or configuration
4. Consider that official docs may sometimes be outdated

### Contributing

Improvements welcome:

- Enhanced parsing of agent responses
- Additional validation rules
- New AI provider integrations
- Better report formatting

## Examples

### Example 1: Weekly Validation Report

```bash
# Run scheduled validation
python agent_validator.py --provider anthropic --scope full

# Results:
# ✅ Accuracy: 94% (GOOD)
# 🔴 Critical: 0
# 🟠 High: 3
# 🟡 Medium: 8
# 🔵 Low: 12
```

### Example 2: Pre-Release Check

```bash
# Validate before v2.0 release
python agent_validator.py --provider anthropic --scope full --interactive

# Quality gates:
# ✅ Accuracy > 85%
# ✅ Critical issues = 0
# ✅ High issues <= 5
# Ready for release!
```

### Example 3: Focus on API Changes

```bash
# Validate after Databricks API update
python agent_validator.py --provider anthropic --files "docs/api/*.md"

# Review detailed findings
cat tests/validation/results/validation-raw-*.md
```

## Quick Reference

| Command                                                              | Description                    |
| -------------------------------------------------------------------- | ------------------------------ |
| `python agent_validator.py --provider anthropic --scope full`        | Full validation                |
| `python agent_validator.py --provider anthropic --scope api`         | API docs only                  |
| `python agent_validator.py --provider anthropic --files "path/*.md"` | Specific files                 |
| `python agent_validator.py --help`                                   | Show all options               |
| `python run_validation.py --scope full`                              | Generate request (manual mode) |

## References

- [Validation Agent Prompt](VALIDATION_AGENT_PROMPT.md) - Detailed validation instructions
- [Configuration Guide](validation-config.json) - Full configuration options
- [Databricks Official Docs](https://docs.databricks.com) - Source of truth

---

**Version**: 1.0.0
**Last Updated**: 2026-02-27
**Maintained By**: Documentation Team

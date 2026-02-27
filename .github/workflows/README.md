# GitHub Actions Workflows

Automated CI/CD workflows for Databricks documentation validation and quality assurance.

---

## Overview

This directory contains GitHub Actions workflows that automatically validate and test the Databricks documentation repository.

### Available Workflows

| Workflow                     | File                         | Trigger                    | Purpose                                            |
| ---------------------------- | ---------------------------- | -------------------------- | -------------------------------------------------- |
| **Documentation Validation** | `validate-documentation.yml` | Schedule, Push, PR, Manual | Validates docs against official Databricks sources |

---

## Documentation Validation Workflow

Automated validation using AI agents to ensure documentation accuracy.

### Triggers

**1. Scheduled**

- Runs every Monday at 9:00 AM UTC
- Full validation of all documentation

**2. Push to Main**

- Triggers when documentation files are modified
- Validates changed docs only

**3. Pull Request**

- Runs when PR modifies documentation
- Blocks merge if quality gates fail

**4. Manual Dispatch**

- Can be triggered from GitHub Actions tab
- Allows custom scope and provider selection

### Configuration

#### Required Secrets

Set these in repository settings → Secrets and variables → Actions:

```
ANTHROPIC_API_KEY    # For Claude validation (recommended)
OPENAI_API_KEY       # For GPT-4 validation (alternative)
```

#### Workflow Inputs (Manual Trigger)

When manually triggering the workflow:

- **scope**: `full`, `api`, `sdk`, `sql`, `examples`
- **provider**: `anthropic`, `openai`

### Quality Gates

The workflow enforces these quality standards:

| Gate                | Threshold | Action on Failure     |
| ------------------- | --------- | --------------------- |
| Minimum Accuracy    | 85%       | Fail PR build         |
| Max Critical Issues | 0         | Create issue, fail PR |
| Max High Issues     | 5         | Warning               |

### Outputs

**1. Validation Reports**

- Uploaded as workflow artifacts
- Available for 90 days
- Includes markdown and JSON formats

**2. GitHub Issues**

- Automatically created for critical findings
- Tagged with `documentation`, `critical`, `validation`

**3. PR Comments**

- Validation results posted to PR
- Shows accuracy score and issue count
- Indicates pass/fail status

**4. Workflow Summary**

- Quick overview in Actions tab
- Accuracy score and issue breakdown

---

## Usage

### Manual Trigger

1. Go to **Actions** tab in GitHub
2. Select **Documentation Validation** workflow
3. Click **Run workflow**
4. Choose:
   - **Branch**: Usually `main`
   - **Scope**: Validation scope
   - **Provider**: AI provider to use
5. Click **Run workflow** button

### View Results

**Workflow Run:**

1. Go to Actions tab
2. Click on workflow run
3. View summary and logs

**Download Reports:**

1. Scroll to workflow artifacts
2. Download `validation-results-[run-number]`
3. Extract and review reports

**Check Issues:**

1. Go to Issues tab
2. Filter by `validation` label
3. Review critical findings

### PR Integration

When you create a PR that modifies documentation:

1. ✅ Workflow runs automatically
2. 📊 Results posted as PR comment
3. ✅/❌ Status check appears
4. 🚫 Merge blocked if critical issues found

Example PR comment:

```markdown
## 🟢 Documentation Validation Results

**Status**: ✅ PASSED
**Accuracy**: 94.5%

### Issues Found

- 🔴 Critical: 0
- 🟠 High: 2

📊 Full validation report available in workflow artifacts.
```

---

## Workflow Details

### Jobs

**validate-docs**

- Sets up Python 3.10
- Installs dependencies (`anthropic`, `openai`)
- Runs validation with specified scope and provider
- Uploads results as artifacts
- Creates GitHub issue if critical issues found
- Posts PR comment with summary
- Checks quality gates

**notify** (on failure)

- Runs if scheduled validation fails
- Can be extended with Slack/email notifications

### Environment Variables

```yaml
ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Artifacts

Validation results stored for 90 days:

```
validation-results-[run-number]/
├── validation-report-[timestamp].md
├── validation-report-[timestamp].json
└── validation-raw-[timestamp]-batch*.md
```

---

## Customization

### Change Schedule

Edit `validate-documentation.yml`:

```yaml
on:
  schedule:
    - cron: "0 9 * * 1" # Monday 9 AM UTC
```

Common schedules:

- Daily: `'0 9 * * *'`
- Weekly: `'0 9 * * 1'` (Monday)
- Bi-weekly: `'0 9 * * 1/2'`
- Monthly: `'0 9 1 * *'` (1st of month)

### Change Quality Gates

Edit workflow or `tests/validation/validation-config.json`:

```yaml
- name: Check quality gates
  run: |
    if [ "$CRITICAL" -gt 0 ]; then
      exit 1  # Fail on any critical
    fi
    if (( $(echo "$ACCURACY < 85" | bc -l) )); then
      exit 1  # Fail if accuracy < 85%
    fi
```

### Add Notifications

Extend the `notify` job:

```yaml
- name: Send Slack notification
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Documentation validation failed!"
      }
```

### Validate Only Changed Files

Modify to validate only PR changes:

```yaml
- name: Get changed files
  id: changed-files
  run: |
    echo "files=$(git diff --name-only ${{ github.event.before }} ${{ github.sha }} | grep '^docs/' | tr '\n' ' ')" >> $GITHUB_OUTPUT

- name: Run validation
  run: |
    python agent_validator.py \
      --provider anthropic \
      --files ${{ steps.changed-files.outputs.files }}
```

---

## Troubleshooting

### Workflow Fails: API Key Not Found

**Problem:**

```
Error: API key not found. Set ANTHROPIC_API_KEY environment variable.
```

**Solution:**

1. Go to Settings → Secrets and variables → Actions
2. Add `ANTHROPIC_API_KEY` secret
3. Re-run workflow

### Workflow Fails: Rate Limiting

**Problem:**

```
Error 429: Rate limit exceeded
```

**Solution:**

- Reduce batch size in workflow
- Add delays between API calls
- Use different validation schedule

### Workflow Fails: Token Limit

**Problem:**

```
Error: Token limit exceeded
```

**Solution:**

- Reduce scope (validate in batches)
- Decrease max_tokens in config
- Split into multiple workflow runs

### Artifacts Not Available

**Problem:**
Can't find validation reports

**Solution:**

- Check workflow completed successfully
- Look in "Artifacts" section at bottom of workflow run
- Artifacts expire after 90 days (retention setting)

---

## Cost Estimation

### GitHub Actions

- **Free tier**: 2,000 minutes/month for private repos
- **Public repos**: Unlimited free
- **Typical run**: 5-10 minutes
- **Weekly schedule**: ~40 minutes/month

### AI API Costs

**Anthropic Claude:**

- Per validation: $0.15 - $0.30
- Weekly (4x/month): ~$1.20/month

**OpenAI GPT-4:**

- Per validation: $0.50 - $0.75
- Weekly (4x/month): ~$3.00/month

**Total Monthly Cost:** $1-3 for weekly validation

---

## Best Practices

### 1. Use Secrets for API Keys

```yaml
# ✅ Correct
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

# ❌ Never do this
env:
  ANTHROPIC_API_KEY: "sk-ant-actual-key-here"
```

### 2. Set Appropriate Timeouts

```yaml
- name: Run validation
  timeout-minutes: 30 # Prevent hanging
  run: python agent_validator.py --provider anthropic --scope full
```

### 3. Cache Dependencies

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.10"
    cache: "pip" # Cache pip dependencies
```

### 4. Use Conditional Execution

```yaml
# Only run on doc changes
- name: Run validation
  if: contains(github.event.head_commit.modified, 'docs/')
  run: python agent_validator.py
```

### 5. Handle Failures Gracefully

```yaml
- name: Run validation
  continue-on-error: true # Don't block other steps
  id: validation
  run: python agent_validator.py

- name: Post results
  if: always() # Run even if validation failed
  run: echo "Results available"
```

---

## Security Considerations

### API Keys

- ✅ Store in GitHub Secrets
- ✅ Never commit to repository
- ✅ Rotate regularly
- ✅ Use read-only keys when possible

### Workflow Permissions

```yaml
permissions:
  contents: read
  issues: write
  pull-requests: write
```

### Third-Party Actions

- ✅ Pin to specific versions (e.g., `@v4`)
- ✅ Review action code before use
- ✅ Use verified creators when possible

---

## Monitoring

### Check Workflow Health

```bash
# View recent workflow runs
gh workflow view "Documentation Validation"

# List failed runs
gh run list --workflow="Documentation Validation" --status=failure
```

### Track Metrics

Monitor over time:

- Validation frequency
- Accuracy trends
- Issue counts
- Workflow duration
- Failure rates

### Set Up Alerts

Configure notifications for:

- Failed scheduled validations
- Critical issues found
- Quality gate failures
- Workflow errors

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Validation System Guide](../../tests/TESTING-GUIDE.md)
- [Testing Quick Reference](../../tests/validation/QUICK-REFERENCE.md)

---

## Support

### Getting Help

1. Check workflow logs in Actions tab
2. Review validation reports in artifacts
3. See [Testing Guide](../../tests/TESTING-GUIDE.md)
4. Check workflow run annotations

### Common Issues

- **Setup**: See [Troubleshooting](#troubleshooting)
- **Configuration**: Edit `validate-documentation.yml`
- **Secrets**: Settings → Secrets and variables
- **Permissions**: Settings → Actions → General

---

**Maintained By**: Documentation Team
**Last Updated**: 2026-02-27
**Version**: 1.0.0

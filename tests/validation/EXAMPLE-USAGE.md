# Example: Using the Validation System with Any AI Assistant

This document provides ready-to-use examples for validating your Databricks documentation with AI assistants like Claude, ChatGPT, or any LLM.

---

## Quick Copy-Paste Prompt

### For First-Time Validation

Copy and paste this entire prompt to your AI assistant:

```
You are a Databricks documentation validation expert. Please validate the following Databricks documentation against the official Databricks documentation at https://docs.databricks.com

VALIDATION REQUEST:

Please systematically check this documentation for:
1. API endpoint accuracy (URLs, parameters, request/response formats)
2. Code example correctness (syntax, imports, best practices)
3. Configuration value accuracy (keys, defaults, types)
4. Feature availability (versions, tiers, prerequisites)
5. Deprecated features or outdated information
6. Security best practices

For each issue found, provide:
- Severity (Critical/High/Medium/Low)
- File location and line numbers
- Description of the issue
- What it should say (based on official docs)
- URL to official Databricks documentation
- Recommended fix

Generate a comprehensive report with:
- Executive summary with accuracy score (0-100%)
- Count of issues by severity
- Detailed findings for each file
- Priority action items

Here are the documentation files to validate:

[PASTE YOUR DOCUMENTATION FILES HERE]

File 1: docs/api/clusters-api.md
```

[paste file content]

```

File 2: docs/api/jobs-api.md
```

[paste file content]

```

[Continue for all files you want to validate]

Please provide a detailed validation report now.
```

---

## Example 1: Validate API Documentation

### Prompt:

````
I need you to validate this Databricks API documentation against the official Databricks API reference at https://docs.databricks.com/api/workspace/introduction

Please check:
- Are endpoint URLs correct?
- Are all required parameters documented?
- Are request/response schemas accurate?
- Are authentication requirements correct?
- Is the API version current?

Here's the documentation:

```markdown
# Databricks Clusters API

The Clusters API allows you to create, manage, and delete Databricks clusters.

## Create Cluster

**Endpoint**: `POST /api/2.0/clusters/create`

**Request Body**:
```json
{
  "cluster_name": "my-cluster",
  "spark_version": "11.3.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "num_workers": 2
}
````

**Response**: Returns cluster ID

```

```

Rate accuracy 0-100% and list any issues with official documentation URLs.

```

---

## Example 2: Validate Code Examples

### Prompt:
```

Please validate this Python code example for Databricks SDK usage. Check against the official Python SDK documentation at https://databricks-sdk-py.readthedocs.io/

Verify:

- Import statements are correct
- Class and method names are accurate
- Parameter types match SDK
- Authentication pattern is current
- Best practices are followed

Code to validate:

```python
from databricks.sdk import WorkspaceClient

client = WorkspaceClient()

# List clusters
clusters = client.clusters.list()
for cluster in clusters:
    print(cluster.cluster_name)
```

Is this code correct? List any issues with severity and corrections.

```

---

## Example 3: Validate SQL Syntax

### Prompt:
```

Validate this Databricks SQL documentation against the official SQL reference at https://docs.databricks.com/sql/language-manual/

Check:

- SQL syntax is valid for Databricks SQL
- Delta Lake syntax is correct
- Function signatures are accurate
- Examples are runnable

Documentation to validate:

```sql
-- Merge data into Delta table
MERGE INTO target_table t
USING source_table s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

Is this syntax correct and current? Provide accuracy score and any corrections needed.

```

---

## Example 4: Comprehensive Multi-File Validation

### Prompt Template:
```

You are a Databricks documentation validation expert. I need a comprehensive validation of multiple documentation files against official Databricks sources.

VALIDATION REQUIREMENTS:

1. **API Accuracy**: Compare against https://docs.databricks.com/api/workspace/introduction
   - Endpoint URLs, HTTP methods, parameters, request/response schemas

2. **Code Examples**: Verify syntax and patterns
   - Python SDK: https://databricks-sdk-py.readthedocs.io/
   - Correct imports, method signatures, error handling

3. **SQL Syntax**: Validate against https://docs.databricks.com/sql/language-manual/
   - Delta Lake syntax, function calls, data types

4. **Configuration**: Verify settings
   - Config keys, default values, data types

5. **Security**: Check best practices
   - Secrets management, authentication, access control

6. **Deprecations**: Identify outdated features
   - Check release notes at https://docs.databricks.com/release-notes/

OUTPUT FORMAT:

# Databricks Documentation Validation Report

**Date**: [Current Date]
**Accuracy Score**: [0-100]%

## Executive Summary

- Total Files: [N]
- Critical Issues: [N]
- High Priority: [N]
- Medium Priority: [N]
- Low Priority: [N]

## Detailed Findings

### File: [filename]

**Accuracy**: [score]%

#### Issue 1: [Title]

- **Severity**: [Critical/High/Medium/Low]
- **Location**: Lines [X-Y]
- **Current**: [What it says now]
- **Expected**: [What it should say]
- **Source**: [Official docs URL]
- **Action**: [How to fix]

[Repeat for each issue]

## Priority Actions

1. [Critical issue summary] - File:Line
2. [High issue summary] - File:Line
   [etc.]

---

FILES TO VALIDATE:

### File 1: docs/api/clusters-api.md

```
[PASTE CONTENT]
```

### File 2: docs/sdk/python-sdk.md

```
[PASTE CONTENT]
```

### File 3: docs/sql/delta-queries.md

```
[PASTE CONTENT]
```

[Add more files as needed]

Please generate the validation report now with specific, actionable findings.

```

---

## Example 5: Quick Single-File Check

### Prompt:
```

Quick validation request:

Compare this documentation against official Databricks docs and rate accuracy 0-100%. List top 3 issues if any.

File: docs/api/jobs-api.md

```
# Jobs API

Create jobs with POST /api/2.0/jobs/create

Required parameters:
- name: string
- tasks: array
```

Accuracy score and issues?

````

---

## Real-World Usage Example

### Scenario: Weekly Documentation Review

**Step 1**: Generate validation request
```bash
cd tests/validation
python run_validation.py --scope full
````

**Step 2**: Open the generated request file

```bash
cat results/validation-request-20240115-093045.txt
```

**Step 3**: Copy the entire content

**Step 4**: Paste into Claude or ChatGPT

**Step 5**: Wait for detailed validation report

**Step 6**: Save the AI's response to a file

```bash
# Save AI response
cat > results/validation-response-20240115-093045.md
[PASTE AI RESPONSE]
[CTRL+D]
```

**Step 7**: Review findings and create tasks

---

## Example Output You'll Receive

When you use these prompts, you'll get responses like:

```markdown
# Databricks Documentation Validation Report

**Accuracy Score**: 92.5%

## Executive Summary

- Total Files: 5
- Critical Issues: 0
- High Priority: 3
- Medium Priority: 7
- Low Priority: 12

## Detailed Findings

### File: docs/api/jobs-api.md

**Accuracy**: 88%

#### Issue 1: Deprecated API Version

- **Severity**: High
- **Location**: Lines 12-15
- **Current**: References Jobs API 2.0
- **Expected**: Should reference Jobs API 2.1
- **Source**: https://docs.databricks.com/api/workspace/jobs
- **Action**: Update all references from 2.0 to 2.1, note 2.0 compatibility

#### Issue 2: Missing Required Parameter

- **Severity**: High
- **Location**: Lines 45-52
- **Current**: Example missing timeout_seconds
- **Expected**: Include timeout_seconds: 0 in example
- **Source**: https://docs.databricks.com/api/workspace/jobs/create
- **Action**: Add timeout_seconds to all job creation examples

[... more issues ...]

## Priority Actions

1. Update Jobs API version references (High) - docs/api/jobs-api.md:12-15
2. Add missing required parameters (High) - docs/api/jobs-api.md:45-52
3. Update deprecated SDK patterns (Medium) - docs/examples/etl.py:78-82

## Recommendations

- Set up automated weekly validation
- Add version badges to documentation
- Create API version migration guide
```

---

## Tips for Best Results

### 1. Be Specific

```
❌ "Check if this is correct"
✅ "Validate this against official Databricks Clusters API docs at https://docs.databricks.com/api/workspace/clusters"
```

### 2. Provide Context

```
✅ "This documentation targets Databricks Runtime 13.x and SDK version 0.18.0"
```

### 3. Request Structured Output

```
✅ "Provide findings in this format: Severity | Location | Issue | Fix | Source URL"
```

### 4. Ask for Sources

```
✅ "Include URLs to official documentation for every finding"
```

### 5. Specify Validation Depth

```
✅ "Deep validation: check every parameter, data type, and example"
```

---

## Common Validation Questions

### Q: "Is this API endpoint correct?"

```
Validate this endpoint against https://docs.databricks.com/api/workspace/introduction:

POST /api/2.0/clusters/create

Is the URL, HTTP method, and API version correct?
```

### Q: "Is this code example up to date?"

````
Check if this Python SDK code follows current best practices per https://databricks-sdk-py.readthedocs.io/:

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
````

Is this the recommended pattern?

```

### Q: "Are these configuration values correct?"
```

Verify these Spark configuration values against official docs:

spark.sql.adaptive.enabled = true
spark.databricks.delta.optimizeWrite.enabled = true

Are these keys and defaults correct?

```

---

## Integration with Your Workflow

### Daily Usage
```

Morning: Run validation on new/changed files
Afternoon: Review findings
Evening: Create fix tickets

```

### Weekly Review
```

Monday: Full validation run
Tuesday: Review critical/high issues
Wednesday: Implement fixes
Thursday: Re-validate
Friday: Update documentation standards

```

### Release Process
```

Pre-release: Full validation
Fix critical issues: Must pass
Fix high issues: Should pass
Document medium/low: Track in backlog
Final validation: Confirm >85% accuracy
Release: Ship with confidence

```

---

## Cost-Effective Validation

### Free Options
1. Use Claude.ai or ChatGPT web interface (copy/paste)
2. Validate small batches of files
3. Focus on changed files only

### Paid API (Automated)
1. Use `agent_validator.py` with API key
2. Batch multiple files efficiently
3. Schedule weekly runs
4. Cost: ~$1-3/month for weekly validation

---

## Success Stories

### Before Validation
- 15 critical API errors
- Deprecated code in 23 examples
- 67% accuracy score
- User complaints about docs

### After Regular Validation
- 0 critical errors
- All examples current
- 94% accuracy score
- Positive user feedback

---

## Next Steps

1. **Try it now**: Copy the "Quick Copy-Paste Prompt" above
2. **Paste into AI**: Use Claude, ChatGPT, or your preferred AI
3. **Review results**: Check the validation report
4. **Fix issues**: Start with critical and high priority
5. **Automate**: Set up scheduled validation with `agent_validator.py`

---

## Resources

- [Full Validation Prompt](VALIDATION_AGENT_PROMPT.md)
- [Configuration Guide](validation-config.json)
- [Testing Guide](../TESTING-GUIDE.md)
- [Quick Reference](QUICK-REFERENCE.md)

---

**Start validating now!** Your documentation quality depends on it.

**Version**: 1.0.0
**Updated**: 2026-02-27
```

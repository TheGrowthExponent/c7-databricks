# Query LLMs and Prototype AI Agents with AI Playground

## Overview

This tutorial introduces you to Databricks AI Playground, a no-code interface for querying large language models (LLMs), comparing results side-by-side, prototyping tool-calling AI agents, and exporting your work to code. AI Playground makes it easy to experiment with foundation models without writing code.

## Prerequisites

- Access to a Databricks workspace with AI Playground enabled
- Permissions to use Foundation Model APIs
- No coding experience required (but helpful for export features)

## What You'll Learn

- How to access and use AI Playground
- How to query different LLMs and compare results
- How to adjust model parameters for different use cases
- How to prototype tool-calling AI agents
- How to export prompts and agents to code
- Best practices for prompt engineering

## Step 1: Access AI Playground

### Navigate to AI Playground

1. In your Databricks workspace, click **AI Playground** in the left sidebar
2. Alternatively, go to **Machine Learning** → **AI Playground**
3. The playground interface will open with model selection options

### Interface Overview

The AI Playground interface includes:

- **Model Selector**: Choose from available LLMs
- **Prompt Area**: Enter your prompts and questions
- **Response Area**: View model responses
- **Parameters Panel**: Adjust temperature, max tokens, etc.
- **Comparison Mode**: Compare multiple models side-by-side
- **Export Options**: Export to notebook, API code, or agent

## Step 2: Query Your First LLM

### Basic Query Example

1. **Select a Model**: Click the model dropdown and select `llama-3.1-70b-instruct` (or another available model)

2. **Enter a Prompt**:
   ```
   Explain what Apache Spark is in simple terms for a beginner.
   ```

3. **Click "Run"** or press `Ctrl+Enter`

4. **Review the Response**: The model will generate a response explaining Spark

### Example Prompts to Try

#### Information Retrieval
```
What are the key differences between Delta Lake and traditional data lakes?
```

#### Code Generation
```
Write a Python function that reads a CSV file using PySpark and returns the top 10 rows sorted by a specific column.
```

#### Data Analysis
```
Given a dataset of sales transactions with columns: date, product_id, quantity, price, region
Suggest 5 interesting analytical questions I could answer with this data.
```

#### SQL Query Generation
```
I have a table called 'customers' with columns: customer_id, name, email, signup_date, country
Write a SQL query to find customers who signed up in the last 30 days, grouped by country.
```

## Step 3: Adjust Model Parameters

### Understanding Key Parameters

#### Temperature (0.0 - 1.0)
- **Low (0.0 - 0.3)**: Deterministic, focused responses
  - Use for: Code generation, factual answers, SQL queries
- **Medium (0.4 - 0.7)**: Balanced creativity and consistency
  - Use for: General questions, explanations, summaries
- **High (0.8 - 1.0)**: Creative, diverse responses
  - Use for: Brainstorming, creative writing, ideation

#### Max Tokens
- Controls maximum length of response
- 1 token ≈ 4 characters or 0.75 words
- Examples:
  - 100 tokens: Short answer (1-2 paragraphs)
  - 500 tokens: Medium response (page of text)
  - 2000 tokens: Long, detailed response

#### Top P (Nucleus Sampling)
- Alternative to temperature
- Range: 0.0 - 1.0
- Controls diversity of word selection
- 0.9 is typical for most use cases

### Experiment with Parameters

**Example: Code Generation (Low Temperature)**
```
Temperature: 0.1
Max Tokens: 500
Prompt: Write a Python function to calculate fibonacci numbers using recursion.
```

**Example: Creative Brainstorming (High Temperature)**
```
Temperature: 0.9
Max Tokens: 1000
Prompt: Suggest 10 creative names for a data analytics platform.
```

## Step 4: Compare Models Side-by-Side

### Enable Comparison Mode

1. Click **"Add model for comparison"** button
2. Select a second model (e.g., `mixtral-8x7b-instruct`)
3. Enter the same prompt in both panels
4. Click **"Run Both"**

### Comparison Example

**Prompt:**
```
Analyze the pros and cons of using a medallion architecture (Bronze/Silver/Gold)
for a data lakehouse implementation.
```

**Models to Compare:**
- Model 1: `llama-3.1-70b-instruct`
- Model 2: `dbrx-instruct`

**What to Look For:**
- Response quality and depth
- Accuracy of technical details
- Structure and clarity
- Response time
- Token usage

### Use Cases for Model Comparison

1. **Quality Assessment**: Which model gives better technical accuracy?
2. **Speed vs Quality**: Balance between response time and detail
3. **Cost Optimization**: Smaller models for simple tasks, larger for complex
4. **Task Suitability**: Different models excel at different tasks

## Step 5: Advanced Prompting Techniques

### Structured Prompts

**Poor Prompt:**
```
Tell me about data quality
```

**Better Prompt:**
```
Explain data quality in the context of modern data engineering.
Include:
1. Definition and importance
2. Common data quality dimensions (accuracy, completeness, consistency, etc.)
3. Tools and techniques for data quality validation
4. Impact of poor data quality on analytics
```

### Few-Shot Learning

**Prompt with Examples:**
```
Convert natural language to SQL queries:

Example 1:
Input: Show all customers from California
Output: SELECT * FROM customers WHERE state = 'CA';

Example 2:
Input: Count orders by product category
Output: SELECT category, COUNT(*) FROM orders GROUP BY category;

Now convert this:
Input: Find the top 5 customers by total purchase amount in the last year
Output:
```

### Chain of Thought Prompting

**Prompt:**
```
Let's think step by step.

Problem: I have a DataFrame with 10 million rows and need to join it with another
DataFrame of 5 million rows. The join is slow. How can I optimize it?

Think through:
1. What could be causing the slowness?
2. What information do I need to diagnose the issue?
3. What optimization techniques could help?
4. Provide specific PySpark code examples.
```

### Role-Based Prompting

**Prompt:**
```
You are a senior data engineer with 10 years of experience in building
large-scale ETL pipelines on Databricks.

A junior engineer asks: "Should I use Delta Live Tables or traditional
Spark Structured Streaming for our new real-time analytics pipeline?"

Provide a detailed, practical answer considering:
- Use case suitability
- Maintenance overhead
- Learning curve
- Cost implications
```

## Step 6: Prototype Tool-Calling AI Agents

### Understanding AI Agents

AI agents can:
- Make decisions based on user input
- Call external tools and functions
- Retrieve information from databases
- Execute code or queries
- Chain multiple actions together

### Create a Simple Agent

1. In AI Playground, click **"Agent"** tab
2. Click **"Create New Agent"**
3. Configure agent settings:

**Agent Configuration Example:**

```yaml
Name: Data Analysis Assistant
Description: Helps users analyze data in Unity Catalog

System Prompt:
You are a data analysis assistant. You help users query and analyze data
stored in Unity Catalog tables. Always verify table existence before querying.

Available Tools:
- list_tables: Get list of available tables in a schema
- execute_query: Run SQL queries on Unity Catalog tables
- describe_table: Get schema information for a table
- generate_visualization: Create charts from query results
```

### Define Agent Tools

**Tool Definition Example:**

```python
# Tool 1: List Tables
{
  "name": "list_tables",
  "description": "Lists all tables in a Unity Catalog schema",
  "parameters": {
    "schema_name": {
      "type": "string",
      "description": "Name of the schema (e.g., 'main.sales')"
    }
  }
}

# Tool 2: Execute Query
{
  "name": "execute_query",
  "description": "Executes a SQL query and returns results",
  "parameters": {
    "query": {
      "type": "string",
      "description": "SQL query to execute"
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of rows to return",
      "default": 100
    }
  }
}
```

### Test Agent Interactions

**User Query:**
```
Show me the top 5 customers by purchase amount from the sales database
```

**Agent Response Flow:**
1. Agent calls `list_tables("main.sales")` to verify tables exist
2. Agent calls `describe_table("main.sales.customers")` to understand schema
3. Agent generates SQL query
4. Agent calls `execute_query()` with the SQL
5. Agent presents results to user

### Example Agent Conversations

**Conversation 1: Data Discovery**
```
User: What tables are available in the analytics schema?
Agent: [Calls list_tables] Here are the tables in main.analytics:
- customer_metrics
- daily_sales_summary
- product_inventory

User: What columns does customer_metrics have?
Agent: [Calls describe_table] The customer_metrics table has:
- customer_id (BIGINT)
- total_purchases (BIGINT)
- lifetime_value (DECIMAL)
- first_purchase_date (DATE)
- last_purchase_date (DATE)
```

**Conversation 2: Analysis Request**
```
User: Calculate the average lifetime value by month of first purchase
Agent: [Generates and executes query]
SELECT
  DATE_TRUNC('month', first_purchase_date) as month,
  AVG(lifetime_value) as avg_ltv,
  COUNT(*) as customer_count
FROM main.analytics.customer_metrics
GROUP BY DATE_TRUNC('month', first_purchase_date)
ORDER BY month;

Results: [Shows query results]
```

## Step 7: Export to Code

### Export Prompt to Notebook

1. After getting a satisfactory response, click **"Export"**
2. Select **"Export to Notebook"**
3. Choose export format:
   - **API Call**: Direct API code
   - **Langchain**: Using Langchain framework
   - **Complete Notebook**: Full working notebook

### Example: Export as API Call

```python
# Exported from AI Playground
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

client = WorkspaceClient()

response = client.serving_endpoints.query(
    name="databricks-llama-3-1-70b-instruct",
    messages=[
        ChatMessage(
            role=ChatMessageRole.SYSTEM,
            content="You are a helpful data engineering assistant."
        ),
        ChatMessage(
            role=ChatMessageRole.USER,
            content="Explain the medallion architecture in data lakehouses."
        )
    ],
    temperature=0.7,
    max_tokens=500
)

print(response.choices[0].message.content)
```

### Example: Export as Langchain

```python
# Exported from AI Playground - Langchain format
from langchain.chat_models import ChatDatabricks
from langchain.schema import HumanMessage, SystemMessage

chat = ChatDatabricks(
    endpoint="databricks-llama-3-1-70b-instruct",
    temperature=0.7,
    max_tokens=500
)

messages = [
    SystemMessage(content="You are a helpful data engineering assistant."),
    HumanMessage(content="Explain the medallion architecture in data lakehouses.")
]

response = chat(messages)
print(response.content)
```

### Example: Export Agent to Code

```python
# Exported AI Agent
from databricks.sdk import WorkspaceClient
from typing import Dict, List

class DataAnalysisAgent:
    def __init__(self):
        self.client = WorkspaceClient()
        self.tools = {
            "list_tables": self.list_tables,
            "execute_query": self.execute_query,
            "describe_table": self.describe_table
        }

    def list_tables(self, schema_name: str) -> List[str]:
        """List all tables in a schema"""
        return spark.sql(f"SHOW TABLES IN {schema_name}").collect()

    def execute_query(self, query: str, limit: int = 100) -> List[Dict]:
        """Execute SQL query and return results"""
        df = spark.sql(query).limit(limit)
        return df.toPandas().to_dict('records')

    def describe_table(self, table_name: str) -> str:
        """Get table schema"""
        return spark.sql(f"DESCRIBE TABLE {table_name}").collect()

    def run(self, user_query: str):
        """Process user query with LLM and tools"""
        # LLM decides which tools to call based on user query
        # Implementation uses Foundation Model APIs
        pass

# Use the agent
agent = DataAnalysisAgent()
agent.run("Show me top customers by purchase amount")
```

## Step 8: Production Prompt Templates

### Create Reusable Templates

**Template: Data Quality Check**
```
Analyze the following data quality metrics and provide recommendations:

Dataset: {dataset_name}
Total Records: {total_records}
Null Values: {null_count} ({null_percentage}%)
Duplicate Records: {duplicate_count}
Date Range: {start_date} to {end_date}
Completeness: {completeness_score}%

Provide:
1. Overall data quality assessment
2. Top 3 issues to address
3. Specific recommendations with SQL examples
```

**Template: SQL Query Explanation**
```
Explain the following SQL query in simple terms:

```sql
{sql_query}
```

Include:
1. What the query does
2. How each clause works
3. Expected output
4. Performance considerations
5. Potential improvements
```

**Template: Code Review**
```
Review the following {language} code for:
- Correctness
- Performance
- Best practices
- Security issues
- Code style

Code:
```{language}
{code_content}
```

Provide specific feedback with examples of improvements.
```

## Best Practices

### 1. Prompt Engineering Tips

**Be Specific**
```
❌ Poor: "Write code to process data"
✅ Good: "Write PySpark code to read a CSV file, remove duplicates, and save as Delta table"
```

**Provide Context**
```
✅ Good prompt includes:
- Your role/expertise level
- What you're trying to accomplish
- Constraints or requirements
- Desired output format
```

**Iterate and Refine**
```
First attempt → Review response → Refine prompt → Better response
```

### 2. Model Selection Guide

| Task Type | Recommended Model | Why |
|-----------|------------------|-----|
| Code Generation | llama-3.1-70b-instruct | Strong coding abilities |
| Data Analysis | dbrx-instruct | Optimized for data tasks |
| General Q&A | mixtral-8x7b-instruct | Fast, cost-effective |
| Complex Reasoning | llama-3.1-405b-instruct | Highest capability |
| SQL Generation | dbrx-instruct | SQL-focused training |

### 3. Cost Optimization

- Use smaller models for simple tasks
- Set appropriate max_tokens limits
- Cache common responses when possible
- Use comparison mode only when necessary
- Export to code for repeated use

### 4. Security Considerations

- Never include sensitive data in prompts
- Use parameter substitution for user data
- Review generated code before execution
- Implement rate limiting for production use
- Use appropriate access controls

## Common Use Cases

### Use Case 1: Documentation Generation

**Prompt:**
```
Generate comprehensive documentation for the following PySpark function:

def process_customer_data(df, start_date, end_date):
    return df.filter(
        (col("purchase_date") >= start_date) &
        (col("purchase_date") <= end_date)
    ).groupBy("customer_id").agg(
        sum("amount").alias("total_spent"),
        count("*").alias("transaction_count")
    )

Include:
- Function description
- Parameter details
- Return value description
- Usage example
- Notes on performance
```

### Use Case 2: Error Debugging

**Prompt:**
```
I'm getting this error when running my PySpark code:

AnalysisException: Column 'customer_id' does not exist

Here's my code:
df = spark.read.table("sales.transactions")
result = df.groupBy("customer_id").count()

Help me:
1. Understand what's wrong
2. How to check available columns
3. Fix the issue
4. Prevent similar issues in the future
```

### Use Case 3: Architecture Decisions

**Prompt:**
```
I need to design a real-time analytics pipeline with these requirements:
- Ingest 50K events per second from Kafka
- Transform and enrich data
- Store in Delta Lake
- Enable sub-second queries
- Budget: $5K/month
- Team: 2 data engineers

Compare these approaches:
1. Delta Live Tables with Streaming
2. Structured Streaming + Delta Lake
3. Apache Flink + Delta Lake

Provide recommendation with:
- Pros/cons of each
- Cost estimates
- Complexity assessment
- Implementation roadmap
```

## Troubleshooting

### Model Not Responding

**Check:**
- Model availability (some models may have quotas)
- Prompt length (may exceed token limits)
- Workspace permissions
- Network connectivity

### Poor Quality Responses

**Solutions:**
- Refine your prompt with more context
- Adjust temperature (lower for factual tasks)
- Try a different model
- Use few-shot examples
- Break complex tasks into steps

### Rate Limiting

**If you hit rate limits:**
- Add delays between requests
- Use batch processing
- Upgrade your workspace tier
- Cache responses for repeated queries

## Next Steps

Now that you understand AI Playground:

1. **[Build RAG Applications](../ml/rag-applications.md)**: Retrieval-augmented generation
2. **[Foundation Model APIs](../ml/foundation-models.md)**: Programmatic API access
3. **[Agent Framework](../ml/agent-framework.md)**: Build production agents
4. **[Prompt Engineering Guide](../ml/prompt-engineering.md)**: Advanced techniques

## Additional Resources

- [Databricks Foundation Model APIs Documentation](https://docs.databricks.com/machine-learning/foundation-models/index.html)
- [LLM Best Practices](https://docs.databricks.com/machine-learning/foundation-models/best-practices.html)
- [AI Playground Guide](https://docs.databricks.com/ai-playground/index.html)
- [Model Serving Documentation](https://docs.databricks.com/machine-learning/model-serving/index.html)

## Summary

In this tutorial, you learned how to:

✅ Access and navigate AI Playground
✅ Query LLMs with various prompts
✅ Adjust model parameters for different use cases
✅ Compare models side-by-side
✅ Apply prompt engineering techniques
✅ Prototype tool-calling AI agents
✅ Export prompts and agents to code
✅ Use templates for common tasks
✅ Apply best practices for production use

You're now ready to leverage LLMs for data engineering, analysis, and automation tasks!

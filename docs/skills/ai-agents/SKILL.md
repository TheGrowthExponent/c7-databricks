---
title: "AI & Agents Skills"
description: "Build intelligent applications with AI agents, vector search, and natural language interfaces"
category: "ai-agents"
tags:
  [
    "ai",
    "agents",
    "vector-search",
    "rag",
    "model-serving",
    "genie",
    "chatbots",
    "semantic-search",
    "llm",
  ]
priority: "high"
skills_count: 5
last_updated: 2026-02-27
version: "1.0.0"
status: "partial"
---

# AI & Agents Skills

This directory contains skills and patterns for building AI applications and agents on Databricks.

## 📚 Skills Overview

### High Priority Skills

#### 1. Databricks Agent Bricks

**Status**: ⚠️ Not yet documented
**Priority**: HIGH
**Description**: Build production-ready AI agents using Databricks Agent Bricks framework

**Key Topics**:

- Agent creation and deployment
- Tool integration and function calling
- Agent monitoring and debugging
- Production deployment patterns
- Multi-agent orchestration

**Use Cases**:

- Customer support chatbots
- Data analysis assistants
- Code generation agents
- Workflow automation agents

**Prerequisites**:

- Unity Catalog access
- Model Serving endpoint knowledge
- Vector Search familiarity

**Related Documentation**:

- [Model Serving](../../sdk/mlflow.md)
- [Unity Catalog API](../../api/unity-catalog.md)
- [Python SDK](../../sdk/python.md)

---

#### 2. Databricks Genie

**Status**: ⚠️ Not yet documented
**Priority**: HIGH
**Description**: Natural language interface for querying and analyzing data

**Key Topics**:

- Genie Spaces setup and configuration
- Natural language to SQL generation
- Data visualization from queries
- Fine-tuning Genie for your data
- Access control and security

**Use Cases**:

- Business user data exploration
- Ad-hoc analytics without SQL knowledge
- Dashboard creation from natural language
- Self-service reporting

**Prerequisites**:

- Unity Catalog enabled
- SQL Warehouses configured
- Table access permissions

**Related Documentation**:

- [SQL Examples](../../examples/sql.md)
- [Unity Catalog API](../../api/unity-catalog.md)
- [Security Best Practices](../../best-practices/security.md)

---

#### 3. Databricks Vector Search

**Status**: ⚠️ Not yet documented
**Priority**: HIGH
**Description**: Build semantic search and retrieval-augmented generation (RAG) applications

**Key Topics**:

- Vector index creation and management
- Embedding generation strategies
- Similarity search patterns
- RAG implementation
- Index optimization and scaling

**Use Cases**:

- Semantic document search
- RAG chatbots
- Recommendation systems
- Duplicate detection
- Content similarity matching

**Prerequisites**:

- Delta Lake tables
- Embedding model access
- Unity Catalog enabled

**Related Documentation**:

- [Delta Lake Guide](../../sdk/delta-lake.md)
- [ML Workflows](../../examples/ml-workflows.md)
- [Performance Optimization](../../best-practices/performance.md)

---

### Medium Priority Skills

#### 4. Databricks Model Serving

**Status**: ⚠️ Partially documented
**Priority**: MEDIUM
**Description**: Deploy and serve machine learning models at scale

**Key Topics**:

- Model endpoint deployment
- Real-time inference
- Batch inference patterns
- Model versioning and rollback
- Autoscaling configuration
- Monitoring and alerting

**Use Cases**:

- Production ML model serving
- A/B testing models
- Online feature computation
- Model ensemble serving

**Prerequisites**:

- MLflow registered models
- Model training knowledge
- API integration experience

**Related Documentation**:

- [MLflow Guide](../../sdk/mlflow.md) ✅
- [ML Workflows](../../examples/ml-workflows.md) ✅
- [Python SDK](../../sdk/python.md) ✅

**Enhancement Needed**:

- Add dedicated Model Serving endpoint examples
- Document autoscaling strategies
- Include monitoring patterns

---

### Low Priority Skills

#### 5. Databricks Unstructured PDF Generation

**Status**: ❌ Not documented
**Priority**: LOW
**Description**: Generate and process unstructured documents and PDFs

**Key Topics**:

- PDF text extraction
- Document parsing
- OCR integration
- Structured data extraction from PDFs
- Batch document processing

**Use Cases**:

- Invoice processing
- Contract analysis
- Document classification
- Form data extraction

**Prerequisites**:

- File storage access (DBFS/S3)
- Python environment setup

**Related Documentation**:

- [DBFS API](../../api/dbfs.md)
- [ETL Patterns](../../examples/etl-patterns.md)

---

## 🎯 Quick Start Examples

### Example 1: Basic Vector Search Setup

```python
from databricks.vector_search.client import VectorSearchClient

# Initialize client
vsc = VectorSearchClient()

# Create vector search endpoint
vsc.create_endpoint(
    name="my-vector-search-endpoint",
    endpoint_type="STANDARD"
)

# Create vector index
vsc.create_delta_sync_index(
    endpoint_name="my-vector-search-endpoint",
    source_table_name="main.default.documents",
    index_name="main.default.documents_index",
    pipeline_type="TRIGGERED",
    primary_key="doc_id",
    embedding_source_column="text",
    embedding_model_endpoint_name="databricks-bge-large-en"
)

# Query the index
results = vsc.get_index(
    endpoint_name="my-vector-search-endpoint",
    index_name="main.default.documents_index"
).similarity_search(
    query_text="machine learning best practices",
    columns=["doc_id", "text", "metadata"],
    num_results=5
)

for result in results:
    print(f"Score: {result['score']}")
    print(f"Text: {result['text']}")
    print("---")
```

### Example 2: RAG Pattern with Vector Search

```python
from databricks.vector_search.client import VectorSearchClient
import mlflow

# Setup
vsc = VectorSearchClient()
llm = mlflow.pyfunc.load_model("models:/llama-2-70b/1")

def rag_query(question: str, index_name: str) -> str:
    """
    Retrieval-Augmented Generation pattern
    """
    # Retrieve relevant context
    search_results = vsc.get_index(
        endpoint_name="my-vector-search-endpoint",
        index_name=index_name
    ).similarity_search(
        query_text=question,
        columns=["text"],
        num_results=3
    )

    # Build context from results
    context = "\n\n".join([r['text'] for r in search_results])

    # Build prompt
    prompt = f"""Answer the question based on the context below.

Context:
{context}

Question: {question}

Answer:"""

    # Generate response
    response = llm.predict(prompt)

    return response

# Use RAG
answer = rag_query(
    question="How do I optimize Delta Lake performance?",
    index_name="main.default.docs_index"
)
print(answer)
```

### Example 3: Agent with Function Calling

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import FunctionInfo
import json

# Initialize client
w = WorkspaceClient()

# Define agent tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_table_schema",
            "description": "Get the schema of a Unity Catalog table",
            "parameters": {
                "type": "object",
                "properties": {
                    "catalog": {"type": "string"},
                    "schema": {"type": "string"},
                    "table": {"type": "string"}
                },
                "required": ["catalog", "schema", "table"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": "Execute a SQL query and return results",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "warehouse_id": {"type": "string"}
                },
                "required": ["query", "warehouse_id"]
            }
        }
    }
]

# Agent implementation
class DataAnalysisAgent:
    def __init__(self, workspace_client):
        self.client = workspace_client
        self.conversation_history = []

    def get_table_schema(self, catalog: str, schema: str, table: str) -> dict:
        """Tool: Get table schema"""
        table_info = self.client.tables.get(
            full_name=f"{catalog}.{schema}.{table}"
        )
        return {
            "columns": [
                {"name": col.name, "type": col.type_name}
                for col in table_info.columns
            ]
        }

    def execute_sql(self, query: str, warehouse_id: str) -> list:
        """Tool: Execute SQL query"""
        statement = self.client.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout="30s"
        )

        if statement.status.state == "SUCCEEDED":
            return statement.result.data_array
        else:
            raise Exception(f"Query failed: {statement.status.error}")

    def process_query(self, user_query: str, model_endpoint: str):
        """Process user query with agent"""
        # Add user query to history
        self.conversation_history.append({
            "role": "user",
            "content": user_query
        })

        # Call LLM with tools
        response = self.call_llm_with_tools(
            messages=self.conversation_history,
            tools=tools,
            model_endpoint=model_endpoint
        )

        # Handle tool calls
        while response.get("tool_calls"):
            for tool_call in response["tool_calls"]:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])

                # Execute tool
                if function_name == "get_table_schema":
                    result = self.get_table_schema(**function_args)
                elif function_name == "execute_sql":
                    result = self.execute_sql(**function_args)

                # Add tool result to conversation
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result)
                })

            # Get next response
            response = self.call_llm_with_tools(
                messages=self.conversation_history,
                tools=tools,
                model_endpoint=model_endpoint
            )

        return response["content"]

# Usage
agent = DataAnalysisAgent(w)
answer = agent.process_query(
    user_query="What is the schema of the sales table in main.analytics?",
    model_endpoint="databricks-meta-llama-3-70b-instruct"
)
print(answer)
```

---

## 🔧 Common Patterns

### Pattern 1: Semantic Search with Filtering

```python
# Search with metadata filtering
results = vsc.get_index(
    endpoint_name="my-vector-search-endpoint",
    index_name="main.default.documents_index"
).similarity_search(
    query_text="databricks optimization",
    columns=["doc_id", "text", "category", "date"],
    filters={"category": "performance", "date": {"$gte": "2026-01-01"}},
    num_results=10
)
```

### Pattern 2: Hybrid Search (Vector + Keyword)

```python
# Combine vector similarity with keyword matching
def hybrid_search(query: str, keywords: list[str], index_name: str):
    # Vector search
    vector_results = vsc.get_index(
        endpoint_name="my-vector-search-endpoint",
        index_name=index_name
    ).similarity_search(
        query_text=query,
        num_results=20
    )

    # Filter by keywords
    filtered_results = [
        r for r in vector_results
        if any(kw.lower() in r['text'].lower() for kw in keywords)
    ]

    return filtered_results[:10]
```

### Pattern 3: Agent with Memory

```python
class AgentWithMemory:
    def __init__(self, model_endpoint: str):
        self.model_endpoint = model_endpoint
        self.memory = []
        self.max_history = 10

    def add_to_memory(self, role: str, content: str):
        self.memory.append({"role": role, "content": content})
        # Keep only recent history
        if len(self.memory) > self.max_history * 2:
            self.memory = self.memory[-self.max_history * 2:]

    def query(self, user_input: str) -> str:
        self.add_to_memory("user", user_input)

        # Call LLM with conversation history
        response = call_model(
            endpoint=self.model_endpoint,
            messages=self.memory
        )

        self.add_to_memory("assistant", response)
        return response
```

---

## 📊 Best Practices

### Vector Search

1. **Index Design**
   - Choose appropriate embedding dimensions (768, 1024, 1536)
   - Consider index type (delta_sync vs direct_access)
   - Plan for incremental updates

2. **Performance Optimization**
   - Batch embedding generation
   - Use filtered search to reduce latency
   - Monitor index freshness

3. **Quality Improvement**
   - Use high-quality embedding models
   - Implement hybrid search strategies
   - Add metadata for filtering

### Agent Development

1. **Tool Design**
   - Keep functions focused and single-purpose
   - Provide clear descriptions for the LLM
   - Validate tool inputs rigorously

2. **Conversation Management**
   - Implement conversation history limits
   - Store context efficiently
   - Handle long conversations gracefully

3. **Error Handling**
   - Retry failed tool calls
   - Provide fallback responses
   - Log all agent interactions

### RAG Applications

1. **Context Selection**
   - Retrieve 3-5 relevant chunks
   - Consider context window limits
   - Rank by relevance score

2. **Prompt Engineering**
   - Be explicit about using provided context
   - Handle cases with no relevant context
   - Request citations from context

3. **Evaluation**
   - Track response quality metrics
   - Monitor retrieval relevance
   - A/B test different configurations

---

## 🚀 Getting Started Checklist

### For Vector Search

- [ ] Enable Unity Catalog
- [ ] Create source Delta table with documents
- [ ] Deploy embedding model endpoint
- [ ] Create Vector Search endpoint
- [ ] Create and sync vector index
- [ ] Test similarity search queries
- [ ] Implement RAG pattern

### For AI Agents

- [ ] Define agent objectives and scope
- [ ] Design tool functions
- [ ] Select and deploy LLM endpoint
- [ ] Implement function calling logic
- [ ] Add conversation management
- [ ] Test agent interactions
- [ ] Deploy to production

### For Genie Spaces

- [ ] Set up Unity Catalog tables
- [ ] Configure SQL Warehouse
- [ ] Create Genie Space
- [ ] Add sample instructions
- [ ] Test natural language queries
- [ ] Grant user access
- [ ] Monitor usage and feedback

---

## 📖 Additional Resources

### Official Documentation

- [Databricks AI Functions](https://docs.databricks.com/en/large-language-models/ai-functions.html)
- [Vector Search Guide](https://docs.databricks.com/en/generative-ai/vector-search.html)
- [Model Serving](https://docs.databricks.com/en/machine-learning/model-serving/index.html)

### Tutorials

- [Build a RAG Application](../../getting-started/ai-playground-tutorial.md)
- [ML Workflows](../../examples/ml-workflows.md)

### API References

- [Python SDK](../../sdk/python.md)
- [MLflow API](../../sdk/mlflow.md)
- [Unity Catalog API](../../api/unity-catalog.md)

---

## 🏷️ Tags

`ai` `agents` `vector-search` `rag` `genie` `model-serving` `embeddings` `semantic-search` `llm` `chatbots`

---

**Last Updated**: 2026-01-15
**Status**: Initial documentation - High priority skills need detailed guides
**Maintainer**: Context7 Documentation Team

---
title: "Databricks Skills Reference"
description: "A comprehensive guide to skills and patterns for building on Databricks, organized by functional area and optimized for AI-assisted development with Context7"
category: "overview"
tags:
  [
    "skills",
    "patterns",
    "best-practices",
    "ai",
    "ml",
    "data-engineering",
    "analytics",
    "devops",
    "deployment",
    "automation",
    "dashboards",
    "workflows",
    "agents",
    "vector-search",
    "mlflow",
  ]
skills_count: 24
last_updated: 2026-02-27
version: "1.0.0"
status: "active"
---

# Databricks Skills Reference

A comprehensive guide to skills and patterns for building on Databricks, organized by functional area and optimized for AI-assisted development with Context7.

## 📖 Overview

This skills directory contains practical guides, code examples, and best practices for all major Databricks capabilities. Each skill includes:

- ✅ **Current Status** - Documentation coverage level
- 🎯 **Priority Level** - Implementation urgency (HIGH/MEDIUM/LOW)
- 📚 **Key Topics** - Main concepts and features
- 💡 **Use Cases** - Real-world applications
- 🔧 **Quick Start Examples** - Copy-paste ready code
- 📊 **Best Practices** - Production-ready patterns
- 🚀 **Getting Started Checklist** - Step-by-step implementation guide

---

## 🗂️ Skills by Category

### 🤖 AI & Agents (5 Skills)

**Directory**: [ai-agents/](ai-agents/)

Build intelligent applications with AI agents, vector search, and natural language interfaces.

| Skill                       | Status            | Priority | Description                          |
| --------------------------- | ----------------- | -------- | ------------------------------------ |
| **Databricks Agent Bricks** | ⚠️ Not documented | **HIGH** | Production-ready AI agents framework |
| **Databricks Genie**        | ⚠️ Not documented | **HIGH** | Natural language data interface      |
| **Vector Search**           | ⚠️ Not documented | **HIGH** | Semantic search and RAG applications |
| **Model Serving**           | ⚠️ Partial        | MEDIUM   | ML model deployment and serving      |
| **PDF Generation**          | ❌ Not documented | LOW      | Unstructured document processing     |

**Key Use Cases**: Chatbots, RAG applications, semantic search, agent orchestration, self-service analytics

📘 **[View AI & Agents Skills →](ai-agents/SKILL.md)**

---

### 📊 MLflow (8 Skills)

**Directory**: [mlflow/](mlflow/)

Experiment tracking, model management, and observability for machine learning workflows.

| Skill                     | Status            | Priority | Description                      |
| ------------------------- | ----------------- | -------- | -------------------------------- |
| **MLflow Onboarding**     | ✅ Covered        | -        | Complete MLflow setup and basics |
| **Querying Metrics**      | ✅ Covered        | -        | Experiment search and analysis   |
| **MLflow Tracing**        | ⚠️ Partial        | MEDIUM   | LLM and agent observability      |
| **Agent Evaluation**      | ❌ Not documented | MEDIUM   | Systematic agent testing         |
| **Chat Session Analysis** | ❌ Not documented | LOW      | Conversation pattern analysis    |
| **Trace Analysis**        | ⚠️ Partial        | LOW      | Deep trace debugging             |
| **Retrieving Traces**     | ⚠️ Partial        | LOW      | Programmatic trace access        |
| **MLflow Docs Search**    | N/A               | -        | Documentation index              |

**Key Use Cases**: Experiment tracking, model registry, hyperparameter tuning, LLM tracing, agent debugging

📘 **[View MLflow Skills →](mlflow/SKILL.md)**

---

### 📈 Analytics & Dashboards (2 Skills)

**Directory**: [analytics/](analytics/)

Business intelligence, dashboards, and data governance with system tables.

| Skill                           | Status            | Priority | Description                       |
| ------------------------------- | ----------------- | -------- | --------------------------------- |
| **AI/BI Dashboards**            | ❌ Not documented | **HIGH** | Intelligent dashboards with Genie |
| **Unity Catalog System Tables** | ⚠️ Partial        | MEDIUM   | Usage monitoring and governance   |

**Key Use Cases**: Executive dashboards, cost analysis, audit compliance, performance monitoring, data lineage

📘 **[View Analytics Skills →](analytics/SKILL.md)**

---

### 🔧 Data Engineering (3 Skills)

**Directory**: [data-engineering/](data-engineering/)

ETL pipelines, data processing, and workflow orchestration.

| Skill                         | Status            | Priority | Description                          |
| ----------------------------- | ----------------- | -------- | ------------------------------------ |
| **Databricks Jobs**           | ✅ Covered        | -        | Workflow orchestration (1,382 lines) |
| **Delta Live Tables**         | ⚠️ Partial        | MEDIUM   | Declarative data pipelines           |
| **Synthetic Data Generation** | ❌ Not documented | LOW      | Test data creation                   |

**Key Use Cases**: ETL pipelines, medallion architecture, data quality, incremental processing, CDC

📘 **[View Data Engineering Skills →](data-engineering/SKILL.md)**

---

### 🚀 Development & Deployment (6 Skills)

**Directory**: [development/](development/)

Application development, deployment automation, and DevOps practices.

| Skill                        | Status            | Priority | Description                          |
| ---------------------------- | ----------------- | -------- | ------------------------------------ |
| **Python SDK**               | ✅ Covered        | -        | Complete SDK reference (1,172 lines) |
| **Configuration**            | ✅ Covered        | -        | Multi-environment setup              |
| **Asset Bundles (DABs)**     | ❌ Not documented | **HIGH** | Modern deployment framework          |
| **Databricks Apps (Python)** | ❌ Not documented | **HIGH** | Full-stack applications              |
| **Apps (APX Framework)**     | ❌ Not documented | **HIGH** | Enterprise app framework             |
| **Lakebase Provisioned**     | ❌ Not documented | LOW      | Provisioned infrastructure           |

**Key Use Cases**: CI/CD automation, infrastructure as code, application hosting, multi-environment deployment

📘 **[View Development Skills →](development/SKILL.md)**

---

## 📊 Skills Coverage Summary

### By Status

| Status                   | Count | Percentage | Skills                                                                          |
| ------------------------ | ----- | ---------- | ------------------------------------------------------------------------------- |
| ✅ **Well Covered**      | 5     | 26%        | MLflow Onboarding, Querying Metrics, Jobs, Python SDK, Config                   |
| ⚠️ **Partially Covered** | 5     | 26%        | Model Serving, MLflow Tracing, System Tables, DLT, Trace Analysis               |
| ❌ **Not Documented**    | 11    | 48%        | Agent Bricks, Genie, Vector Search, AI/BI Dashboards, Asset Bundles, Apps, etc. |

### By Priority

| Priority     | Count | High-Priority Topics                                                                           |
| ------------ | ----- | ---------------------------------------------------------------------------------------------- |
| **HIGH**     | 8     | Agent Bricks, Genie, Vector Search, AI/BI Dashboards, Asset Bundles, Apps (Python), Apps (APX) |
| **MEDIUM**   | 4     | Model Serving, MLflow Tracing, System Tables, Delta Live Tables, Agent Evaluation              |
| **LOW**      | 5     | PDF Generation, Chat Analysis, Trace Analysis, Synthetic Data, Lakebase                        |
| **Complete** | 5     | MLflow Onboarding, Querying Metrics, Jobs, Python SDK, Config                                  |

---

## 🎯 Quick Navigation

### By Use Case

**Building AI Applications?**

- [Agent Bricks](ai-agents/SKILL.md#databricks-agent-bricks) - AI agent framework
- [Vector Search](ai-agents/SKILL.md#databricks-vector-search) - Semantic search & RAG
- [Model Serving](ai-agents/SKILL.md#databricks-model-serving) - Deploy ML models
- [MLflow Tracing](mlflow/SKILL.md#instrumenting-with-mlflow-tracing) - LLM observability

**Building Data Pipelines?**

- [Databricks Jobs](data-engineering/SKILL.md#databricks-jobs) - Workflow orchestration
- [Delta Live Tables](data-engineering/SKILL.md#databricks-spark-declarative-pipelines) - Declarative pipelines
- [ETL Patterns](../examples/etl-patterns.md) - Common ETL patterns

**Building Analytics?**

- [AI/BI Dashboards](analytics/SKILL.md#databricks-aibi-dashboards) - Intelligent dashboards
- [Genie Spaces](ai-agents/SKILL.md#databricks-genie) - Natural language queries
- [System Tables](analytics/SKILL.md#unity-catalog-system-tables) - Usage monitoring

**Deploying to Production?**

- [Asset Bundles](development/SKILL.md#databricks-asset-bundles) - Modern deployments
- [Python SDK](development/SKILL.md#databricks-python-sdk) - Automation
- [Databricks Apps](development/SKILL.md#databricks-apps-python) - Application hosting

**Training ML Models?**

- [MLflow Guide](../sdk/mlflow.md) - Experiment tracking
- [ML Workflows](../examples/ml-workflows.md) - End-to-end pipelines
- [Model Registry](mlflow/SKILL.md#model-registry-and-deployment) - Model management

---

## 🚀 Getting Started

### For AI/ML Developers

1. Start with [MLflow Onboarding](mlflow/SKILL.md#mlflow-onboarding)
2. Explore [Vector Search](ai-agents/SKILL.md#databricks-vector-search) for RAG
3. Learn [Agent Bricks](ai-agents/SKILL.md#databricks-agent-bricks) for production agents
4. Review [Model Serving](ai-agents/SKILL.md#databricks-model-serving) for deployment

### For Data Engineers

1. Master [Databricks Jobs](data-engineering/SKILL.md#databricks-jobs) API
2. Learn [Delta Live Tables](data-engineering/SKILL.md#databricks-spark-declarative-pipelines)
3. Study [ETL Patterns](../examples/etl-patterns.md)
4. Implement [Data Quality](data-engineering/SKILL.md#pattern-1-medallion-architecture) checks

### For Analytics/BI Users

1. Start with [Genie Spaces](ai-agents/SKILL.md#databricks-genie)
2. Build [AI/BI Dashboards](analytics/SKILL.md#databricks-aibi-dashboards)
3. Monitor with [System Tables](analytics/SKILL.md#unity-catalog-system-tables)
4. Track [Costs and Usage](analytics/SKILL.md#example-3-cost-analysis-with-system-tables)

### For DevOps/Platform Engineers

1. Configure [Multi-environment Setup](development/SKILL.md#databricks-configuration)
2. Implement [Asset Bundles](development/SKILL.md#databricks-asset-bundles)
3. Automate with [Python SDK](development/SKILL.md#databricks-python-sdk)
4. Build [CI/CD Pipelines](development/SKILL.md#example-5-cicd-pipeline-with-asset-bundles)

---

## 📚 Related Documentation

### Core Documentation

- [Getting Started Guide](../getting-started/) - Platform introduction and setup
- [API Reference](../api/) - Complete REST API documentation
- [SDK Guides](../sdk/) - Python SDK, Delta Lake, MLflow
- [Examples](../examples/) - Working code examples
- [Best Practices](../best-practices/) - Performance and security

### Skills Documentation Standards

- [SKILL-FORMAT-GUIDE.md](SKILL-FORMAT-GUIDE.md) - Required format for all SKILL.md files
- [SKILL-TEMPLATE.md](SKILL-TEMPLATE.md) - Template for creating new skills documentation

### Quick Links

- [30-Minute Quickstart](../getting-started/quickstart.md)
- [Authentication Guide](../getting-started/authentication.md)
- [Jobs API (1,382 lines)](../api/jobs.md)
- [Python SDK (1,172 lines)](../sdk/python.md)
- [ETL Patterns](../examples/etl-patterns.md)
- [ML Workflows](../examples/ml-workflows.md)

---

## 💡 How to Use This Guide

### For Developers

Each skill guide includes:

1. **Overview** - What the skill covers
2. **Quick Start Examples** - Ready-to-use code
3. **Common Patterns** - Production-tested approaches
4. **Best Practices** - Expert recommendations
5. **Checklists** - Step-by-step implementation

### For AI Assistants (Context7)

This documentation is optimized for AI-assisted development:

- ✅ Consistent structure across all skills
- ✅ Complete, working code examples
- ✅ Clear section hierarchies
- ✅ Comprehensive cross-references
- ✅ Production-ready patterns

### Reading the Status Indicators

- ✅ **Covered** - Comprehensive documentation available
- ⚠️ **Partial** - Basic coverage, needs expansion
- ❌ **Not Documented** - High-priority gap
- N/A - Not applicable or reference only

---

## 📝 Documentation Standards

All skills documentation follows these standards:

### Structure

- Clear hierarchy with numbered sections
- Consistent formatting across all files
- Practical examples for every concept
- Cross-references to related topics

### Code Examples

- Production-ready implementations
- Complete error handling
- Security best practices
- Performance considerations

### Best Practices

- Industry-standard patterns
- Databricks-specific optimizations
- Cost management strategies
- Testing and validation approaches

---

## 🤝 Contributing

To add or enhance skills documentation:

1. **Follow the SKILL.md format** - See [SKILL-FORMAT-GUIDE.md](SKILL-FORMAT-GUIDE.md) for required YAML frontmatter
2. **Use the template** - Start with [SKILL-TEMPLATE.md](SKILL-TEMPLATE.md) for new skills
3. **Get date from CLI** - Always use `date +%Y-%m-%d` for last_updated field (never hardcode)
4. Follow the established structure and format
5. Include complete, working code examples
6. Add practical use cases and scenarios
7. Cross-reference related documentation
8. Update this index file

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for detailed guidelines.

**Required Files:**

- [SKILL-FORMAT-GUIDE.md](SKILL-FORMAT-GUIDE.md) - Complete format requirements and validation
- [SKILL-TEMPLATE.md](SKILL-TEMPLATE.md) - Starting template for new SKILL.md files

---

## 📈 Roadmap

### Phase 5: High-Priority Skills (Planned)

**AI & Agents**

- [ ] Agent Bricks comprehensive guide
- [ ] Genie Spaces setup and patterns
- [ ] Vector Search implementation guide
- [ ] RAG application patterns

**Analytics**

- [ ] AI/BI Dashboards complete guide
- [ ] System Tables analysis patterns
- [ ] Cost monitoring dashboards
- [ ] Audit and compliance queries

**Development**

- [ ] Asset Bundles deployment guide
- [ ] Databricks Apps tutorials
- [ ] CI/CD pipeline examples
- [ ] Multi-environment patterns

**Data Engineering**

- [ ] Delta Live Tables deep dive
- [ ] Data quality frameworks
- [ ] CDC processing patterns
- [ ] Performance optimization

---

## 📞 Support

For questions or issues:

1. Check the relevant skill guide
2. Review [Getting Started](../getting-started/)
3. Consult [API Documentation](../api/)
4. See [Examples](../examples/)

---

## 📊 Project Statistics

| Metric                        | Count    |
| ----------------------------- | -------- |
| **Total Skills**              | 24       |
| **Well Documented**           | 5 (21%)  |
| **Partially Covered**         | 5 (21%)  |
| **Documentation Needed**      | 11 (46%) |
| **Reference Only**            | 3 (12%)  |
| **Total Documentation Files** | 6        |
| **Skills Categories**         | 5        |

---

## 🏷️ Tags

`skills` `patterns` `best-practices` `ai` `ml` `data-engineering` `analytics` `devops` `deployment` `automation` `dashboards` `workflows` `agents` `vector-search` `mlflow`

---

**Last Updated**: 2026-01-15
**Version**: 1.0.0
**Status**: Initial skills documentation framework complete
**Maintainer**: Context7 Documentation Team

---

**Note**: This skills documentation is part of the [c7-databricks](../../README.md) project - a comprehensive Databricks documentation repository optimized for Context7 AI-assisted development.

For official Databricks documentation, visit [docs.databricks.com](https://docs.databricks.com/)

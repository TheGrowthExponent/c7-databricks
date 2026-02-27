# Databricks Getting Started Documentation

Welcome to the Databricks Getting Started guide! This directory contains comprehensive tutorials to help you quickly become productive with the Databricks platform.

## 📚 Tutorial Overview

### Core Fundamentals
Start here to understand Databricks basics and set up your environment:

- **[Introduction to Databricks](introduction.md)** - Learn about the Databricks platform, architecture, and core capabilities
- **[Setup Guide](setup.md)** - Configure your Databricks workspace and environment
- **[Authentication Guide](authentication.md)** - Set up secure access with tokens and authentication methods
- **[Quick Start Guide](quickstart.md)** - Create your first cluster and run code in 30 minutes
- **[Databricks Connect](databricks-connect.md)** - Connect local IDEs to Databricks clusters

### Hands-On Tutorials
Follow these step-by-step tutorials aligned with official Databricks getting started content:

1. **[Query and Visualize Data](query-visualize-data.md)**
   - Query Unity Catalog data with SQL, Python, Scala, and R
   - Create interactive visualizations
   - Work with sample datasets
   - Build dashboards

2. **[Import and Visualize CSV Data](csv-import-tutorial.md)**
   - Upload CSV files to Unity Catalog volumes
   - Read and transform data
   - Modify column names and clean data
   - Save as Delta tables

3. **[Create Tables in Unity Catalog](create-table-tutorial.md)**
   - Understand Unity Catalog structure
   - Create managed and external tables
   - Set up partitioned tables
   - Grant permissions and manage access

4. **[Build ETL Pipelines](etl-pipeline-tutorial.md)**
   - Create Lakeflow Spark Declarative Pipelines
   - Build traditional Apache Spark ETL workflows
   - Implement medallion architecture (Bronze/Silver/Gold)
   - Use Auto Loader for incremental ingestion
   - Schedule and orchestrate pipelines

5. **[Train and Deploy ML Models](ml-model-tutorial.md)**
   - Load and explore datasets
   - Train classification models with scikit-learn
   - Track experiments with MLflow
   - Perform hyperparameter tuning with Hyperopt
   - Register and deploy models
   - Make predictions with production models

6. **[Query LLMs and Build AI Agents](ai-playground-tutorial.md)**
   - Use AI Playground to query LLMs
   - Compare models side-by-side
   - Prototype tool-calling AI agents
   - Export to code
   - Apply prompt engineering techniques

## 🎯 Learning Paths

### For Data Engineers
```
1. Introduction → Setup → Authentication
2. Query and Visualize Data
3. Import CSV Data
4. Create Tables in Unity Catalog
5. Build ETL Pipelines
```

### For Data Scientists
```
1. Introduction → Setup → Quick Start
2. Query and Visualize Data
3. Train and Deploy ML Models
4. Query LLMs and Build AI Agents
```

### For Data Analysts
```
1. Introduction → Authentication
2. Query and Visualize Data
3. Import CSV Data
4. Create Tables in Unity Catalog
```

### For AI/ML Engineers
```
1. Quick Start → Authentication
2. Train and Deploy ML Models
3. Query LLMs and Build AI Agents
4. Build ETL Pipelines (for data prep)
```

## 📖 Tutorial Features

Each tutorial includes:
- ✅ **Clear Prerequisites** - Know what you need before starting
- ✅ **Step-by-Step Instructions** - Easy to follow guidance
- ✅ **Code Examples** - Working code in Python, SQL, Scala, and R
- ✅ **Visualizations** - Learn to create charts and dashboards
- ✅ **Best Practices** - Production-ready patterns
- ✅ **Troubleshooting** - Common issues and solutions
- ✅ **Next Steps** - Suggested learning path

## 🚀 Quick Navigation

### By Technology
- **SQL**: [Query Data](query-visualize-data.md), [Create Tables](create-table-tutorial.md)
- **Python**: All tutorials include Python examples
- **Scala**: [Query Data](query-visualize-data.md), [CSV Import](csv-import-tutorial.md)
- **R**: [Query Data](query-visualize-data.md), [CSV Import](csv-import-tutorial.md)
- **MLflow**: [ML Model Tutorial](ml-model-tutorial.md)
- **Delta Lake**: [ETL Pipelines](etl-pipeline-tutorial.md), [Create Tables](create-table-tutorial.md)
- **Unity Catalog**: [Query Data](query-visualize-data.md), [Create Tables](create-table-tutorial.md)

### By Use Case
- **Data Ingestion**: [CSV Import](csv-import-tutorial.md), [ETL Pipelines](etl-pipeline-tutorial.md)
- **Data Transformation**: [ETL Pipelines](etl-pipeline-tutorial.md)
- **Data Analysis**: [Query and Visualize](query-visualize-data.md)
- **Machine Learning**: [ML Model Tutorial](ml-model-tutorial.md)
- **AI Agents**: [AI Playground](ai-playground-tutorial.md)
- **Data Governance**: [Create Tables](create-table-tutorial.md)

## 💡 Tips for Success

### First-Time Users
1. Start with [Introduction to Databricks](introduction.md) to understand core concepts
2. Complete [Setup Guide](setup.md) and [Authentication Guide](authentication.md)
3. Run through [Quick Start Guide](quickstart.md) to get hands-on experience
4. Pick a tutorial that matches your role and goals

### Experienced Users
- Use tutorials as reference documentation
- Focus on specific features you need (e.g., Unity Catalog, MLflow)
- Explore advanced topics in each tutorial's "Best Practices" section
- Export code examples to customize for your use cases

## 🔗 Related Documentation

### Core Documentation
- [API Reference](../api/overview.md) - REST API and SDK documentation
- [Python SDK Guide](../sdk/python.md) - Comprehensive Python SDK reference
- [SQL Reference](../sql/overview.md) - SQL syntax and functions
- [CLI Guide](../cli/overview.md) - Command-line interface tools

### Advanced Topics
- [Machine Learning](../ml/mlflow.md) - MLflow, AutoML, Feature Store
- [Best Practices](../best-practices/general.md) - Production patterns
- [Examples](../examples/python.md) - Additional code examples

## 🎓 External Resources

### Official Databricks Resources
- [Databricks Documentation](https://docs.databricks.com/)
- [Databricks Academy](https://academy.databricks.com/) - Free training courses
- [Databricks Blog](https://databricks.com/blog) - Latest updates and tutorials
- [Community Forums](https://community.databricks.com/) - Get help from the community

### Learning Platforms
- [Databricks Certified Associate Developer](https://academy.databricks.com/certification)
- [Databricks Certified Professional Data Engineer](https://academy.databricks.com/certification)
- [YouTube: Databricks Channel](https://www.youtube.com/c/Databricks)

## 🆘 Getting Help

### If You're Stuck
1. Check the **Troubleshooting** section in each tutorial
2. Search [Databricks Community Forums](https://community.databricks.com/)
3. Review [Stack Overflow - Databricks Tag](https://stackoverflow.com/questions/tagged/databricks)
4. Contact your workspace administrator
5. Email onboarding-help@databricks.com (for setup issues)

### Report Issues
Found an error in the documentation? Please report it:
- File an issue in the repository
- Suggest improvements
- Contribute corrections via pull requests

## 📋 Prerequisites Summary

### Workspace Access
- Active Databricks workspace (free trial available at [databricks.com/try-databricks](https://databricks.com/try-databricks))
- User account with appropriate permissions

### Technical Requirements
- Web browser (Chrome, Firefox, Safari, or Edge recommended)
- Internet connection
- Basic knowledge of SQL, Python, or other supported languages (depending on tutorial)

### Optional but Recommended
- Understanding of cloud platforms (AWS, Azure, or GCP)
- Experience with data engineering or data science concepts
- Familiarity with distributed computing (Apache Spark)

## 🔄 Keeping Up to Date

These tutorials are maintained to reflect the latest Databricks features and best practices. Notable updates:

- **Latest**: Added AI Playground tutorial for LLM querying and agent prototyping
- **New**: Lakeflow Spark Declarative Pipelines in ETL tutorial
- **Updated**: Unity Catalog permissions and table management
- **Enhanced**: ML model deployment with MLflow Model Registry

Check individual tutorial files for specific version notes and last updated dates.

## 📝 Tutorial Completion Checklist

Track your learning progress:

- [ ] Read Introduction to Databricks
- [ ] Complete Setup and Authentication
- [ ] Run Quick Start Guide
- [ ] Query and visualize Unity Catalog data
- [ ] Import and transform CSV data
- [ ] Create tables in Unity Catalog
- [ ] Build an ETL pipeline
- [ ] Train and deploy an ML model
- [ ] Experiment with AI Playground

## 🎉 What's Next?

After completing these tutorials, you'll be ready to:

1. **Build Production Pipelines** - Create robust, scalable data workflows
2. **Deploy ML Models** - Put machine learning models into production
3. **Implement Data Governance** - Use Unity Catalog for enterprise-grade governance
4. **Optimize Performance** - Apply advanced optimization techniques
5. **Create AI Applications** - Build LLM-powered data applications

Continue your learning journey:
- Explore [Advanced Topics](../best-practices/general.md)
- Join the [Databricks Community](https://community.databricks.com/)
- Get [Certified](https://academy.databricks.com/certification)

---

**Happy Learning! 🚀**

For questions or feedback, please reach out through the community forums or your workspace administrator.

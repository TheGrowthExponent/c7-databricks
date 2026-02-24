#!/usr/bin/env python3
"""
AI Agent Integration for Databricks Documentation Validation

This script integrates with AI APIs (Claude, OpenAI, etc.) to automatically
validate documentation against official Databricks sources.

Usage:
    python agent_validator.py --provider anthropic --scope full
    python agent_validator.py --provider openai --files "docs/api/*.md"
    python agent_validator.py --provider anthropic --interactive
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AIAgentValidator:
    """Validates documentation using AI agent APIs."""

    def __init__(
        self,
        provider: str = "anthropic",
        config_path: str = "validation-config.json",
        api_key: Optional[str] = None,
    ):
        """Initialize AI agent validator.

        Args:
            provider: AI provider (anthropic, openai, azure)
            config_path: Path to validation configuration
            api_key: API key for the provider (or set via environment)
        """
        self.provider = provider.lower()
        self.config_path = Path(__file__).parent / config_path
        self.config = self._load_config()
        self.api_key = api_key or self._get_api_key()
        self.client = self._initialize_client()
        self.results_dir = (
            Path(__file__).parent / self.config["reporting"]["output_directory"]
        )
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict:
        """Load validation configuration."""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)

    def _get_api_key(self) -> str:
        """Get API key from environment variables."""
        env_vars = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "azure": "AZURE_OPENAI_API_KEY",
        }

        env_var = env_vars.get(self.provider)
        if not env_var:
            logger.error(f"Unknown provider: {self.provider}")
            sys.exit(1)

        api_key = os.environ.get(env_var)
        if not api_key:
            logger.error(f"API key not found. Set {env_var} environment variable.")
            sys.exit(1)

        return api_key

    def _initialize_client(self):
        """Initialize AI provider client."""
        try:
            if self.provider == "anthropic":
                try:
                    import anthropic

                    return anthropic.Anthropic(api_key=self.api_key)
                except ImportError:
                    logger.error(
                        "anthropic package not installed. Run: pip install anthropic"
                    )
                    sys.exit(1)

            elif self.provider == "openai":
                try:
                    import openai

                    openai.api_key = self.api_key
                    return openai
                except ImportError:
                    logger.error(
                        "openai package not installed. Run: pip install openai"
                    )
                    sys.exit(1)

            else:
                logger.error(f"Provider {self.provider} not yet implemented")
                sys.exit(1)

        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} client: {e}")
            sys.exit(1)

    def _load_agent_prompt(self) -> str:
        """Load the agent validation prompt."""
        prompt_file = Path(__file__).parent / "VALIDATION_AGENT_PROMPT.md"
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load agent prompt: {e}")
            sys.exit(1)

    def _read_file_content(self, file_path: Path) -> str:
        """Read content of a documentation file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return ""

    def _create_validation_prompt(
        self, files: List[Path], batch_size: int = 5
    ) -> List[str]:
        """Create validation prompts for AI agent.

        Args:
            files: List of files to validate
            batch_size: Number of files per validation batch

        Returns:
            List of prompt strings for each batch
        """
        agent_prompt = self._load_agent_prompt()
        prompts = []

        # Process files in batches to avoid token limits
        for i in range(0, len(files), batch_size):
            batch = files[i : i + batch_size]

            file_contents = []
            for file_path in batch:
                content = self._read_file_content(file_path)
                if content:
                    file_contents.append(f"""
### File: {file_path}

```
{content}
```
""")

            batch_prompt = f"""
{agent_prompt}

---

## VALIDATION REQUEST - BATCH {i // batch_size + 1}

Please validate the following Databricks documentation files against the official
Databricks documentation at https://docs.databricks.com

### Files in This Batch:
{", ".join([str(f) for f in batch])}

### File Contents:

{"".join(file_contents)}

### Validation Requirements:
1. Compare each file against official Databricks documentation
2. Check for API accuracy, code correctness, configuration values
3. Identify deprecated features or outdated information
4. Rate accuracy for each file (0-100%)
5. List specific issues with line numbers
6. Provide actionable fix recommendations
7. Include URLs to official documentation for reference

### Output Format:
Provide a structured report following the format in the validation prompt, including:
- Executive summary with accuracy scores
- Detailed findings for each file
- Issue severity (Critical/High/Medium/Low)
- Specific line numbers and corrections
- Official documentation references

Generate the validation report now.
"""
            prompts.append(batch_prompt)

        return prompts

    def _call_anthropic_api(self, prompt: str) -> str:
        """Call Anthropic Claude API."""
        try:
            model = self.config["agent_configuration"]["model"]
            max_tokens = self.config["agent_configuration"]["max_tokens"]
            temperature = self.config["agent_configuration"]["temperature"]

            logger.info(f"Calling Anthropic API with model {model}...")

            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text

        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            raise

    def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI GPT API."""
        try:
            model = "gpt-4-turbo-preview"  # or from config

            logger.info(f"Calling OpenAI API with model {model}...")

            response = self.client.ChatCompletion.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a documentation validation expert.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.config["agent_configuration"]["temperature"],
                max_tokens=self.config["agent_configuration"]["max_tokens"],
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

    def _call_ai_agent(self, prompt: str) -> str:
        """Call appropriate AI agent based on provider."""
        if self.provider == "anthropic":
            return self._call_anthropic_api(prompt)
        elif self.provider == "openai":
            return self._call_openai_api(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _parse_agent_response(self, response: str) -> Dict:
        """Parse agent response and extract structured data."""
        # Extract key metrics from the response
        result = {
            "raw_response": response,
            "accuracy_score": 0.0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0,
            "findings": [],
            "recommendations": [],
        }

        # Parse accuracy score
        if "Accuracy Score:" in response or "accuracy score" in response.lower():
            try:
                # Look for percentage patterns
                import re

                matches = re.findall(r"(\d+(?:\.\d+)?)\s*%", response)
                if matches:
                    result["accuracy_score"] = float(matches[0])
            except:
                pass

        # Count issue severities
        result["critical_issues"] = response.lower().count("critical")
        result["high_issues"] = response.lower().count(
            "high priority"
        ) + response.lower().count("severity: high")
        result["medium_issues"] = response.lower().count(
            "medium priority"
        ) + response.lower().count("severity: medium")
        result["low_issues"] = response.lower().count(
            "low priority"
        ) + response.lower().count("severity: low")

        return result

    def _save_results(self, results: List[Dict], timestamp: str):
        """Save validation results to files."""
        # Combine all batch results
        combined_result = {
            "validation_id": f"VAL-{timestamp}",
            "timestamp": timestamp,
            "provider": self.provider,
            "config_version": self.config["validation"]["version"],
            "batches": len(results),
            "total_accuracy": 0.0,
            "total_critical": 0,
            "total_high": 0,
            "total_medium": 0,
            "total_low": 0,
            "batch_results": results,
        }

        # Calculate totals
        for batch in results:
            combined_result["total_critical"] += batch.get("critical_issues", 0)
            combined_result["total_high"] += batch.get("high_issues", 0)
            combined_result["total_medium"] += batch.get("medium_issues", 0)
            combined_result["total_low"] += batch.get("low_issues", 0)

        # Calculate average accuracy
        accuracy_scores = [
            b.get("accuracy_score", 0)
            for b in results
            if b.get("accuracy_score", 0) > 0
        ]
        if accuracy_scores:
            combined_result["total_accuracy"] = sum(accuracy_scores) / len(
                accuracy_scores
            )

        # Save JSON report
        json_path = self.results_dir / f"validation-report-{timestamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(combined_result, f, indent=2)
        logger.info(f"JSON report saved to {json_path}")

        # Save markdown report
        md_path = self.results_dir / f"validation-report-{timestamp}.md"
        self._save_markdown_report(combined_result, md_path)
        logger.info(f"Markdown report saved to {md_path}")

        # Save raw responses
        for i, batch in enumerate(results):
            raw_path = self.results_dir / f"validation-raw-{timestamp}-batch{i + 1}.md"
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(batch.get("raw_response", ""))

        return combined_result

    def _save_markdown_report(self, result: Dict, output_path: Path):
        """Save results as markdown report."""
        accuracy = result["total_accuracy"]

        if accuracy >= self.config["accuracy_thresholds"]["excellent"]:
            status = "🟢 EXCELLENT"
        elif accuracy >= self.config["accuracy_thresholds"]["good"]:
            status = "🟡 GOOD"
        elif accuracy >= self.config["accuracy_thresholds"]["needs_improvement"]:
            status = "🟠 NEEDS IMPROVEMENT"
        else:
            status = "🔴 REQUIRES ATTENTION"

        content = f"""# Databricks Documentation Validation Report

**Validation ID**: {result["validation_id"]}
**Date**: {result["timestamp"]}
**Provider**: {result["provider"].upper()}
**Status**: {status}
**Accuracy Score**: {accuracy:.1f}%

---

## Executive Summary

- **Validation Batches**: {result["batches"]}
- **Critical Issues**: 🔴 {result["total_critical"]}
- **High Priority Issues**: 🟠 {result["total_high"]}
- **Medium Priority Issues**: 🟡 {result["total_medium"]}
- **Low Priority Issues**: 🔵 {result["total_low"]}

---

## Quality Gates Status

| Gate | Threshold | Actual | Status |
|------|-----------|--------|--------|
| Minimum Accuracy | {self.config["quality_gates"]["minimum_accuracy_score"]}% | {accuracy:.1f}% | {self._gate_status(accuracy >= self.config["quality_gates"]["minimum_accuracy_score"])} |
| Max Critical Issues | {self.config["quality_gates"]["maximum_critical_issues"]} | {result["total_critical"]} | {self._gate_status(result["total_critical"] <= self.config["quality_gates"]["maximum_critical_issues"])} |
| Max High Issues | {self.config["quality_gates"]["maximum_high_issues"]} | {result["total_high"]} | {self._gate_status(result["total_high"] <= self.config["quality_gates"]["maximum_high_issues"])} |

---

## Batch Results

"""

        for i, batch in enumerate(result["batch_results"]):
            content += f"""
### Batch {i + 1}

- **Accuracy**: {batch.get("accuracy_score", 0):.1f}%
- **Critical Issues**: {batch.get("critical_issues", 0)}
- **High Issues**: {batch.get("high_issues", 0)}
- **Medium Issues**: {batch.get("medium_issues", 0)}
- **Low Issues**: {batch.get("low_issues", 0)}

**Details**: See `validation-raw-{result["timestamp"]}-batch{i + 1}.md` for full analysis.

"""

        content += f"""
---

## Next Steps

1. Review raw validation reports in the results directory
2. Address all CRITICAL issues immediately
3. Plan fixes for HIGH priority issues within 7 days
4. Schedule MEDIUM priority issues for next sprint

---

## Configuration

- **Agent Model**: {self.config["agent_configuration"]["model"]}
- **Temperature**: {self.config["agent_configuration"]["temperature"]}
- **Max Tokens**: {self.config["agent_configuration"]["max_tokens"]}
- **Provider**: {result["provider"]}

---

**Report Generated**: {datetime.now().isoformat()}
**Next Validation**: {self.config["schedule"]["frequency"]}
"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _gate_status(self, passed: bool) -> str:
        """Return status emoji for quality gate."""
        return "✅ PASS" if passed else "❌ FAIL"

    def validate(self, files: List[Path], batch_size: int = 3) -> Dict:
        """Run validation on specified files.

        Args:
            files: List of files to validate
            batch_size: Number of files to validate per API call

        Returns:
            Validation results dictionary
        """
        logger.info(f"Starting validation of {len(files)} files...")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Create validation prompts
        prompts = self._create_validation_prompt(files, batch_size)
        logger.info(f"Created {len(prompts)} validation batches")

        # Process each batch
        results = []
        for i, prompt in enumerate(prompts):
            logger.info(f"Processing batch {i + 1}/{len(prompts)}...")

            try:
                # Call AI agent
                response = self._call_ai_agent(prompt)

                # Parse response
                parsed = self._parse_agent_response(response)
                parsed["batch_number"] = i + 1
                results.append(parsed)

                logger.info(
                    f"Batch {i + 1} completed - Accuracy: {parsed.get('accuracy_score', 0):.1f}%"
                )

                # Rate limiting
                if i < len(prompts) - 1:
                    time.sleep(2)  # Wait between API calls

            except Exception as e:
                logger.error(f"Batch {i + 1} failed: {e}")
                results.append(
                    {"batch_number": i + 1, "error": str(e), "status": "failed"}
                )

        # Save results
        final_result = self._save_results(results, timestamp)

        logger.info("Validation complete!")
        logger.info(f"Overall Accuracy: {final_result['total_accuracy']:.1f}%")
        logger.info(
            f"Total Issues: {final_result['total_critical'] + final_result['total_high'] + final_result['total_medium'] + final_result['total_low']}"
        )

        return final_result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered Databricks documentation validation"
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai", "azure"],
        default="anthropic",
        help="AI provider to use",
    )
    parser.add_argument(
        "--scope",
        choices=["full", "api", "sdk", "sql", "examples"],
        default="full",
        help="Validation scope",
    )
    parser.add_argument("--files", nargs="+", help="Specific files to validate")
    parser.add_argument("--batch-size", type=int, default=3, help="Files per batch")
    parser.add_argument(
        "--config", default="validation-config.json", help="Configuration file path"
    )
    parser.add_argument("--api-key", help="API key (or set via environment)")
    parser.add_argument(
        "--interactive", action="store_true", help="Interactive mode with prompts"
    )

    args = parser.parse_args()

    # Initialize validator
    try:
        validator = AIAgentValidator(
            provider=args.provider, config_path=args.config, api_key=args.api_key
        )
    except Exception as e:
        logger.error(f"Failed to initialize validator: {e}")
        sys.exit(1)

    # Get files to validate
    from run_validation import ValidationRunner

    runner = ValidationRunner(config_path=args.config)
    files = runner._get_files_to_validate(args.scope, args.files)

    if not files:
        logger.error("No files found to validate")
        sys.exit(1)

    # Interactive confirmation
    if args.interactive:
        print(f"\nFound {len(files)} files to validate")
        print(f"Provider: {args.provider}")
        print(f"Batch size: {args.batch_size}")
        print(
            f"Estimated API calls: {(len(files) + args.batch_size - 1) // args.batch_size}"
        )
        response = input("\nProceed with validation? (yes/no): ")
        if response.lower() != "yes":
            print("Validation cancelled")
            sys.exit(0)

    # Run validation
    try:
        result = validator.validate(files, batch_size=args.batch_size)

        # Check quality gates
        passed = (
            result["total_accuracy"]
            >= validator.config["quality_gates"]["minimum_accuracy_score"]
            and result["total_critical"]
            <= validator.config["quality_gates"]["maximum_critical_issues"]
        )

        sys.exit(0 if passed else 1)

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Databricks Documentation Validation Runner

This script orchestrates the validation of Databricks documentation against
official sources using an AI agent. It can be run on-demand or scheduled.

Usage:
    python run_validation.py --scope full
    python run_validation.py --scope api --files "docs/api/*.md"
    python run_validation.py --config validation-config.json
"""

import argparse
import glob
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ValidationRunner:
    """Orchestrates documentation validation using AI agent."""

    def __init__(self, config_path: str = "validation-config.json"):
        """Initialize validation runner with configuration."""
        self.config_path = Path(__file__).parent / config_path
        self.config = self._load_config()
        self.results_dir = (
            Path(__file__).parent / self.config["reporting"]["output_directory"]
        )
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.validation_results = []

    def _load_config(self) -> Dict:
        """Load validation configuration."""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            sys.exit(1)

    def _get_files_to_validate(
        self, scope: str = "full", files: Optional[List[str]] = None
    ) -> List[Path]:
        """Get list of files to validate based on scope."""
        if files:
            # Use explicitly provided files
            all_files = []
            for pattern in files:
                all_files.extend(glob.glob(pattern, recursive=True))
            return [Path(f) for f in all_files]

        # Get files based on include/exclude patterns
        include_patterns = self.config["scope"]["include_paths"]
        exclude_patterns = self.config["scope"]["exclude_paths"]

        repo_root = Path(__file__).parent.parent.parent
        all_files = []

        for pattern in include_patterns:
            full_pattern = str(repo_root / pattern)
            matched_files = glob.glob(full_pattern, recursive=True)
            all_files.extend(matched_files)

        # Filter out excluded files
        filtered_files = []
        for file_path in all_files:
            exclude = False
            for exclude_pattern in exclude_patterns:
                if Path(file_path).match(exclude_pattern):
                    exclude = True
                    break
            if not exclude:
                filtered_files.append(Path(file_path))

        logger.info(f"Found {len(filtered_files)} files to validate")
        return filtered_files

    def _load_agent_prompt(self) -> str:
        """Load the agent validation prompt."""
        prompt_file = Path(__file__).parent / "VALIDATION_AGENT_PROMPT.md"
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load agent prompt: {e}")
            sys.exit(1)

    def _generate_validation_request(self, files: List[Path]) -> str:
        """Generate validation request for AI agent."""
        agent_prompt = self._load_agent_prompt()

        file_list = "\n".join([f"- {f}" for f in files])

        validation_request = f"""
{agent_prompt}

---

## VALIDATION REQUEST

Please validate the following Databricks documentation files against the official
Databricks documentation at https://docs.databricks.com

### Files to Validate:
{file_list}

### Validation Configuration:
- Validation Types: {", ".join(self.config["scope"]["validation_types"])}
- Accuracy Threshold: {self.config["accuracy_thresholds"]["good"]}%
- Generate Fix Suggestions: {self.config["agent_configuration"]["generate_fix_suggestions"]}

### Instructions:
1. Review each file systematically
2. Compare against official Databricks documentation
3. Identify discrepancies, errors, and outdated information
4. Rate accuracy for each file
5. Generate detailed findings with line numbers
6. Provide actionable recommendations
7. Follow the output format specified in the prompt

### Priority Focus Areas:
- API endpoint accuracy (critical)
- Code example syntax and correctness (high)
- Configuration values and defaults (high)
- Deprecated features (high)
- Security best practices (critical)

Generate a comprehensive validation report following the format specified above.
"""
        return validation_request

    def _create_report_template(self, timestamp: str) -> Dict:
        """Create empty report template."""
        return {
            "validation_id": f"VAL-{timestamp}",
            "timestamp": timestamp,
            "config_version": self.config["validation"]["version"],
            "scope": "full",
            "files_validated": 0,
            "total_issues": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0,
            "accuracy_score": 0.0,
            "status": "pending",
            "findings": [],
            "recommendations": [],
        }

    def _save_report(self, report: Dict, format: str = "markdown"):
        """Save validation report to file."""
        timestamp = report["timestamp"]

        if (
            format == "markdown"
            or self.config["reporting"]["report_format"] == "markdown"
        ):
            self._save_markdown_report(report, timestamp)

        if self.config["reporting"]["generate_json_export"]:
            self._save_json_report(report, timestamp)

    def _save_markdown_report(self, report: Dict, timestamp: str):
        """Save report in markdown format."""
        report_path = self.results_dir / f"validation-report-{timestamp}.md"

        accuracy_score = report.get("accuracy_score", 0)
        if accuracy_score >= self.config["accuracy_thresholds"]["excellent"]:
            status_badge = "🟢 EXCELLENT"
        elif accuracy_score >= self.config["accuracy_thresholds"]["good"]:
            status_badge = "🟡 GOOD"
        elif accuracy_score >= self.config["accuracy_thresholds"]["needs_improvement"]:
            status_badge = "🟠 NEEDS IMPROVEMENT"
        else:
            status_badge = "🔴 REQUIRES ATTENTION"

        content = f"""# Databricks Documentation Validation Report

**Validation ID**: {report["validation_id"]}
**Date**: {timestamp}
**Status**: {status_badge}
**Accuracy Score**: {accuracy_score:.1f}%

---

## Executive Summary

- **Total Files Validated**: {report["files_validated"]}
- **Total Issues Found**: {report["total_issues"]}
- **Critical Issues**: 🔴 {report["critical_issues"]}
- **High Priority Issues**: 🟠 {report["high_issues"]}
- **Medium Priority Issues**: 🟡 {report["medium_issues"]}
- **Low Priority Issues**: 🔵 {report["low_issues"]}

---

## Validation Scope

**Validation Types**:
{self._format_list(self.config["scope"]["validation_types"])}

**Official Sources Referenced**:
{self._format_dict_as_list(self.config["official_sources"])}

---

## Quality Gates Status

| Gate | Threshold | Actual | Status |
|------|-----------|--------|--------|
| Minimum Accuracy | {self.config["quality_gates"]["minimum_accuracy_score"]}% | {accuracy_score:.1f}% | {self._check_gate(accuracy_score >= self.config["quality_gates"]["minimum_accuracy_score"])} |
| Max Critical Issues | {self.config["quality_gates"]["maximum_critical_issues"]} | {report["critical_issues"]} | {self._check_gate(report["critical_issues"] <= self.config["quality_gates"]["maximum_critical_issues"])} |
| Max High Issues | {self.config["quality_gates"]["maximum_high_issues"]} | {report["high_issues"]} | {self._check_gate(report["high_issues"] <= self.config["quality_gates"]["maximum_high_issues"])} |

---

## Detailed Findings

{self._format_findings(report.get("findings", []))}

---

## Recommendations

{self._format_recommendations(report.get("recommendations", []))}

---

## Next Steps

1. Review and address all CRITICAL issues immediately
2. Plan fixes for HIGH priority issues within 7 days
3. Schedule MEDIUM priority issues for next sprint
4. Track LOW priority issues in backlog

---

## Validation Configuration

- **Config Version**: {self.config["validation"]["version"]}
- **Agent Model**: {self.config["agent_configuration"]["model"]}
- **Comparison Mode**: {self.config["agent_configuration"]["comparison_mode"]}

---

**Report Generated**: {datetime.now().isoformat()}
**Next Validation**: {self.config["schedule"]["frequency"]} - {self.config["schedule"]["day"]} at {self.config["schedule"]["time"]} {self.config["schedule"]["timezone"]}
"""

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Markdown report saved to {report_path}")

    def _save_json_report(self, report: Dict, timestamp: str):
        """Save report in JSON format."""
        report_path = self.results_dir / f"validation-report-{timestamp}.json"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"JSON report saved to {report_path}")

    def _format_list(self, items: List) -> str:
        """Format list as markdown bullets."""
        return "\n".join([f"- {item}" for item in items])

    def _format_dict_as_list(self, items: Dict) -> str:
        """Format dictionary as markdown bullets."""
        return "\n".join([f"- **{key}**: {value}" for key, value in items.items()])

    def _check_gate(self, passed: bool) -> str:
        """Return status emoji for quality gate."""
        return "✅ PASS" if passed else "❌ FAIL"

    def _format_findings(self, findings: List[Dict]) -> str:
        """Format findings section."""
        if not findings:
            return "_No issues found. All documentation appears accurate._"

        sections = []
        for finding in findings:
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🔵",
            }.get(finding.get("severity", "low").lower(), "⚪")

            section = f"""
### {severity_emoji} {finding.get("title", "Issue")}

- **Severity**: {finding.get("severity", "Unknown")}
- **Type**: {finding.get("type", "Unknown")}
- **File**: `{finding.get("file", "Unknown")}`
- **Location**: Lines {finding.get("lines", "N/A")}

**Description**: {finding.get("description", "No description provided")}

**Recommended Action**: {finding.get("recommendation", "Review and update")}

**Official Reference**: {finding.get("source_url", "N/A")}
"""
            sections.append(section)

        return "\n---\n".join(sections)

    def _format_recommendations(self, recommendations: List) -> str:
        """Format recommendations section."""
        if not recommendations:
            return "_No specific recommendations at this time._"

        return "\n".join([f"{i + 1}. {rec}" for i, rec in enumerate(recommendations)])

    def run_validation(
        self, scope: str = "full", files: Optional[List[str]] = None
    ) -> Dict:
        """Run the validation process."""
        logger.info("Starting documentation validation...")

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Get files to validate
        files_to_validate = self._get_files_to_validate(scope, files)

        if not files_to_validate:
            logger.warning("No files found to validate")
            return {"status": "error", "message": "No files to validate"}

        # Generate validation request
        validation_request = self._generate_validation_request(files_to_validate)

        # Create report template
        report = self._create_report_template(timestamp)
        report["files_validated"] = len(files_to_validate)
        report["scope"] = scope

        # Save validation request for agent
        request_path = self.results_dir / f"validation-request-{timestamp}.txt"
        with open(request_path, "w", encoding="utf-8") as f:
            f.write(validation_request)

        logger.info(f"Validation request saved to {request_path}")

        # Output instructions for manual execution
        print("\n" + "=" * 80)
        print("VALIDATION REQUEST GENERATED")
        print("=" * 80)
        print(f"\nValidation request has been saved to:\n  {request_path}")
        print(f"\nTo complete validation, please:")
        print("1. Copy the content of the validation request file")
        print("2. Provide it to your AI assistant (Claude, GPT-4, etc.)")
        print("3. The agent will analyze the documentation and generate a report")
        print("4. Save the agent's report output")
        print("\nAlternatively, integrate with an AI API to automate this step.")
        print("\nConfiguration:")
        print(f"  - Agent Model: {self.config['agent_configuration']['model']}")
        print(f"  - Files to Validate: {len(files_to_validate)}")
        print(
            f"  - Accuracy Threshold: {self.config['quality_gates']['minimum_accuracy_score']}%"
        )
        print("=" * 80 + "\n")

        # For now, create a placeholder report
        report["status"] = "request_generated"
        report["message"] = "Validation request generated. Awaiting agent execution."

        self._save_report(report)

        return report

    def process_agent_response(self, response_file: str):
        """Process the validation response from the AI agent."""
        logger.info(f"Processing agent response from {response_file}")

        try:
            with open(response_file, "r", encoding="utf-8") as f:
                response_content = f.read()

            # Parse the response and extract key metrics
            # This is a simplified parser - enhance based on actual response format
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            report = self._create_report_template(timestamp)
            report["status"] = "completed"
            report["raw_response"] = response_content

            # Save the processed report
            self._save_report(report)

            logger.info("Agent response processed successfully")
            return report

        except Exception as e:
            logger.error(f"Failed to process agent response: {e}")
            return {"status": "error", "message": str(e)}


def main():
    """Main entry point for validation runner."""
    parser = argparse.ArgumentParser(
        description="Run Databricks documentation validation"
    )
    parser.add_argument(
        "--scope",
        choices=["full", "api", "sdk", "sql", "examples", "custom"],
        default="full",
        help="Validation scope",
    )
    parser.add_argument(
        "--files", nargs="+", help="Specific files or patterns to validate"
    )
    parser.add_argument(
        "--config",
        default="validation-config.json",
        help="Path to validation configuration file",
    )
    parser.add_argument("--process-response", help="Process an agent response file")

    args = parser.parse_args()

    # Initialize runner
    runner = ValidationRunner(config_path=args.config)

    if args.process_response:
        # Process existing agent response
        result = runner.process_agent_response(args.process_response)
    else:
        # Run new validation
        result = runner.run_validation(scope=args.scope, files=args.files)

    # Exit with appropriate code
    if result.get("status") in ["error", "failed"]:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

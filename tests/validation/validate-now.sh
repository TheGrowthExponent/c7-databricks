#!/bin/bash
# Quick Documentation Validation Script
# Run this script to validate documentation immediately

set -e

echo "=========================================="
echo "Databricks Documentation Validator"
echo "=========================================="
echo ""

# Check if in correct directory
if [ ! -f "validation-config.json" ]; then
    echo "❌ Error: Must run from tests/validation directory"
    echo "Usage: cd tests/validation && bash validate-now.sh"
    exit 1
fi

# Check Python installation
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed"
    exit 1
fi

echo "Select validation mode:"
echo "1) Full automated validation (requires API key)"
echo "2) Generate validation request (manual AI review)"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "Select AI provider:"
        echo "1) Anthropic Claude (recommended)"
        echo "2) OpenAI GPT-4"
        echo ""
        read -p "Enter choice (1 or 2): " provider_choice

        if [ "$provider_choice" = "1" ]; then
            PROVIDER="anthropic"
            API_KEY_VAR="ANTHROPIC_API_KEY"
        else
            PROVIDER="openai"
            API_KEY_VAR="OPENAI_API_KEY"
        fi

        # Check API key
        if [ -z "${!API_KEY_VAR}" ]; then
            echo ""
            echo "❌ API key not found in environment"
            echo "Please set $API_KEY_VAR:"
            echo "  export $API_KEY_VAR='your-api-key-here'"
            exit 1
        fi

        echo ""
        echo "Select validation scope:"
        echo "1) Full repository"
        echo "2) API docs only"
        echo "3) SDK docs only"
        echo "4) SQL examples only"
        echo ""
        read -p "Enter choice (1-4): " scope_choice

        case $scope_choice in
            1) SCOPE="full" ;;
            2) SCOPE="api" ;;
            3) SCOPE="sdk" ;;
            4) SCOPE="sql" ;;
            *) SCOPE="full" ;;
        esac

        echo ""
        echo "🔍 Starting validation..."
        echo "  Provider: $PROVIDER"
        echo "  Scope: $SCOPE"
        echo ""

        # Check dependencies
        if ! python -c "import anthropic" 2>/dev/null && [ "$PROVIDER" = "anthropic" ]; then
            echo "📦 Installing dependencies..."
            pip install anthropic
        fi

        if ! python -c "import openai" 2>/dev/null && [ "$PROVIDER" = "openai" ]; then
            echo "📦 Installing dependencies..."
            pip install openai
        fi

        # Run validation
        python agent_validator.py --provider "$PROVIDER" --scope "$SCOPE" --interactive

        EXIT_CODE=$?

        echo ""
        if [ $EXIT_CODE -eq 0 ]; then
            echo "✅ Validation completed successfully"
            echo "📊 Check results in: tests/validation/results/"
        else
            echo "❌ Validation failed or quality gates not met"
            echo "📊 Check results in: tests/validation/results/"
        fi

        # Show latest report
        LATEST_REPORT=$(ls -t results/validation-report-*.md 2>/dev/null | head -1)
        if [ -f "$LATEST_REPORT" ]; then
            echo ""
            echo "📄 Latest report: $LATEST_REPORT"
            echo ""
            echo "View with: cat $LATEST_REPORT | less"
        fi
        ;;

    2)
        echo ""
        echo "Select validation scope:"
        echo "1) Full repository"
        echo "2) API docs only"
        echo "3) SDK docs only"
        echo "4) SQL examples only"
        echo ""
        read -p "Enter choice (1-4): " scope_choice

        case $scope_choice in
            1) SCOPE="full" ;;
            2) SCOPE="api" ;;
            3) SCOPE="sdk" ;;
            4) SCOPE="sql" ;;
            *) SCOPE="full" ;;
        esac

        echo ""
        echo "🔍 Generating validation request..."
        echo "  Scope: $SCOPE"
        echo ""

        python run_validation.py --scope "$SCOPE"

        echo ""
        echo "✅ Validation request generated"
        echo ""
        echo "Next steps:"
        echo "1. Find the validation request in: tests/validation/results/"
        echo "2. Copy the entire request"
        echo "3. Provide it to your AI assistant (Claude, GPT-4, etc.)"
        echo "4. Save the AI's response"
        echo "5. Review findings and update documentation"
        echo ""

        # Show latest request file
        LATEST_REQUEST=$(ls -t results/validation-request-*.txt 2>/dev/null | head -1)
        if [ -f "$LATEST_REQUEST" ]; then
            echo "📄 Request file: $LATEST_REQUEST"
            echo ""
            read -p "View request now? (y/n): " view_choice
            if [ "$view_choice" = "y" ]; then
                cat "$LATEST_REQUEST" | less
            fi
        fi
        ;;

    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="

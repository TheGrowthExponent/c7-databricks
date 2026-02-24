# Databricks Documentation Validation - PowerShell Script
# Run this script to validate documentation on Windows

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('full', 'api', 'sdk', 'sql', 'examples')]
    [string]$Scope = '',

    [Parameter(Mandatory=$false)]
    [ValidateSet('anthropic', 'openai')]
    [string]$Provider = '',

    [Parameter(Mandatory=$false)]
    [switch]$Interactive = $false,

    [Parameter(Mandatory=$false)]
    [switch]$Manual = $false
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Databricks Documentation Validator" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "validation-config.json"))
{
    Write-Host "Error: Must run from tests\validation directory" -ForegroundColor Red
    Write-Host "Usage: cd tests\validation; .\validate-now.ps1" -ForegroundColor Yellow
    exit 1
}

# Check Python installation
try
{
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch
{
    Write-Host "Error: Python is not installed" -ForegroundColor Red
    exit 1
}

# Determine validation mode
if (-not $Manual)
{
    if (-not $Interactive)
    {
        Write-Host "Select validation mode:" -ForegroundColor Yellow
        Write-Host "1) Full automated validation (requires API key)"
        Write-Host "2) Generate validation request (manual AI review)"
        Write-Host ""
        $choice = Read-Host "Enter choice (1 or 2)"
    } else
    {
        $choice = "1"
    }
} else
{
    $choice = "2"
}

if ($choice -eq "1")
{
    Write-Host ""

    # Select provider if not specified
    if (-not $Provider)
    {
        Write-Host "Select AI provider:" -ForegroundColor Yellow
        Write-Host "1) Anthropic Claude (recommended)"
        Write-Host "2) OpenAI GPT-4"
        Write-Host ""
        $providerChoice = Read-Host "Enter choice (1 or 2)"

        if ($providerChoice -eq "1")
        {
            $Provider = "anthropic"
            $apiKeyVar = "ANTHROPIC_API_KEY"
        } else
        {
            $Provider = "openai"
            $apiKeyVar = "OPENAI_API_KEY"
        }
    } else
    {
        if ($Provider -eq "anthropic")
        {
            $apiKeyVar = "ANTHROPIC_API_KEY"
        } else
        {
            $apiKeyVar = "OPENAI_API_KEY"
        }
    }

    # Check API key
    $apiKey = [Environment]::GetEnvironmentVariable($apiKeyVar)
    if (-not $apiKey)
    {
        Write-Host ""
        Write-Host "Error: API key not found in environment" -ForegroundColor Red
        Write-Host "Please set $apiKeyVar :" -ForegroundColor Yellow
        Write-Host "  `$env:$apiKeyVar='your-api-key-here'" -ForegroundColor Yellow
        Write-Host "  Or permanently: [Environment]::SetEnvironmentVariable('$apiKeyVar', 'your-key', 'User')" -ForegroundColor Yellow
        exit 1
    }

    # Select scope if not specified
    if (-not $Scope)
    {
        Write-Host ""
        Write-Host "Select validation scope:" -ForegroundColor Yellow
        Write-Host "1) Full repository"
        Write-Host "2) API docs only"
        Write-Host "3) SDK docs only"
        Write-Host "4) SQL examples only"
        Write-Host ""
        $scopeChoice = Read-Host "Enter choice (1-4)"

        switch ($scopeChoice)
        {
            "1"
            { $Scope = "full" 
            }
            "2"
            { $Scope = "api" 
            }
            "3"
            { $Scope = "sdk" 
            }
            "4"
            { $Scope = "sql" 
            }
            default
            { $Scope = "full" 
            }
        }
    }

    Write-Host ""
    Write-Host "Starting validation..." -ForegroundColor Green
    Write-Host "  Provider: $Provider" -ForegroundColor Cyan
    Write-Host "  Scope: $Scope" -ForegroundColor Cyan
    Write-Host ""

    # Check dependencies
    Write-Host "Checking dependencies..." -ForegroundColor Yellow

    try
    {
        python -c "import anthropic" 2>&1 | Out-Null
    } catch
    {
        if ($Provider -eq "anthropic")
        {
            Write-Host "Installing anthropic..." -ForegroundColor Yellow
            pip install anthropic
        }
    }

    try
    {
        python -c "import openai" 2>&1 | Out-Null
    } catch
    {
        if ($Provider -eq "openai")
        {
            Write-Host "Installing openai..." -ForegroundColor Yellow
            pip install openai
        }
    }

    # Run validation
    Write-Host "Running validation (this may take a few minutes)..." -ForegroundColor Yellow

    if ($Interactive)
    {
        python agent_validator.py --provider $Provider --scope $Scope --interactive
    } else
    {
        python agent_validator.py --provider $Provider --scope $Scope
    }

    $exitCode = $LASTEXITCODE

    Write-Host ""
    if ($exitCode -eq 0)
    {
        Write-Host "Validation completed successfully!" -ForegroundColor Green
        Write-Host "Check results in: tests\validation\results\" -ForegroundColor Cyan
    } else
    {
        Write-Host "Validation failed or quality gates not met" -ForegroundColor Red
        Write-Host "Check results in: tests\validation\results\" -ForegroundColor Cyan
    }

    # Show latest report
    $latestReport = Get-ChildItem -Path "results\validation-report-*.md" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($latestReport)
    {
        Write-Host ""
        Write-Host "Latest report: $($latestReport.Name)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "View with: Get-Content $($latestReport.FullName) | more" -ForegroundColor Yellow

        # Extract accuracy if JSON exists
        $jsonReport = $latestReport.FullName -replace '\.md$', '.json'
        if (Test-Path $jsonReport)
        {
            try
            {
                $reportData = Get-Content $jsonReport | ConvertFrom-Json
                Write-Host ""
                Write-Host "Quick Summary:" -ForegroundColor Green
                Write-Host "  Accuracy: $($reportData.total_accuracy)%" -ForegroundColor Cyan
                Write-Host "  Critical: $($reportData.total_critical)" -ForegroundColor $(if ($reportData.total_critical -gt 0)
                    { "Red" 
                    } else
                    { "Green" 
                    })
                Write-Host "  High: $($reportData.total_high)" -ForegroundColor $(if ($reportData.total_high -gt 5)
                    { "Yellow" 
                    } else
                    { "Green" 
                    })
            } catch
            {
                # Ignore JSON parse errors
            }
        }
    }

} elseif ($choice -eq "2")
{
    Write-Host ""

    # Select scope if not specified
    if (-not $Scope)
    {
        Write-Host "Select validation scope:" -ForegroundColor Yellow
        Write-Host "1) Full repository"
        Write-Host "2) API docs only"
        Write-Host "3) SDK docs only"
        Write-Host "4) SQL examples only"
        Write-Host ""
        $scopeChoice = Read-Host "Enter choice (1-4)"

        switch ($scopeChoice)
        {
            "1"
            { $Scope = "full" 
            }
            "2"
            { $Scope = "api" 
            }
            "3"
            { $Scope = "sdk" 
            }
            "4"
            { $Scope = "sql" 
            }
            default
            { $Scope = "full" 
            }
        }
    }

    Write-Host ""
    Write-Host "Generating validation request..." -ForegroundColor Green
    Write-Host "  Scope: $Scope" -ForegroundColor Cyan
    Write-Host ""

    python run_validation.py --scope $Scope

    Write-Host ""
    Write-Host "Validation request generated!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Find the validation request in: tests\validation\results\" -ForegroundColor White
    Write-Host "2. Copy the entire request" -ForegroundColor White
    Write-Host "3. Provide it to your AI assistant (Claude, GPT-4, etc.)" -ForegroundColor White
    Write-Host "4. Save the AI's response" -ForegroundColor White
    Write-Host "5. Review findings and update documentation" -ForegroundColor White
    Write-Host ""

    # Show latest request file
    $latestRequest = Get-ChildItem -Path "results\validation-request-*.txt" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($latestRequest)
    {
        Write-Host "Request file: $($latestRequest.Name)" -ForegroundColor Cyan
        Write-Host ""
        $viewChoice = Read-Host "View request now? (y/n)"
        if ($viewChoice -eq "y")
        {
            Get-Content $latestRequest.FullName | more
        }
    }

} else
{
    Write-Host "Invalid choice" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

exit 0

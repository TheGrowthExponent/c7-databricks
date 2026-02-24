@echo off
REM Quick Documentation Validation Script for Windows
REM Run this script to validate documentation immediately

setlocal enabledelayedexpansion

echo ==========================================
echo Databricks Documentation Validator
echo ==========================================
echo.

REM Check if in correct directory
if not exist "validation-config.json" (
    echo Error: Must run from tests\validation directory
    echo Usage: cd tests\validation ^&^& validate-now.bat
    exit /b 1
)

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    exit /b 1
)

echo Select validation mode:
echo 1) Full automated validation (requires API key)
echo 2) Generate validation request (manual AI review)
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Select AI provider:
    echo 1) Anthropic Claude (recommended)
    echo 2) OpenAI GPT-4
    echo.
    set /p provider_choice="Enter choice (1 or 2): "

    if "!provider_choice!"=="1" (
        set PROVIDER=anthropic
        set API_KEY_VAR=ANTHROPIC_API_KEY
    ) else (
        set PROVIDER=openai
        set API_KEY_VAR=OPENAI_API_KEY
    )

    REM Check API key
    call :check_env_var !API_KEY_VAR!
    if errorlevel 1 (
        echo.
        echo Error: API key not found in environment
        echo Please set !API_KEY_VAR!:
        echo   set !API_KEY_VAR!=your-api-key-here
        exit /b 1
    )

    echo.
    echo Select validation scope:
    echo 1) Full repository
    echo 2) API docs only
    echo 3) SDK docs only
    echo 4) SQL examples only
    echo.
    set /p scope_choice="Enter choice (1-4): "

    if "!scope_choice!"=="1" set SCOPE=full
    if "!scope_choice!"=="2" set SCOPE=api
    if "!scope_choice!"=="3" set SCOPE=sdk
    if "!scope_choice!"=="4" set SCOPE=sql
    if not defined SCOPE set SCOPE=full

    echo.
    echo Starting validation...
    echo   Provider: !PROVIDER!
    echo   Scope: !SCOPE!
    echo.

    REM Check dependencies
    python -c "import anthropic" >nul 2>&1
    if errorlevel 1 (
        if "!PROVIDER!"=="anthropic" (
            echo Installing dependencies...
            pip install anthropic
        )
    )

    python -c "import openai" >nul 2>&1
    if errorlevel 1 (
        if "!PROVIDER!"=="openai" (
            echo Installing dependencies...
            pip install openai
        )
    )

    REM Run validation
    python agent_validator.py --provider !PROVIDER! --scope !SCOPE! --interactive

    if errorlevel 1 (
        echo.
        echo Validation failed or quality gates not met
        echo Check results in: tests\validation\results\
    ) else (
        echo.
        echo Validation completed successfully
        echo Check results in: tests\validation\results\
    )

    REM Show latest report
    for /f "delims=" %%i in ('dir /b /o-d results\validation-report-*.md 2^>nul') do (
        set LATEST_REPORT=results\%%i
        goto :found_report
    )
    :found_report
    if defined LATEST_REPORT (
        echo.
        echo Latest report: !LATEST_REPORT!
        echo.
        echo View with: type !LATEST_REPORT! ^| more
    )

) else if "%choice%"=="2" (
    echo.
    echo Select validation scope:
    echo 1) Full repository
    echo 2) API docs only
    echo 3) SDK docs only
    echo 4) SQL examples only
    echo.
    set /p scope_choice="Enter choice (1-4): "

    if "!scope_choice!"=="1" set SCOPE=full
    if "!scope_choice!"=="2" set SCOPE=api
    if "!scope_choice!"=="3" set SCOPE=sdk
    if "!scope_choice!"=="4" set SCOPE=sql
    if not defined SCOPE set SCOPE=full

    echo.
    echo Generating validation request...
    echo   Scope: !SCOPE!
    echo.

    python run_validation.py --scope !SCOPE!

    echo.
    echo Validation request generated
    echo.
    echo Next steps:
    echo 1. Find the validation request in: tests\validation\results\
    echo 2. Copy the entire request
    echo 3. Provide it to your AI assistant (Claude, GPT-4, etc.)
    echo 4. Save the AI's response
    echo 5. Review findings and update documentation
    echo.

    REM Show latest request file
    for /f "delims=" %%i in ('dir /b /o-d results\validation-request-*.txt 2^>nul') do (
        set LATEST_REQUEST=results\%%i
        goto :found_request
    )
    :found_request
    if defined LATEST_REQUEST (
        echo Request file: !LATEST_REQUEST!
        echo.
        set /p view_choice="View request now? (y/n): "
        if /i "!view_choice!"=="y" (
            type !LATEST_REQUEST! | more
        )
    )

) else (
    echo Invalid choice
    exit /b 1
)

echo.
echo ==========================================
echo Done!
echo ==========================================

endlocal
exit /b 0

:check_env_var
if not defined %1 exit /b 1
exit /b 0

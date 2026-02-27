# Quick reference script to get today's date in ISO 8601 format
# Rule: DATE-CLI-001 - Get Today's Date from CLI Before Adding Last Updated Dates
# Usage: .\get-date.ps1

$TODAY = Get-Date -Format "yyyy-MM-dd"
Write-Host "Today's date: $TODAY" -ForegroundColor Green
Write-Host ""
Write-Host "Use this date for 'last_updated' fields in documentation files."
Write-Host "Format: YYYY-MM-DD (ISO 8601)"
Write-Host ""
Write-Host "Example usage in Markdown frontmatter:" -ForegroundColor Cyan
Write-Host "---"
Write-Host "title: Document Title"
Write-Host "last_updated: $TODAY"
Write-Host "---"

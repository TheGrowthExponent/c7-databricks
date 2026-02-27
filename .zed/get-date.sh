#!/bin/bash
# Quick reference script to get today's date in ISO 8601 format
# Rule: DATE-CLI-001 - Get Today's Date from CLI Before Adding Last Updated Dates
# Usage: ./get-date.sh

TODAY=$(date +%Y-%m-%d)
echo "Today's date: $TODAY"
echo ""
echo "Use this date for 'last_updated' fields in documentation files."
echo "Format: YYYY-MM-DD (ISO 8601)"

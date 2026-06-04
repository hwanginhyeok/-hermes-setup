#!/bin/bash

# Cron Status Verification Script
# Quick overview of all cron jobs and their recent execution status

echo "======================================"
echo "Cron Status Verification"
echo "======================================"
echo ""

# 1. Check Hermes cron jobs
echo "📌 Hermes Cron Jobs:"
if command -v cronjob &> /dev/null; then
    cronjob action=list 2>/dev/null | head -30
else
    echo "  ⚠️  cronjob command not available"
fi
echo ""

# 2. Show active systemd services
echo "📌 Active Systemd User Services:"
systemctl --user list-units --type=service --state=running --no-pager | head -10
echo ""

# 3. Check recent crontab logs
echo "📌 Recent Crontab Log Activity:"
echo ""
echo "  Be:A Studio Daily (last 10 lines):"
if [ -f ~/.pm_logs/be_a_studio_daily.log ]; then
    tail -3 ~/.pm_logs/be_a_studio_daily.log | sed 's/^/    /'
else
    echo "    ⚠️  Log file not found"
fi

echo ""
echo "  Service Health (last 5 lines):"
if [ -f ~/.pm_logs/service_health.log ]; then
    tail -2 ~/.pm_logs/service_health.log | sed 's/^/    /'
else
    echo "    ⚠️  Log file not found"
fi

echo ""
echo "  Nightly Healthcheck (last 5 lines):"
if [ -f ~/.pm_logs/nightly_healthcheck.log ]; then
    tail -2 ~/.pm_logs/nightly_healthcheck.log | sed 's/^/    /'
else
    echo "    ⚠️  Log file not found"
fi

echo ""
echo "======================================"
echo "🔍 Quick Log Search:"
echo "======================================"
echo ""
echo "Search pattern (leave blank to skip):"
read -r SEARCH_PATTERN

if [ -n "$SEARCH_PATTERN" ]; then
    echo ""
    echo "Searching for: $SEARCH_PATTERN"
    echo ""
    grep -i "$SEARCH_PATTERN" ~/.pm_logs/*.log 2>/dev/null | tail -10 | sed 's/^/  /'
fi

echo ""
echo "======================================"
echo "✓ Verification complete"
echo "======================================"

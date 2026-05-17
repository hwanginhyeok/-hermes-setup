#!/bin/bash
# tmux 세션별 pane 수 확인 및 보고
# PM 오케스트레이션에서 세션 상태 진단용

echo "=== tmux 세션별 pane 수 ==="
for session in PM bea insung stock music hermes; do
    if tmux has-session -t "$session" 2>/dev/null; then
        panes=$(tmux list-panes -t "${session}:1" 2>/dev/null | wc -l)
        expected=3
        case "$session" in
            PM) expected=4 ;;
            bea) expected=4 ;;
            hermes) expected=2 ;;
        esac
        
        if (( panes == expected )); then
            echo "✅ $session: $panes panes"
        else
            echo "⚠️  $session: $panes panes (기대: $expected)"
        fi
    else
        echo "❌ $session: 세션 없음"
    fi
done

echo ""
echo "=== 전체 세션 목록 ==="
tmux list-sessions 2>/dev/null || echo "tmux 세션 없음"

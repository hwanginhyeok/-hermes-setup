# tmux Session Management - PM Workspace

## Session Architecture (2026-05-20 standardized)

### Standard Pane Layout

| Session | Panes | Purpose | Layout |
|---------|-------|---------|--------|
| **PM** | 4 | Orchestrator | tiled (claude + bash×3) |
| **bea** | 2 | be-a-studio | main-vertical (claude + bash) |
| **stock** | 2 | 주식부자 | main-vertical (claude + bash) |
| **insung** | 2 | 인성이 | main-vertical (claude + bash) |
| **music** | 2 | music-lab | main-vertical (claude + bash) |
| **hermes** | 2 | Automation | main-vertical (gateway + chat) |

### Pane Purposes

- **pane 1**: Primary agent (claude, hermes gateway)
- **pane 2**: Bash shell (for manual commands, additional agents)

### Session Creation Script

Location: `~/project-manager/open-all.sh`

**Key behaviors**:
- Creates all sessions if they don't exist
- **Adds missing panes** up to target count
- **Does NOT remove extra panes** (requires session rebuild)
- English session names only (stock, insung, music, bea, hermes)

## Common Issues

### Korean/English Session Name Conflicts

**Problem**: Old sessions with Korean names coexist with new English names

**Detection**:
```bash
tmux list-sessions -F "#{session_name}"
# Shows: 주식부자, 인성이, 자율주행, stock, insung, music, bea
```

**Fix**:
```bash
# Kill Korean sessions
tmux kill-session -t 주식부자
tmux kill-session -t 인성이
tmux kill-session -t 자율주행

# Rebuild with English names
cd ~/project-manager && ./open-all.sh
```

**Prevention**: Always use English session names. Script creates English names only.

### Pane Count Mismatch

**Problem**: Session has more/fewer panes than expected

**Detection**:
```bash
tmux list-sessions -F "#{session_name}: #{window_panes} panes"
```

**Case 1: Too few panes**
- Script auto-adds missing panes
- Just run `./open-all.sh`

**Case 2: Too many panes**
- Script will NOT auto-remove
- Must rebuild session:
  ```bash
  tmux kill-session -t <session-name>
  cd ~/project-manager && ./open-all.sh
  ```

**Case 3: Pane count reduction in script**
- After modifying `open-all.sh` to reduce panes
- Old sessions keep old pane count
- Must kill and recreate to apply

### Hermes Gateway Not Running

**Problem**: Hermes cron jobs not firing

**Detection**:
```bash
hermes gateway status
# Shows: "✗ Gateway is not running"
```

**Fix**:
```bash
# Start in tmux hermes session
tmux send-keys -t hermes:1.1 "hermes gateway run" Enter

# Verify
hermes gateway status
# Should show: "✓ Gateway is running (PID: ...)"
```

**Permanent fix**: Modified `open-all.sh` to auto-start gateway in hermes:1.1

## Session Control from PM

### Sending Commands to Other Sessions

```bash
# Send to specific pane
tmux send-keys -t bea:1.2 "claude --add-dir ~/project-manager" Enter

# Send to multiple sessions
for session in bea stock insung music; do
  tmux send-keys -t ${session}:1.1 "/hih-clear" Enter
done
```

### Capturing Output from Other Sessions

```bash
# Capture last 30 lines
tmux capture-pane -t bea:1.1 -p -S -30

# Capture entire pane history
tmux capture-pane -t bea:1.1 -p -S -
```

## Session Lifecycle

### Startup
```bash
cd ~/project-manager && ./open-all.sh
```

### Status Check
```bash
tmux list-sessions -F "#{session_name}: #{session_windows} windows, #{window_panes} panes"
```

### Attach to Session
```bash
tmux attach -t PM       # or bea, stock, insung, music, hermes
```

### Cleanup
```bash
# Kill project sessions only (keeps PM, hermes)
./open-all.sh --kill

# Kill all sessions
./open-all.sh --kill-all
```

## Troubleshooting Checklist

- [ ] Session exists: `tmux has-session -t <name>`
- [ ] Correct pane count: `tmux list-panes -t <name>:1 | wc -l`
- [ ] Agent running in pane 1: Check for "Claude>" prompt
- [ ] Gateway running: `hermes gateway status`
- [ ] No Korean/English duplicates: `tmux list-sessions`
- [ ] Script permissions: `ls -l ~/project-manager/open-all.sh`

## Related Files

- `~/project-manager/open-all.sh` - Session creation script
- `~/project-manager/projects.yaml` - Project registry
- `~/.tmux.conf` - tmux configuration (if exists)

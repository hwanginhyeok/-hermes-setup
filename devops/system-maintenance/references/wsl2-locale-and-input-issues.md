# WSL2 Locale and Input Issues

## Korean Input Not Working in tmux

### Symptoms
- Cannot type Korean characters inside tmux sessions
- Input works in normal WSL terminal but fails inside tmux
- Garbled text or characters not appearing when typing Korean

### Root Cause

WSL2 often defaults to `C.UTF-8` locale which supports UTF-8 encoding but lacks Korean locale support. Combined with missing UTF-8 override in tmux configuration, this prevents proper Korean character input.

### Systematic Diagnosis (6-Step Pattern)

**Step 1: tmux Version Check**
```bash
tmux -V
# Expected: tmux 3.4 or higher
```

**Step 2: Current UTF-8 Locale**
```bash
echo $LANG
echo $LC_CTYPE
# Problem: Shows C.UTF-8 (supports UTF-8 but no Korean locale)
# Expected: ko_KR.UTF-8 or en_US.UTF-8
```

**Step 3: System Korean Locale Availability**
```bash
locale -a | grep -i ko
# Problem: Empty output = no Korean locale installed
# Expected: ko_KR.utf8 present
```

**Step 4: tmux.conf UTF-8 Settings**
```bash
cat ~/.tmux.conf | grep -i terminal
# Problem: Missing UTF-8 override line
# Expected: Contains `set -ga terminal-overrides ",*256col*:Tc"`
```

**Step 5: TERM Environment Variable**
```bash
echo $TERM
# Expected: screen-256color or xterm-256color
```

**Step 6: Terminal Type**
```bash
echo $TERM_PROGRAM
echo $WT_SESSION
# Expected: Windows Terminal or compatible
```

### Resolution

**1. Install Korean Locale**
```bash
sudo locale-gen ko_KR.UTF-8
sudo update-locale LANG=ko_KR.UTF-8
```

**2. Set Environment Variables (~/.bashrc)**
```bash
cat >> ~/.bashrc << 'EOF'
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8
export LC_CTYPE=ko_KR.UTF-8
EOF

# Reload
source ~/.bashrc
```

**3. Update tmux Configuration (~/.tmux.conf)**
```bash
# Add these lines (if missing)
set -g default-terminal "screen-256color"
set -ga terminal-overrides ",*256col*:Tc"
set -g default-command "bash"
```

**4. Reload tmux Configuration**
```bash
tmux source-file ~/.tmux.conf
```

**5. Restart tmux Sessions**
```bash
# Exit all tmux sessions
exit

# Reattach to verify
tmux attach -t PM
```

**6. Verify Korean Input**
```bash
# Type some Korean in tmux
echo "한글 입력 테스트"
# Expected: Korean characters display correctly
```

### Expected Diagnostic Results (After Fix)

| Step | Before Fix | After Fix |
|------|-----------|-----------|
| 1. tmux version | tmux 3.4 | tmux 3.4 (unchanged) |
| 2. LANG/LC_CTYPE | C.UTF-8 | ko_KR.UTF-8 |
| 3. Korean locale | ❌ None | ✅ ko_KR.utf8 |
| 4. tmux.conf UTF-8 | ⚠️ Missing | ✅ Override present |
| 5. TERM | screen-256color | screen-256color (unchanged) |
| 6. Terminal | Windows Terminal | Windows Terminal (unchanged) |

### Windows Terminal UTF-8 Encoding

Even with proper WSL locale, Windows Terminal must also be configured for UTF-8:

**Settings → 기본값 (Defaults) → 고급 (Advanced)**
- Ensure UTF-8 encoding is selected
- Or add to Windows Terminal settings.json:
```json
"profiles": {
  "defaults": {
    "encoding": "utf-8"
  }
}
```

### Quick Verification Script

```bash
#!/bin/bash
# Quick Korean input test
echo "한글 입력 테스트"
echo "Current locale: $LANG"
echo "Available Korean locales:"
locale -a | grep -i ko
```

### Common Failure Patterns

**Pattern 1: Locale Installed But Not Active**
```bash
# Symptoms
locale -a | grep ko  # Shows ko_KR.utf8
echo $LANG          # Still shows C.UTF-8

# Fix: Logout and login, or run:
export LANG=ko_KR.UTF-8
```

**Pattern 2: tmux.conf Changes Not Applied**
```bash
# Symptoms
tmux.conf edited but Korean still doesn't work

# Fix: Must reload tmux configuration OR restart sessions
tmux source-file ~/.tmux.conf
# Or fully restart: exit and reattach
```

**Pattern 3: Windows Terminal Override**
```bash
# Symptoms
All WSL locale correct, but Terminal mangles Korean

# Fix: Check Windows Terminal settings for encoding
# Ensure UTF-8 is selected, not legacy codepages
```

### Related Issues

**Unicode Characters in tmux Status Bar**
- If status bar shows garbled Unicode (e.g., arrows, symbols)
- Same UTF-8 override fix applies: `set -ga terminal-overrides ",*256col*:Tc"`

**Korean Font Rendering**
- Characters display but appear as squares/tofu
- Terminal font lacks Korean glyphs
- Fix: Install Noto Sans CJK or use Cascadia Code with Korean support

## Locale Best Practices

### For Korean Users
```bash
# Always set Korean locale as default
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8

# For development tools that require English
# (e.g., some error messages are clearer in English)
# Override per-command:
LANG=C.UTF-8 some-tool
```

### For Multilingual Environments
```bash
# Set English as system locale, support Korean for input
export LANG=en_US.UTF-8
export LC_CTYPE=ko_KR.UTF-8  # Only ctype for character handling
```

### Checking All Locale Categories
```bash
# Show all locale-related environment variables
locale
# Look for any that show "POSIX" or "C" instead of UTF-8
```

## Reference: Locale Category Meanings

| Variable | Purpose | Recommended Value |
|----------|---------|-------------------|
| LANG | Default locale for all categories | ko_KR.UTF-8 |
| LC_ALL | Override all locale categories | ko_KR.UTF-8 (or unset) |
| LC_CTYPE | Character classification and handling | ko_KR.UTF-8 |
| LC_MESSAGES | Language for messages/errors | ko_KR.UTF-8 (optional) |
| LC_TIME | Date/time formatting | ko_KR.UTF-8 (optional) |

**Note**: LC_ALL overrides everything. For fine-grained control, set individual LC_* instead.

## Quick Fix Summary

```bash
# One-liner to fix Korean input in tmux (WSL2)
sudo locale-gen ko_KR.UTF-8 && \
sudo update-locale LANG=ko_KR.UTF-8 && \
echo 'export LANG=ko_KR.UTF-8' >> ~/.bashrc && \
echo 'export LC_ALL=ko_KR.UTF-8' >> ~/.bashrc && \
echo 'export LC_CTYPE=ko_KR.UTF-8' >> ~/.bashrc && \
sed -i '/set -g default-terminal/a set -ga terminal-overrides ",*256col*:Tc"' ~/.tmux.conf && \
tmux source-file ~/.tmux.conf && \
echo "Fix applied. Restart tmux session to take effect."
```

---

## Related Issues

- **tmux copy-paste with Korean**: Ensure clipboard backend supports UTF-8 (OSC 52)
- **Korean filenames**: Always UTF-8, but Windows compatibility may need conversion
- **SSH Korean input**: Both client and server must have UTF-8 locale
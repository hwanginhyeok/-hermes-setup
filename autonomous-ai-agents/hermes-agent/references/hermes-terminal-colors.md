# Hermes Terminal Color Configuration

## User Color Preference

**REQUIRED**: Pure black (#000000) on white backgrounds, NOT dark gray variants.

When setting colors for terminal output, HTML, or any UI elements:
- ✓ **CORRECT**: `#000000` (pure black)
- ✗ **WRONG**: `#222222`, `#333333`, or any gray variant for "black"

## Built-in Skins

Located in `~/.hermes/skins/`

### light-black.yaml (Recommended for this user)

```yaml
name: light-black
description: Bright background with black text for light terminal themes

colors:
  banner_border: "#000000"
  banner_title: "#000000"
  banner_accent: "#333333"
  banner_dim: "#666666"
  banner_text: "#000000"
  ui_accent: "#2563EB"
  ui_label: "#333333"
  ui_ok: "#16A34A"
  ui_error: "#DC2626"
  ui_warn: "#CA8A04"
  prompt: "#000000"
  input_rule: "#CCCCCC"
  response_border: "#000000"
  status_bar_bg: "#F5F5F5"
  status_bar_text: "#000000"
  status_bar_strong: "#000000"
  status_bar_dim: "#666666"
  # ... more colors
```

**Key colors:**
- Primary text: `#000000`
- UI accent: `#2563EB` (blue)
- Success: `#16A34A` (green)
- Error: `#DC2626` (red)

### Personality Color Palettes

Different personalities apply different color schemes on top of skins:

| Personality | Color Palette | Appearance |
|-------------|---------------|------------|
| `kawaii` | Gold + Cornsilk | Yellow/cream tones |
| `default` | Classic Hermes | Gold borders, warm tones |
| Custom | Skin-defined | Uses skin.yaml directly |

**Issue**: `kawaii` personality uses gold/cornsilk even with `light-black` skin.

## Configuring Skin

### Method 1: Edit config.yaml

```yaml
# ~/.hermes/config.yaml
agent:
  skin: light-black
  personality: default  # Remove kawaii if set
```

### Method 2: Use hermes config

```bash
hermes config set agent.skin light-black
hermes config set agent.personality default
```

### Method 3: Slash command (in session)

```
/skin light-black
/personality default
```

**RESTART REQUIRED** after changes:
- CLI: Exit and relaunch `hermes`
- Gateway: `/restart`

## Verifying Color Settings

```bash
# Check current skin/personality
hermes config show | grep -A 5 "agent:"

# List available skins
ls ~/.hermes/skins/

# View skin file contents
cat ~/.hermes/skins/light-black.yaml

# Check if personality is overriding skin
grep personality ~/.hermes/config.yaml
```

## Color Code Reference

### Pure Black Variants (ALWAYS use #000000)

| Code | Name | Use? |
|------|------|------|
| `#000000` | Pure black | ✓ YES (user requirement) |
| `#080808` | Very dark gray | ✗ NO |
| `#1a1a1a` | Dark gray | ✗ NO |
| `#222222` | Medium dark gray | ✗ NO (explicitly rejected) |
| `#333333` | Dark gray | ✗ NO (for accent only, not main text) |

### ANSI Color Codes (Terminal Output)

If setting terminal colors directly:

```bash
# Black text (what user wants)
echo -e "\033[0;30mBlack text\033[0m"

# NOT these grays:
echo -e "\033[0;90mBright black/gray\033[0m"  # Dark gray
echo -e "\033[0;37mWhite\033[0m"               # White background
```

## Common Issues

### Issue: Output still looks yellow after changing skin

**Cause**: `kawaii` personality uses gold/cornsilk colors regardless of skin.

**Fix**:
```bash
hermes config set agent.personality default
# Then restart
```

### Issue: Skin setting not applied

**Cause**: Config not reloaded after change.

**Fix**: Restart Hermes process - config is read at startup only.

### Issue: HTML colors wrong in PFD/web output

**Cause**: Hard-coded color codes in HTML/templates, not using Hermes skin.

**Fix**: Update HTML templates to use `#000000` for black elements, never `#222222`.

**Example**:
```html
<!-- WRONG -->
<div style="color: #222222">Text</div>

<!-- CORRECT -->
<div style="color: #000000">Text</div>
```

## tmux Integration (User Context)

### User's tmux Theme (Dark Mono)

Location: `~/.tmux.conf`

```bash
# Color Palette
bg_main     = #ffffff    # Status bar background (pure white)
bg_active   = #f0f0f0    # Active window tab
fg_dim      = #333333    # Inactive text (dark gray)
fg_mid      = #000000    # Secondary text (pure black)
fg_dark     = #000000    # Primary text (pure black)
accent      = #2563eb    # Point blue
```

**Key colors:**
- Background: `#ffffff` (pure white)
- Main text: `#000000` (pure black)
- Dim text: `#333333` (dark gray)
- Accent: `#2563eb` (blue)

### Recommended Hermes Skins for tmux Dark Mono

| Skin | Background | Text | Accent | Match? |
|------|-----------|------|--------|--------|
| **`daylight`** | Light | Dark (#111827) | Blue (#2563EB) | ✅ Perfect - accent matches |
| `warm-lightmode` | Light | Dark brown (#2C1810) | Brown (#8B4513) | ⚠️ Acceptable - warm tone |
| `mono` | Light | Grayscale | Gray | ⚠️ Acceptable - no accent |
| `light-black` | Light | Pure black (#000000) | Blue (#2563EB) | ✅ Good - custom skin |
| `default` | Dark | Gold/cornsilk | Gold | ❌ Wrong - too yellow |
| `slate` | Dark | Light blue | Blue | ❌ Wrong background |

### Built-in Skin: daylight (Recommended)

The `daylight` skin is designed for light terminals and **perfectly matches the tmux Dark Mono theme**:

```yaml
# From hermes_cli/skin_engine.py - _BUILTIN_SKINS["daylight"]
colors:
  banner_border: "#2563EB"      # Matches tmux accent
  banner_title: "#0F172A"       # Dark blue-gray
  banner_accent: "#1D4ED8"      # Darker blue
  banner_dim: "#475569"         # Medium gray
  banner_text: "#111827"        # Very dark gray (near black)
  ui_accent: "#2563EB"          # Matches tmux accent
  ui_label: "#0F766E"           # Teal
  ui_ok: "#15803D"              # Green
  ui_error: "#B91C1C"           # Red
  ui_warn: "#B45309"            # Orange
  prompt: "#111827"             # Near-black prompt
  input_rule: "#93C5FD"         # Light blue
  response_border: "#2563EB"    # Matches tmux accent
  session_label: "#1D4ED8"      # Dark blue
  session_border: "#64748B"     # Medium gray
```

**Advantages of `daylight` skin:**
- ✅ Accent color (#2563EB) **exactly matches** tmux accent
- ✅ Dark text colors (#111827, #0F172A) readable on white background
- ✅ Built-in (no custom skin file needed)
- ✅ Designed specifically for light terminal backgrounds

**Activation:**
```bash
hermes config set display.skin daylight
# Restart required
```

### Workflow: Match Hermes to tmux

1. **Extract tmux colors:**
   ```bash
   cat ~/.tmux.conf | grep -E "bg=#|fg=#|accent"
   ```

2. **Identify key colors:**
   - Background: white/dark?
   - Primary text: black/white?
   - Accent: which color?

3. **Select matching Hermes skin:**
   - Light bg + dark text → `daylight`, `warm-lightmode`, `mono`
   - Dark bg + light text → `slate`, `default`, `ares`

4. **Update config:**
   ```bash
   hermes config set display.skin daylight
   ```

5. **Restart Hermes:**
   - CLI: Exit and relaunch
   - Gateway: `/restart`

### Example: Fixing Yellow Output in tmux

**Problem**: Hermes output appears yellow in tmux Dark Mono theme.

**Diagnosis:**
```bash
# Check current skin
hermes config show | grep "skin:"
# Output: skin: fantasy (invalid → falls back to default gold)

# Check tmux colors
grep -E "bg=#|fg=#" ~/.tmux.conf
# Output: bg=#ffffff, fg=#000000, accent=#2563eb
```

**Solution:**
```bash
# Change to daylight (matches tmux accent)
hermes config set display.skin daylight

# Restart
exit  # CLI
hermes  # Relaunch
```

**Verification:** Output should now appear with dark text and blue accents, not yellow.

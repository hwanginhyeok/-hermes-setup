# CLI Tool Installation Patterns

## x.ai CLI (Grok)

### Installation

**Linux/WSL:**
```bash
curl -fsSL https://x.ai/cli/install.sh | bash
```

**Windows PowerShell:**
```powershell
iwr -useb https://x.ai/cli/install.ps1 | iex
```

### Verification

```bash
# Check version
grok --version
# Expected: grok 0.2.3 (14d81fd87) or higher

# Inspect current configuration
grok inspect

# List sessions (requires authentication)
grok sessions list

# List available models (requires authentication)
grok models
```

### Installation Details

**Binary locations (Linux/WSL):**
- Download directory: `~/.grok/downloads/`
- Binary directory: `~/.grok/bin/`
- Symlinks: `~/.local/bin/grok`, `~/.local/bin/agent`

**Configuration files:**
- Config: `~/.grok/config.toml`
- Completion: `~/.grok/completions/bash/grok.bash`
- Zsh completion: `~/.grok/completions/zsh/_grok`

### Authentication

**OAuth Browser Flow (Required):**
```bash
grok login
# Opens browser window for OAuth authentication
```

**Authentication flow:**
1. Run `grok login` in terminal
2. Browser opens to x.ai OAuth page
3. Authorize application
4. Token stored in `~/.grok/auth.json`

**Important:**
- **Cannot authenticate headless** - Requires interactive browser session
- OAuth tokens stored locally in `~/.grok/auth.json`
- Token format: `{"scope_url": {"key": "token"}, ...}`
- Supported scopes: OIDC (`https://auth.x.ai::b1a00492-073a-47ea-816f-4c329264a828`) and legacy (`https://accounts.x.ai/sign-in`)

### Common Usage Patterns

**Simple prompt (headless):**
```bash
grok -p "Generate a Python function to sort a list"
```

**Interactive mode:**
```bash
grok
# Starts interactive CLI session
```

**Continue previous session:**
```bash
grok -c
```

**Specify model:**
```bash
grok -m grok-beta "Analyze this data"
```

**Resume specific session:**
```bash
grok -r <SESSION_ID>
```

**With output format (headless only):**
```bash
grok -p "Task" --output-format json
```

### Environment Variables

**Proxy settings:**
```bash
export GROK_PROXY_URL="https://your-proxy.com"
export GROK_CHANNEL="stable"  # or "alpha", "enterprise"
export GROK_BIN_DIR="~/.grok/bin"  # Custom binary directory
```

**OAuth mode:**
```bash
grok --oauth
# Forces OAuth flow even if deployment key configured
```

### Troubleshooting

**Not authenticated error:**
```
You are not authenticated.

Default model: grok-build
```
**Solution:** Run `grok login` in browser-enabled session

**Command not found:**
```bash
# Add to PATH
export PATH="$HOME/.grok/bin:$PATH"

# Or use symlink location
export PATH="$HOME/.local/bin:$PATH"
```

**Login timeout (180s):**
- Occurs in headless environments (no browser access)
- Workaround: Authenticate in GUI terminal, copy `~/.grok/auth.json` to headless environment

**Binary permission denied:**
```bash
chmod +x ~/.grok/bin/grok
```

## Generic CLI Tool Installation Pattern

### Checklist for New CLI Tools

1. **Verify prerequisites:**
   ```bash
   # Check for required dependencies
   which curl wget
   which python3 python
   which node npm
   ```

2. **Install tool:**
   - Download from official source
   - Verify checksum if available
   - Execute installer script

3. **Verify installation:**
   ```bash
   <tool> --version
   <tool> --help
   which <tool>
   ```

4. **Configure PATH:**
   - Add to `~/.bashrc` or `~/.zshrc`
   - Export in current session: `export PATH="$PATH:<tool-path>"`

5. **Authentication (if required):**
   - Check authentication method (API key, OAuth, token file)
   - Test basic command without authentication
   - Complete authentication flow
   - Verify credentials work

6. **Test basic functionality:**
   ```bash
   <tool> <basic-command>
   ```

### Common Installation Issues

**Permission denied on installation:**
```bash
# Use sudo carefully (only for system-wide tools)
sudo <install-command>

# Or install to user directory
curl -fsSL <url> | bash -s -- --install-dir ~/.local
```

**Network issues during download:**
```bash
# Use alternative mirror
export CDN=https://mirror.example.com
curl -fsSL <url> | bash

# Or download manually
curl -fLO <download-url>
sh <downloaded-file>
```

**Installation script blocked:**
```bash
# Download script first, review, then execute
curl -fsSL <url> -o install.sh
less install.sh  # Review
bash install.sh
```

## References

- [x.ai CLI GitHub](https://github.com/xai-org/grok)
- [x.ai CLI Documentation](https://docs.x.ai/cli)
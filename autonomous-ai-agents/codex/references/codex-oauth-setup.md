# Codex OAuth Authentication

Codex CLI requires OAuth authentication before use. This is NOT an environment issue - it's a deliberate security design by OpenAI.

## Authentication Steps

### 1. Device Auth (Recommended)

```bash
codex login --device-auth
```

**Process:**
1. Command outputs a URL and a one-time code (15-minute expiry)
2. Open URL in browser: https://auth.openai.com/codex/device
3. Enter the code
4. Sign in to ChatGPT account
5. Authorize Codex CLI access

**Example output:**
```
Welcome to Codex [v0.130.0]
OpenAI's command-line coding agent

Follow these steps to sign in with ChatGPT using device code authorization:

1. Open this link in your browser and sign in to your account
   https://auth.openai.com/codex/device

2. Enter this one-time code (expires in 15 minutes)
   ZE1A-OJB5H

Device codes are a common phishing target. Never share this code.
```

### 2. Verify Login

```bash
codex login status
```

**Success output:**
```
Logged in as <email>@openai.com
```

**Failure output:**
```
Not logged in
```

### 3. Test Authentication

```bash
codex exec "print('hello')"
```

Should execute successfully and output `hello`.

## Common Issues

### 401 Unauthorized

**Error:**
```
ERROR: unexpected status 401 Unauthorized
ERROR: Missing bearer or basic authentication in header
```

**Cause:** Not logged in or token expired

**Fix:**
```bash
codex login --device-auth
```

### Command Timed Out

**Cause:** OAuth not completed before command execution

**Fix:** Complete browser authorization before running commands

### Session Files Location

OAuth state stored in:
```
~/.codex/
├── state_5.sqlite
├── logs_2.sqlite
└── sessions/
```

**Note:** Session files are separate from OpenAI API keys (OPENAI_API_KEY env var does NOT help with Codex CLI)

## Alternative: API Key Method

If you have an OpenAI API key:

```bash
echo "sk-..." | codex login --with-api-key
```

However, device auth is preferred for interactive use.

## For Hermes Agent Integration

When using Codex via Hermes skill, authentication is separate from Hermes LLM configuration:

- **Hermes LLM**: Configured via `~/.hermes/config.yaml` (model/provider)
- **Codex CLI**: Requires separate OAuth via `codex login`

This means even if Hermes is configured to use OpenAI, Codex CLI still needs its own login.

## Troubleshooting

### Login hangs

**Issue:** Browser doesn't open automatically

**Fix:** Copy URL and code manually to browser

### Login fails after completing

**Issue:** Network issue or server error

**Fix:** Check internet connection, try `codex logout` then login again

### Multiple accounts

**Issue:** Need to switch accounts

**Fix:**
```bash
codex logout
codex login --device-auth
```
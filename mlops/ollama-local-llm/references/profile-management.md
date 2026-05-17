# Hermes Profile Management

**Last Updated**: 2026-05-05

## Overview

Hermes supports multiple configuration profiles, each with independent model settings. Profiles override the global config.

## Config Hierarchy (Priority Order)

1. **Profile config** (`~/.hermes/profiles/<name>/config.yaml`) - HIGHEST
2. **Global config** (`~/.hermes/config.yaml`) - Default
3. **Fallback model** - Emergency fallback

## Common Scenarios

### "Why is my model different?"

**Symptom**: Global config shows `provider: ollama`, but session uses `glm-4.6`

**Cause**: Active profile overrides global config

**Diagnosis**:
```bash
# Check for profiles
ls -la ~/.hermes/profiles/

# If any exist, check their config
cat ~/.hermes/profiles/<name>/config.yaml | grep -A2 "model:"
```

**Solutions**:
- **Option 1**: Delete profile to use global config
  ```bash
  rm -rf ~/.hermes/profiles/<name>
  ```

- **Option 2**: Modify profile config
  ```bash
  nano ~/.hermes/profiles/<name>/config.yaml
  # Change provider to desired value
  ```

- **Option 3**: Use `--profile` flag to explicitly select
  ```bash
  hermes --profile default chat  # Force use global config
  ```

### Creating a Profile

```bash
# Method 1: Via CLI (if supported)
hermes profile create myprofile

# Method 2: Manually
mkdir -p ~/.hermes/profiles/myprofile
cp ~/.hermes/config.yaml ~/.hermes/profiles/myprofile/
# Edit the copy as needed
```

### Listing Profiles

```bash
ls ~/.hermes/profiles/
```

Each subdirectory is a profile.

### Switching Profiles

Hermes automatically uses the first profile found (alphabetical). To control which profile is active:

1. **Delete all profiles** to use global config
2. **Rename profile** to control priority: `mv ~/.hermes/profiles/z-profile ~/.hermes/profiles/a-profile`
3. **Use CLI flag** (if available): `hermes --profile <name>`

## Profile Config Structure

A profile config is a complete `config.yaml`:

```yaml
# ~/.hermes/profiles/myprofile/config.yaml
model:
  provider: zai-glm
  default: glm-4.6

custom_providers:
  - name: zai-glm
    base_url: https://api.z.ai/api/anthropic
    key_env: Z_AI_API_KEY
    api_mode: anthropic_messages

# ... all other settings from global config
```

**Note**: Profiles inherit NOTHING from global config. They must be complete config files.

## When to Use Profiles

✅ **Good use cases**:
- Different projects need different models
- Testing a new config without breaking global setup
- Team environments with shared profiles

❌ **Avoid when**:
- You just want to change providers temporarily (use `--provider` flag instead)
- You're not sure which config is active (causes confusion)

## Troubleshooting

### "I can't tell which config is being used"

```bash
# Check for profiles first
ls ~/.hermes/profiles/

# If profiles exist, check their model setting
cat ~/.hermes/profiles/*/config.yaml | grep -A2 "model:"

# Compare with global
grep -A2 "model:" ~/.hermes/config.yaml
```

### "Deleted profile but still using wrong model"

Check session cache:
```bash
# Clear Hermes cache
rm -rf ~/.hermes/cache/

# Restart Hermes session
```

### "Want to copy global config to profile"

```bash
# Create profile from global
mkdir -p ~/.hermes/profiles/myprofile
cp ~/.hermes/config.yaml ~/.hermes/profiles/myprofile/

# Then edit the profile as needed
nano ~/.hermes/profiles/myprofile/config.yaml
```

## Quick Reference

| Action | Command |
|--------|---------|
| List profiles | `ls ~/.hermes/profiles/` |
| View profile config | `cat ~/.hermes/profiles/<name>/config.yaml` |
| Delete profile | `rm -rf ~/.hermes/profiles/<name>` |
| Copy global to profile | `cp ~/.hermes/config.yaml ~/.hermes/profiles/<name>/` |
| View global config | `cat ~/.hermes/config.yaml` |

## Related References

- `references/zai-glm-provider.md` - Z.AI provider config
- `references/hermes-troubleshooting.md` - Complete Hermes troubleshooting
- `templates/hermes-config.yaml` - Config template

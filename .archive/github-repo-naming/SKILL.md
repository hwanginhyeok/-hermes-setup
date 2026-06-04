---
name: github-repo-naming
description: GitHub repository naming conflicts and resolution strategies. Common issues with reserved names, hyphen prefixes, and backup naming conventions.
---

# GitHub Repository Naming Pitfalls

## Issue

**Repository naming conflict with hyphen prefix:**
- Desired: `hermes-setup`
- Actual: `-hermes-setup` (hyphen prefix required)

## Root Cause

GitHub reserved naming conflicts when certain names are already taken.

## Resolution

1. **Accept hyphen prefix:**
   ```bash
   git remote add origin https://github.com/hwanginhyeok/-hermes-setup.git
   ```

2. **Document clearly in README:**
   ```markdown
   # Hermes Setup Repository
   
   **Repository:** https://github.com/hwanginhyeok/-hermes-setup
   
   **Note:** Hyphen prefix required due to naming conflicts.
   ```

3. **Update documentation:**
   - Clone instructions include hyphen prefix
   - All references use full name with prefix

## Best Practices

1. **Check availability first:**
   ```bash
   curl -s "https://api.github.com/users/$(git config user.name)/repos" | jq -r '.[].name'
   ```

2. **Have backup names ready:**
   - Primary: `hermes-setup`
   - Backup 1: `-hermes-setup`
   - Backup 2: `hermes-setup-v2`

3. **Document naming decisions:**
   - Add comment in README
   - Update setup scripts
   - Notify team of actual vs intended names

## Session Context

**2026-05-17 PM Session:**
- Attempted to create `hermes-setup`
- GitHub automatically added hyphen prefix
- Repository: https://github.com/hwanginhyeok/-hermes-setup
- Status: ✅ Accepted and documented
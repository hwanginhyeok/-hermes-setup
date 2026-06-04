# Gmail Setup for Hermes Agent Integration

## Quick Setup Pattern

This is the fastest way to configure Gmail for Hermes Agent cronjob notifications, reports, and automated alerts.

### Prerequisites

1. Gmail account with 2-Step Verification enabled
2. Google App Password (16-character password)

### Generate App Password

1. Go to https://myaccount.google.com/apppasswords
2. Select app: "Mail" → Device: "Other (Custom name)"
3. Enter name: "Hermes Agent WSL"
4. Click "Generate"
5. Copy the 16-character password (format: `abcd efgh ijkl mnop`)
6. **Remove spaces** for .netrc file: `abcdefghijklmn`

### Configuration Files

**Step 1: Create Himalaya config**

```bash
mkdir -p ~/.config/himalaya
cat > ~/.config/himalaya/config.toml << 'EOF'
# Gmail IMAP/SMTP Configuration for Hermes Agent
# Account: your-email@gmail.com

[email_accounts.your_account]
email = "your-email@gmail.com"

# IMAP settings
imap-host = "imap.gmail.com"
imap-port = 993
imap-starttls = false  # SSL/TLS

# SMTP settings
smtp-host = "smtp.gmail.com"
smtp-port = 465
smtp-starttls = false  # SSL/TLS

# Default account
default = "your_account"
EOF
```

**Step 2: Store credentials securely**

```bash
# Replace YOUR_EMAIL and YOUR_APP_PASSWORD_NO_SPACES
cat > ~/.netrc << EOF
machine imap.gmail.com login YOUR_EMAIL@gmail.com password YOUR_APP_PASSWORD_NO_SPACES
machine smtp.gmail.com login YOUR_EMAIL@gmail.com password YOUR_APP_PASSWORD_NO_SPACES
EOF
chmod 600 ~/.netrc
```

**Step 3: Verify installation**

```bash
# Check Himalaya version
source ~/.cargo/env && himalaya --version

# Test email connection
himalaya envelope list --account your_account
```

## Use Cases

Once configured, Himalaya can be used for:

1. **Cronjob failure alerts**: Send email when cronjobs fail
2. **Daily/weekly reports**: Automated report delivery
3. **Emergency notifications**: Production issue alerts
4. **Email-based commands**: Receive and process emails via cron

## Integration with Cronjobs

**Example: Send cronjob report via email**

```python
import subprocess

def send_email_report(subject, body, recipient):
    """Send email using Himalaya"""
    message = f"""From: your-email@gmail.com
To: {recipient}
Subject: {subject}

{body}
"""
    
    subprocess.run(
        ["himalaya", "template", "send"],
        input=message,
        text=True,
        capture_output=True
    )
```

## Troubleshooting

### Authentication failed

**Error**: `Authentication failed [EMAIL]`

**Solution**:
1. Verify 2-Step Verification is enabled
2. Regenerate App Password
3. Check .netrc has correct permissions (chmod 600)
4. Ensure no spaces in App Password in .netrc

### IMAP/SMTP connection errors

**Error**: `Could not connect to server`

**Solution**:
1. Check internet connectivity
2. Verify imap.gmail.com and smtp.gmail.com are reachable
3. Ensure ports 993 (IMAP) and 465 (SMTP) are not blocked

### Email not sending

**Error**: No error but email not received

**Solution**:
1. Check Gmail "Sent" folder via web UI
2. Verify recipient email address is correct
3. Check spam folder at recipient
4. Ensure Gmail account has sufficient sending quota

## Security Notes

- **Never commit .netrc to version control**
- **Use App Passwords, not account password**
- **Restrict App Password to Mail only**
- **Rotate App Passwords periodically (every 90 days)**
- **Monitor Gmail account for unauthorized access**

## References

- Himalaya Documentation: https://github.com/pimalaya/himalaya
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
- IMAP/SMTP Settings: https://support.google.com/mail/answer/7126229

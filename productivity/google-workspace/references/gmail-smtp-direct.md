# Gmail SMTP via Python smtplib

Quick send-only Gmail delivery without OAuth or CLI tools. Best for:
- Automated reports/alerts from cronjobs
- Simple notification systems
- Headless servers

## Prerequisites

1. Gmail account with 2-factor authentication enabled
2. App Password (not account password)
   - Google Account → Security → 2-Step Verification → App passwords
   - Generate new app password → Copy the 16-character code
   - Format: `xxxx xxxx xxxx xxxx` (spaces included)

## Code Template

```python
import smtplib
from email.message import EmailMessage

# SMTP Configuration
smtp_host = "smtp.gmail.com"
smtp_port = 465  # SSL
email_address = "your@gmail.com"
app_password = "xxxx xxxx xxxx xxxx"  # Include spaces!

def send_email(to_address, subject, body, html=False):
    """Send email via Gmail SMTP."""
    msg = EmailMessage()
    
    if html:
        msg.set_content(body, subtype='html')
    else:
        msg.set_content(body)
    
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = to_address
    
    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(email_address, app_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send: {e}")
        return False

# Usage
send_email(
    to_address="recipient@example.com",
    subject="Report: Daily Summary",
    body="Line 1\nLine 2\nLine 3"
)

# HTML email
send_email(
    to_address="recipient@example.com",
    subject="Report: Daily Summary",
    body="<h1>Daily Summary</h1><p>Stats: <strong>123</strong></p>",
    html=True
)
```

## Business Email (Gintlab/Workspace)

Business Gmail accounts (e.g., `user@gintlab.com`) hosted on Google Workspace
use the same SMTP settings:

```python
# Works for both personal@gmail.com and user@company.com
smtp_host = "smtp.gmail.com"
smtp_port = 465
email_address = "user@company.com"  # Business address
app_password = "xxxx xxxx xxxx xxxx"  # Generated from business account
```

**Note**: Some organizations block external App Password generation. If IT policy
prevents App Password creation, you'll need to use the full OAuth flow
(see `google-workspace` skill) or ask IT administrator to enable SMTP relay.

**User Configuration (2026-06-01)**:
- Personal Gmail: `dlsgur5560@gmail.com` (App Password: `vkqf shay deop qygf`)
- Business Gintlab: `inhyeok.hwang@gintlab.com` (tested successfully via SMTP)
- Test confirmation: Both addresses can send via smtplib with SSL port 465
- App Password source: Located in `/home/gint_pcd/projects/주식부자프로젝트/.env` as `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD`

## Testing Connection

```python
import smtplib

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
        server.ehlo()
        print("✅ SMTP server reachable")
except Exception as e:
    print(f"❌ Cannot reach SMTP server: {e}")
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Authentication failed` | Wrong password or 2FA not enabled | Verify App Password (includes spaces), enable 2FA |
| `Less secure app not supported` | Using account password instead of App Password | Generate App Password from Google Security settings |
| `Connection timeout` | Firewall or network issue | Check if port 465 is blocked |
| `Sender address rejected` | IT policy blocks external senders | Use OAuth or ask IT to allow SMTP relay |

## Comparison: smtplib vs Himalaya vs google-workspace

| Feature | smtplib | Himalaya | google-workspace (OAuth) |
|---------|---------|----------|---------------------------|
| Setup time | 2 min | 10-15 min | 15-20 min |
| Dependencies | Python only | Rust/Cargo | Python + OAuth setup |
| Capabilities | Send only | Send + read + search | Full Gmail + Calendar + Drive |
| Good for | Alerts, reports | Email workflows | Multi-service integration |
| Business email | ✅ (if App Password allowed) | ✅ | ✅ (always works) |

## When to Use Each

- **smtplib**: Automated reports, cronjob notifications, simple send-only needs
- **Himalaya**: Interactive email management, reading/searching Gmail
- **google-workspace**: Need Calendar/Drive/Sheets integration or full Workspace access

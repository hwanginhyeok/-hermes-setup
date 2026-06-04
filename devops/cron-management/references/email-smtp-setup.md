# Email SMTP Setup for Hermes Cron Notifications

## Overview

Hermes cronjobs can deliver results via email. This guide covers SMTP setup for Gmail-based services.

## Configuration Pattern

### SMTP Settings (Gmail)

**Server:**
- Host: `smtp.gmail.com`
- Port: `465` (SSL)
- Authentication: App Password (2FA required)

### Setup Steps

1. **Generate App Password**
   - Google Account → Security → 2-Step Verification
   - App Passwords → Generate (name: "Hermes Agent")
   - Format: `xxxx xxxx xxxx xxxx` (16 characters, spaces included)

2. **Store Credentials Securely**
   ```bash
   mkdir -p ~/.config/gmail
   chmod 700 ~/.config/gmail
   
   # Create .env file
   cat > ~/.config/gmail/.env << 'EOF'
   GMAIL_ADDRESS=your_email@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   EOF
   
   chmod 600 ~/.config/gmail/.env
   ```

3. **Test SMTP Connection**
   ```python
   import smtplib
   from email.message import EmailMessage
   
   gmail_user = "your_email@gmail.com"
   gmail_password = "xxxx xxxx xxxx xxxx"  # App Password with spaces
   
   msg = EmailMessage()
   msg.set_content("Test email from Hermes Agent")
   msg['Subject'] = 'SMTP Test'
   msg['From'] = gmail_user
   msg['To'] = gmail_user
   
   with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
       server.login(gmail_user, gmail_password)
       server.send_message(msg)
   ```

## Enterprise Email (Gintlab Example)

### Corporate Gmail Detection

**Test server connectivity:**
```python
import smtplib

# Test common SMTP servers
servers = [
    ("smtp.gmail.com", 465),    # Gmail-based
    ("smtp.office365.com", 587), # Microsoft Exchange
    ("mail.company.com", 587),   # Self-hosted
]

for host, port in servers:
    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=5) as server:
                server.ehlo()
                print(f"✅ {host}:{port} (SSL)")
                break
        else:
            with smtplib.SMTP(host, port, timeout=5) as server:
                server.starttls()
                print(f"✅ {host}:{port} (STARTTLS)")
                break
    except Exception as e:
        print(f"❌ {host}:{port} - {e}")
```

### Enterprise Configuration (inhyeok.hwang@gintlab.com)

**Verified Settings (2026-06-01):**
- Email: `inhyeok.hwang@gintlab.com`
- SMTP: `smtp.gmail.com:465` (SSL)
- Backend: Gmail-based corporate email
- Authentication: Same as personal Gmail (App Password)

**Test Result:** ✅ Email delivery successful

### Sending Pattern

```python
def send_email_notification(recipient, subject, body):
    """Send email notification via Gmail SMTP"""
    import smtplib
    from email.message import EmailMessage
    import os
    
    # Load credentials from environment
    gmail_user = os.getenv('GMAIL_ADDRESS')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = recipient
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
```

## Cronjob Email Integration

### Configure Deliver Target

When creating a cronjob, specify email delivery:

```python
cronjob(
    action="create",
    name="Daily Status Report",
    schedule="0 9 * * 1-5",
    deliver="inhyeok.hwang@gintlab.com",  # Email delivery
    prompt="Generate daily status report and send via email"
)
```

### Multiple Recipients

For multiple recipients, use comma-separated values or implement custom delivery logic in the cronjob prompt.

## Security Best Practices

1. **Never commit credentials** to git
2. **Use App Passwords**, not account passwords
3. **Set file permissions**: `chmod 600 ~/.config/gmail/.env`
4. **Rotate passwords** quarterly
5. **Monitor delivery failures** in cron logs

## Troubleshooting

### Common Errors

**Authentication Error:**
```
smtplib.SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```
- Solution: Verify App Password is correct (include spaces)
- Solution: Ensure 2FA is enabled on Google Account

**Connection Timeout:**
```
timeout: timed out
```
- Solution: Check network connectivity
- Solution: Verify SMTP server and port

**Relay Denied (Corporate):**
```
550 5.7.1 Relaying not permitted
```
- Solution: Contact IT admin for SMTP relay whitelist
- Solution: Use corporate VPN if required

## Reference Implementation

Full script: `scripts/email-smtp-test.py`

```python
#!/usr/bin/env python3
"""Test email SMTP connection and delivery"""

import smtplib
import os
from email.message import EmailMessage
from pathlib import Path

def test_smtp_connection(
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 465,
    email_address: str = None,
    app_password: str = None
):
    """Test SMTP connection and send test email"""
    
    if not email_address or not app_password:
        print("❌ Email address and app password required")
        return False
    
    msg = EmailMessage()
    msg.set_content("SMTP connection test successful!")
    msg['Subject'] = 'SMTP Test Email'
    msg['From'] = email_address
    msg['To'] = email_address
    
    try:
        print(f"Testing {smtp_host}:{smtp_port}...")
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(email_address, app_password)
            server.send_message(msg)
        print("✅ Email sent successfully")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    # Load from environment or arguments
    email = os.getenv('GMAIL_ADDRESS') or (sys.argv[1] if len(sys.argv) > 1 else None)
    password = os.getenv('GMAIL_APP_PASSWORD') or (sys.argv[2] if len(sys.argv) > 2 else None)
    
    test_smtp_connection(email_address=email, app_password=password)
```

## Related Documentation

- [Himalaya CLI Configuration](../email/himalaya/SKILL.md) - Terminal email client
- [Cronjob Management](./cron-management/SKILL.md) - Job scheduling and monitoring

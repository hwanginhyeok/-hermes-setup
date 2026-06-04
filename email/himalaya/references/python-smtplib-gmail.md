# Python smtplib Gmail Setup (Simple Alternative to Himalaya)

**When to use this**: When you only need to SEND emails (not read/manage them) and want a simpler, more reliable approach than Himalaya CLI configuration.

## Why This Over Himalaya?

- ✅ **No configuration files**: No TOML, no .netrc management
- ✅ **No external dependencies**: Uses Python standard library
- ✅ **Simpler debugging**: Python tracebacks vs RUST_LOG
- ✅ **Cross-platform**: Works anywhere Python runs
- ✅ **Easier error handling**: Full exception control

## Quick Setup

### Prerequisites

1. Gmail account with 2-Step Verification enabled
2. Google App Password (16-character password)

### Generate App Password

1. Go to https://myaccount.google.com/apppasswords
2. Select app: "Mail" → Device: "Other (Custom name)"
3. Enter name: "Hermes Agent WSL"
4. Click "Generate"
5. Copy the 16-character password (format: `abcd efgh ijkl mnop`)

### Environment Variables (Recommended)

```bash
# Add to ~/.bashrc or ~/.zshrc
export GMAIL_ADDRESS="your-email@gmail.com"
export GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"  # App Password WITH spaces

# Source the file
source ~/.bashrc
```

## Basic Usage

### Simple Send Function

```python
import smtplib
from email.message import EmailMessage
import os

def send_email(subject, body, to_email, from_email=None):
    """Send email via Gmail SMTP (SSL)"""
    
    # Load credentials from environment (recommended)
    email_address = from_email or os.environ.get("GMAIL_ADDRESS")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if not email_address or not app_password:
        raise ValueError("GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables must be set")
    
    # SMTP settings
    smtp_host = "smtp.gmail.com"
    smtp_port = 465
    
    # Create message
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = to_email
    
    # Send via SMTP SSL
    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(email_address, app_password)
            server.send_message(msg)
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        return False

# Example usage
send_email(
    subject="Test Email from Hermes Agent",
    body="This is a test email sent via Python smtplib.",
    to_email="recipient@example.com"
)
```

### Send HTML Email

```python
from email.message import EmailMessage

def send_html_email(subject, html_body, to_email):
    """Send HTML email via Gmail SMTP"""
    
    msg = EmailMessage()
    msg.set_content(html_body, subtype='html')
    msg['Subject'] = subject
    msg['From'] = os.environ["GMAIL_ADDRESS"]
    msg['To'] = to_email
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ["GMAIL_ADDRESS"], os.environ["GMAIL_APP_PASSWORD"])
        server.send_message(msg)

# Example
html_content = """
<html>
  <body>
    <h1>Daily Report</h1>
    <p><strong>Status:</strong> ✅ All systems operational</p>
    <ul>
      <li>Cronjobs: 9 running</li>
      <li>Errors: 0</li>
    </ul>
  </body>
</html>
"""

send_html_email(
    subject="Daily System Report",
    html_body=html_content,
    to_email="recipient@example.com"
)
```

### Send Email with Attachment

```python
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

def send_email_with_attachment(subject, body, to_email, attachment_path):
    """Send email with file attachment"""
    
    msg = MIMEMultipart()
    msg['From'] = os.environ["GMAIL_ADDRESS"]
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Add body
    msg.attach(MIMEText(body, 'plain'))
    
    # Add attachment
    with open(attachment_path, 'rb') as f:
        part = MIMEApplication(f.read(), Name=osp.basename(attachment_path))
    
    part['Content-Disposition'] = f'attachment; filename="{osp.basename(attachment_path)}"'
    msg.attach(part)
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ["GMAIL_ADDRESS"], os.environ["GMAIL_APP_PASSWORD"])
        server.send_message(msg)

# Example
send_email_with_attachment(
    subject="Weekly Report Attached",
    body="Please find the weekly report attached.",
    to_email="recipient@example.com",
    attachment_path="/path/to/report.pdf"
)
```

## Cronjob Integration

### Daily Cronjob Report Script

```python
#!/usr/bin/env python3
"""Send cronjob status report via email"""

import smtplib
from email.message import EmailMessage
import subprocess
import os
from datetime import datetime

def get_cronjob_status():
    """Get cronjob execution status via hermes cronjob tool"""
    result = subprocess.run(
        ["hermes", "cronjob", "list"],
        capture_output=True,
        text=True
    )
    return result.stdout

def send_report(status_text):
    """Send status report via email"""
    msg = EmailMessage()
    msg.set_content(status_text)
    msg['Subject'] = f"Hermes Cronjob Daily Report - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = os.environ["GMAIL_ADDRESS"]
    msg['To'] = os.environ["GMAIL_ADDRESS"]
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(os.environ["GMAIL_ADDRESS"], os.environ["GMAIL_APP_PASSWORD"])
            server.send_message(msg)
        print("✅ Daily report sent successfully")
    except Exception as e:
        print(f"❌ Failed to send report: {e}")

if __name__ == "__main__":
    status = get_cronjob_status()
    send_report(status)
```

### Cronjob Entry

```bash
# Add to crontab: crontab -e
0 9 * * * /usr/bin/python3 /path/to/daily_report.py >> /tmp/cron_report.log 2>&1
```

## Error Handling

### Common Errors and Solutions

```python
import smtplib
from smtplib import SMTPAuthenticationError, SMTPException

def send_email_with_retry(subject, body, to_email, max_retries=3):
    """Send email with retry logic"""
    
    for attempt in range(max_retries):
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = os.environ["GMAIL_ADDRESS"]
            msg['To'] = to_email
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(os.environ["GMAIL_ADDRESS"], os.environ["GMAIL_APP_PASSWORD"])
                server.send_message(msg)
            
            print(f"✅ Email sent on attempt {attempt + 1}")
            return True
            
        except SMTPAuthenticationError:
            print("❌ Authentication failed - check App Password")
            return False
        except smtplib.SMTPServerDisconnected:
            print(f"⚠️ Server disconnected, retrying... (attempt {attempt + 1}/{max_retries})")
            time.sleep(2 ** attempt)  # Exponential backoff
        except SMTPException as e:
            print(f"❌ SMTP error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    print(f"❌ Failed after {max_retries} attempts")
    return False
```

## Security Best Practices

### ✅ DO: Use Environment Variables

```python
# Load from environment (recommended)
app_password = os.environ.get("GMAIL_APP_PASSWORD")
```

### ❌ DON'T: Hardcode Credentials

```python
# NEVER do this in production code
app_password = "abcd efgh ijkl mnop"
```

### ✅ DO: Use Keyring for Added Security

```bash
# Install keyring
pip install keyring

# Store password securely
keyring set gmail your-email@gmail.com
# (enter App Password when prompted)

# Retrieve in Python
import keyring
app_password = keyring.get_password("gmail", "your-email@gmail.com")
```

### ✅ DO: Validate Email Addresses

```python
import re

def is_valid_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Usage
if not is_valid_email(to_email):
    raise ValueError(f"Invalid email address: {to_email}")
```

## Testing

### Test Email Function

```python
def test_email_connection():
    """Test email connection without sending"""
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(os.environ["GMAIL_ADDRESS"], os.environ["GMAIL_APP_PASSWORD"])
            print("✅ Email connection test successful")
            return True
    except Exception as e:
        print(f"❌ Email connection test failed: {e}")
        return False

# Run test
if test_email_connection():
    print("Ready to send emails!")
```

### Send Test Email

```python
if __name__ == "__main__":
    # Test configuration
    if not os.environ.get("GMAIL_ADDRESS") or not os.environ.get("GMAIL_APP_PASSWORD"):
        print("❌ GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables must be set")
    else:
        send_email(
            subject="Hermes Agent Email Test",
            body="This is a test email from Hermes Agent via Python smtplib.",
            to_email=os.environ["GMAIL_ADDRESS"]
        )
```

## Comparison with Himalaya

| Aspect | Himalaya CLI | Python smtplib |
|---------|-------------|-----------------|
| **Configuration** | TOML + .netrc | Environment variables |
| **Dependencies** | Rust binary | Python stdlib |
| **Send emails** | ✅ | ✅ |
| **Read emails** | ✅ | ❌ (requires IMAP library) |
| **Search emails** | ✅ | ❌ |
| **Manage folders** | ✅ | ❌ |
| **Error handling** | Exit codes | Full Python exceptions |
| **Debugging** | RUST_LOG | Python tracebacks |
| **Learning curve** | Higher | Lower |

## When to Use Each

**Use Python smtplib when:**
- Only sending emails (no reading needed)
- Simple automated notifications
- Cronjob alerts/reports
- Minimum dependency overhead
- You prefer Python over CLI tools

**Use Himalaya when:**
- Full email client features needed
- Interactive email management
- Multiple email accounts
- Complex email workflows
- Terminal-based email workflow

## Troubleshooting

### "Authentication failed"

**Cause**: Incorrect App Password or 2-Step Verification not enabled

**Solution**:
1. Verify 2-Step Verification is enabled
2. Regenerate App Password
3. Check environment variables are set correctly
4. Ensure App Password includes spaces when stored

### "Connection refused"

**Cause**: Firewall blocking port 465 or network issue

**Solution**:
1. Check internet connectivity
2. Verify port 465 is not blocked
3. Try with TLS (port 587) instead:

```python
# Alternative: STARTTLS on port 587
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(email_address, app_password)
    server.send_message(msg)
```

### "Less secure app" error

**Cause**: Google security blocking access

**Solution**:
1. Ensure you're using App Password, not account password
2. Allow less secure apps (deprecated - use App Password instead)
3. Check Google Account security alerts

## Configuration Reuse Patterns

### Reuse from Existing Projects

When setting up email for a new project, check if other projects already have Gmail credentials configured:

```bash
# Find Gmail credentials in other projects
grep -r "GMAIL_APP_PASSWORD" ~/projects/*/ 2>/dev/null

# Example: Found in 주식부자프로젝트/.env
# GMAIL_ADDRESS=dlsgur5560@gmail.com
# GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
```

Then reference those credentials in your new project:

```python
import os
from pathlib import Path

# Load credentials from existing project .env
stock_project = Path.home() / "projects" / "주식부자프로젝트"
env_file = stock_project / ".env"

if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)
    gmail_user = os.getenv("GMAIL_ADDRESS")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    # Now use these for sending emails
```

### Business/Work Email (Organization Email)

Many organizations use Gmail for business email (e.g., `user@company.com`). These work exactly like personal Gmail:

```python
# Business email works identically to personal Gmail
business_email = "user@company.com"  # Gmail-based business email
# Use same SMTP settings: smtp.gmail.com:465 with SSL
```

**Testing business email connectivity:**

```python
import smtplib
import subprocess
from email.message import EmailMessage

def test_business_email(email_address):
    """Test if business email can send via Gmail SMTP"""
    smtp_servers = [
        ("smtp.gmail.com", 465),      # Gmail-based
        ("smtp.office365.com", 587),  # Microsoft Exchange
    ]
    
    for smtp_host, smtp_port in smtp_servers:
        try:
            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=5) as server:
                    server.ehlo()
                    print(f"✅ {smtp_host}:{smtp_port} connection successful")
                    return smtp_host, smtp_port
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=5) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    print(f"✅ {smtp_host}:{smtp_port} connection successful")
                    return smtp_host, smtp_port
        except Exception as e:
            print(f"❌ {smtp_host}:{smtp_port} failed: {e}")
            continue
    
    return None, None

# Test email delivery
def send_test_email(from_email, to_email, app_password):
    """Send test email to verify business email connectivity"""
    msg = EmailMessage()
    msg.set_content(f"Test email from {from_email} to {to_email}")
    msg['Subject'] = 'Business Email Connection Test'
    msg['From'] = from_email
    msg['To'] = to_email
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, app_password)
            server.send_message(msg)
        print(f"✅ Test email sent to {to_email}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
```

**Common business email patterns:**

| Organization | Email Pattern | SMTP Backend |
|-------------|--------------|--------------|
| Google Workspace | `user@company.com` | smtp.gmail.com:465 (SSL) |
| Microsoft 365 | `user@company.com` | smtp.office365.com:587 (STARTTLS) |
| Custom SMTP | `user@company.com` | Custom SMTP server |

### Multiple Email Accounts

When working with multiple email accounts (personal + business):

```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class EmailConfig:
    """Email account configuration"""
    address: str
    app_password: str
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465

# Load multiple accounts
class EmailManager:
    def __init__(self):
        self.accounts = {}
        self._load_accounts()
    
    def _load_accounts(self):
        """Load email accounts from environment or config"""
        # Personal email (from 주식부자프로젝트)
        personal_config = self._load_from_project(
            "주식부자프로젝트",
            "GMAIL_ADDRESS",
            "GMAIL_APP_PASSWORD"
        )
        if personal_config:
            self.accounts["personal"] = personal_config
        
        # Business email
        business_addr = os.getenv("BUSINESS_EMAIL")
        business_pass = os.getenv("BUSINESS_APP_PASSWORD")
        if business_addr and business_pass:
            self.accounts["business"] = EmailConfig(
                address=business_addr,
                app_password=business_pass
            )
    
    def _load_from_project(self, project_name: str, addr_key: str, pass_key: str) -> Optional[EmailConfig]:
        """Load credentials from existing project .env file"""
        try:
            from dotenv import load_dotenv
            from pathlib import Path
            
            project_path = Path.home() / "projects" / project_name
            env_file = project_path / ".env"
            
            if env_file.exists():
                load_dotenv(env_file)
                addr = os.getenv(addr_key)
                password = os.getenv(pass_key)
                
                if addr and password:
                    return EmailConfig(address=addr, app_password=password)
        except Exception as e:
            print(f"Failed to load from {project_name}: {e}")
        
        return None
    
    def send(self, account_name: str, subject: str, body: str, to_email: str):
        """Send email using specified account"""
        config = self.accounts.get(account_name)
        if not config:
            raise ValueError(f"Account '{account_name}' not configured")
        
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = config.address
        msg['To'] = to_email
        
        with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port) as server:
            server.login(config.address, config.app_password)
            server.send_message(msg)
        
        print(f"✅ Email sent via {account_name} ({config.address})")

# Usage
email_manager = EmailManager()

# Send via personal account
email_manager.send(
    account_name="personal",
    subject="Personal Report",
    body="Personal content...",
    to_email="recipient@example.com"
)

# Send via business account
email_manager.send(
    account_name="business",
    subject="Business Report",
    body="Business content...",
    to_email="colleague@company.com"
)
```

## References

- Python smtplib docs: https://docs.python.org/3/library/smtplib.html
- Email.message docs: https://docs.python.org/3/library/email.message.html
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
- Gmail SMTP settings: https://support.google.com/mail/answer/7126229
- Google Workspace (Business Email): https://workspace.google.com/

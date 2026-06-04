# Business Email (Gintlab/Google Workspace)

## Quick Test

Test if your business email can use standard Gmail SMTP:

```python
import smtplib

def test_business_email(email_address, app_password):
    """Test if business email can connect via Gmail SMTP"""
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(email_address, app_password)
        return True, "Connection successful"
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed - check App Password or IT policy"
    except Exception as e:
        return False, f"Connection failed: {e}"

# Usage
success, message = test_business_email("user@company.com", "xxxx xxxx xxxx xxxx")
print(f"{'✅' if success else '❌'} {message}")
```

## Proven Working Configurations

Tested and confirmed working (2026-06-01):

| From | To | Status |
|------|-----|--------|
| `dlsgur5560@gmail.com` | `inhyeok.hwang@gintlab.com` | ✅ Working |
| `dlsgur5560@gmail.com` | `dlsgur5560@gmail.com` | ✅ Working |
| `inhyeok.hwang@gintlab.com` | `any@example.com` | ✅ Working (if App Password allowed) |

## IT Policy Restrictions

Some organizations block external App Password generation. Symptoms:

1. **App Password option missing** from Google Account settings
   - Cause: IT admin disabled "Allow users to manage their own app passwords"
   - Solution: Ask IT admin to enable for your account

2. **"Authentication failed" despite correct password**
   - Cause: SMTP relay required or IP whitelist enforced
   - Solution: Ask IT admin about SMTP relay configuration

3. **"Less secure app not supported"**
   - Cause: Workspace security policy blocking basic auth
   - Solution: Use OAuth flow (see `google-workspace` skill) or ask IT to allow SMTP

## When to Contact IT

Contact your IT administrator **before** implementing if you need to:

1. Send automated emails from a service account (not your personal address)
2. Send more than 100 emails/day (Gmail limit)
3. Use a custom "From" address different from your login
4. Configure SMTP relay for on-premises applications

**Sample IT request template**:

```
Subject: SMTP Access Request for Hermes Agent Automation

Hi IT Team,

I need to send automated emails from my address (user@company.com) via Gmail SMTP for project automation.

Details:
- Application: Hermes Agent (AI assistant)
- Purpose: Daily reports, cronjob alerts, project notifications
- Email volume: ~10-20 emails/day
- Method: SMTP SSL (smtp.gmail.com:465) with App Password

Could you please:
1. Confirm if App Password generation is allowed for my account?
2. If not, configure SMTP relay for the automation server?

Thanks,
[Your Name]
```

## Alternative: OAuth 2.0 Flow

If App Passwords are blocked, use the full OAuth flow:

1. Load the `google-workspace` skill
2. Follow the OAuth setup steps (requires Google Cloud project)
3. OAuth works for all Workspace accounts regardless of App Password policy

## Mixed Account Setup

If you have both personal and business email:

```python
# Personal Gmail
PERSONAL_GMAIL = "personal@gmail.com"
PERSONAL_APP_PASS = "xxxx xxxx xxxx xxxx"

# Business Gmail  
WORK_GMAIL = "user@company.com"
WORK_APP_PASS = "yyyy yyyy yyyy yyyy"

# Choose sender based on context
def send_notification(recipient, is_business=False):
    sender = WORK_GMAIL if is_business else PERSONAL_GMAIL
    password = WORK_APP_PASS if is_business else PERSONAL_APP_PASS
    
    send_email(
        to_email=recipient,
        subject="Notification",
        body="Message here",
        from_email=sender,
        app_password=password
    )
```

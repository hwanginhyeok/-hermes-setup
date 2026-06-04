#!/usr/bin/env python3
"""Test email SMTP connection and delivery

Usage:
    python3 email-smtp-test.py
    GMAIL_ADDRESS="user@gmail.com" GMAIL_APP_PASSWORD="xxxx xxxx" python3 email-smtp-test.py
    python3 email-smtp-test.py user@gmail.com "xxxx xxxx xxxx xxxx"
"""

import smtplib
import os
import sys
from email.message import EmailMessage
from pathlib import Path


def test_smtp_connection(
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 465,
    email_address: str = None,
    app_password: str = None,
    test_recipient: str = None
):
    """Test SMTP connection and send test email
    
    Args:
        smtp_host: SMTP server hostname
        smtp_port: SMTP server port (465 for SSL, 587 for STARTTLS)
        email_address: Sender email address
        app_password: App password for authentication
        test_recipient: Optional recipient (defaults to sender)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    
    if not email_address or not app_password:
        print("❌ Email address and app password required")
        print("   Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables")
        print("   Or pass as arguments: email-smtp-test.py <email> <password>")
        return False
    
    recipient = test_recipient or email_address
    
    msg = EmailMessage()
    msg.set_content(f"""SMTP Connection Test

This is a test email from Hermes Agent SMTP verification.

Configuration:
- SMTP Server: {smtp_host}:{smtp_port}
- Sender: {email_address}
- Recipient: {recipient}

If you receive this email, SMTP configuration is successful!

--
Hermes Agent
Email SMTP Test Script
""")
    msg['Subject'] = '✅ SMTP Test Email - Hermes Agent'
    msg['From'] = email_address
    msg['To'] = recipient
    
    print("=" * 60)
    print("SMTP Connection Test")
    print("=" * 60)
    print(f"Server: {smtp_host}:{smtp_port}")
    print(f"Sender: {email_address}")
    print(f"Recipient: {recipient}")
    print()
    
    try:
        print("Connecting to SMTP server...")
        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
            print(f"✅ Connected to {smtp_host}")
            
            print("Authenticating...")
            server.login(email_address, app_password)
            print("✅ Authentication successful")
            
            print("Sending test email...")
            server.send_message(msg)
            print(f"✅ Email sent to {recipient}")
            
        print()
        print("=" * 60)
        print("SUCCESS: SMTP configuration is working!")
        print("=" * 60)
        print(f"\nCheck inbox at {recipient}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\nPossible solutions:")
        print("  1. Verify App Password is correct (include spaces)")
        print("  2. Ensure 2-Factor Authentication is enabled")
        print("  3. Generate new App Password from Google Account settings")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        print("\nPossible solutions:")
        print("  1. Check network connectivity")
        print("  2. Verify SMTP server and port")
        print("  3. Ensure firewall allows outbound SMTP")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main entry point"""
    
    # Load credentials from environment or arguments
    email = os.getenv('GMAIL_ADDRESS')
    password = os.getenv('GMAIL_APP_PASSWORD')
    recipient = os.getenv('TEST_RECIPIENT')
    
    # Override with command-line arguments if provided
    if len(sys.argv) > 1:
        email = sys.argv[1]
    if len(sys.argv) > 2:
        password = sys.argv[2]
    if len(sys.argv) > 3:
        recipient = sys.argv[3]
    
    # Test SMTP connection
    success = test_smtp_connection(
        email_address=email,
        app_password=password,
        test_recipient=recipient
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

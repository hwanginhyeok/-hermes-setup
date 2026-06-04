#!/usr/bin/env python3
"""
Cronjob Execution Monitor with Email Alerts

Monitors Hermes Agent cronjobs and sends email alerts for:
- Failed executions (error status)
- Long-running jobs (execution time threshold)
- Daily summary reports

Requirements:
- GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables set
- Hermes Agent cronjob command available

Usage:
    python cronjob_monitor.py [--mode {check,summary,alert}] [--threshold SECONDS]

Examples:
    # Check all cronjobs and alert on failures
    python cronjob_monitor.py --mode check

    # Send daily summary report
    python cronjob_monitor.py --mode summary

    # Alert on jobs running longer than 300 seconds
    python cronjob_monitor.py --mode alert --threshold 300
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

try:
    import smtplib
    from email.message import EmailMessage
except ImportError:
    print("❌ Missing required modules: smtplib, email.message")
    print("Install with: pip install --break-system-packages smtplib")
    sys.exit(1)


# Configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
CRON_OUTPUT_BASE = Path.home() / ".hermes" / "cron" / "output"


def load_env_credentials():
    """Load Gmail credentials from environment variables"""
    email_address = os.environ.get("GMAIL_ADDRESS")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if not email_address or not app_password:
        print("❌ GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables must be set")
        print("\nSet them with:")
        print('  export GMAIL_ADDRESS="your-email@gmail.com"')
        print('  export GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"')
        sys.exit(1)
    
    return email_address, app_password


def get_cronjob_list() -> List[Dict[str, Any]]:
    """Get list of all cronjobs via hermes CLI"""
    try:
        result = subprocess.run(
            ["hermes", "cronjob", "list", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to get cronjob list: {result.stderr}")
            return []
        
        data = json.loads(result.stdout)
        return data.get("jobs", [])
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout getting cronjob list")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse cronjob list: {e}")
        return []
    except Exception as e:
        print(f"❌ Error getting cronjob list: {e}")
        return []


def get_job_execution_status(job_id: str) -> Dict[str, Any]:
    """Get execution status for a specific cronjob"""
    job_output_dir = CRON_OUTPUT_BASE / job_id
    
    if not job_output_dir.exists():
        return {
            "status": "no_output_dir",
            "latest_run": None,
            "duration": None,
            "error": None
        }
    
    # Find latest run directory
    run_dirs = sorted(
        [d for d in job_output_dir.iterdir() if d.is_dir()],
        key=lambda x: x.name,
        reverse=True
    )
    
    if not run_dirs:
        return {
            "status": "no_runs",
            "latest_run": None,
            "duration": None,
            "error": None
        }
    
    latest_run = run_dirs[0]
    metadata_file = latest_run / "metadata.json"
    
    if not metadata_file.exists():
        return {
            "status": "no_metadata",
            "latest_run": latest_run.name,
            "duration": None,
            "error": None
        }
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        started_at = metadata.get("started_at")
        completed_at = metadata.get("completed_at")
        error = metadata.get("error")
        
        duration = None
        if started_at and completed_at:
            start = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            end = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
            duration = (end - start).total_seconds()
        
        return {
            "status": "success" if error is None else "error",
            "latest_run": latest_run.name,
            "started_at": started_at,
            "completed_at": completed_at,
            "duration": duration,
            "error": error
        }
        
    except Exception as e:
        return {
            "status": "parse_error",
            "latest_run": latest_run.name,
            "duration": None,
            "error": str(e)
        }


def check_jobs(jobs: List[Dict[str, Any]], threshold: int = None) -> List[Dict[str, Any]]:
    """Check job execution status and return issues"""
    issues = []
    
    for job in jobs:
        job_id = job.get("job_id")
        job_name = job.get("name", "Unknown")
        
        execution = get_job_execution_status(job_id)
        
        # Check for failed executions
        if execution["status"] == "error":
            issues.append({
                "type": "failure",
                "job_id": job_id,
                "job_name": job_name,
                "error": execution.get("error"),
                "latest_run": execution.get("latest_run")
            })
        
        # Check for long-running jobs
        elif threshold and execution.get("duration"):
            if execution["duration"] > threshold:
                issues.append({
                    "type": "slow",
                    "job_id": job_id,
                    "job_name": job_name,
                    "duration": execution["duration"],
                    "threshold": threshold,
                    "latest_run": execution.get("latest_run")
                })
    
    return issues


def generate_summary_report(jobs: List[Dict[str, Any]]) -> str:
    """Generate daily summary report"""
    total_jobs = len(jobs)
    
    # Get execution status for all jobs
    jobs_with_status = []
    for job in jobs:
        job_id = job.get("job_id")
        execution = get_job_execution_status(job_id)
        jobs_with_status.append({
            **job,
            "execution": execution
        })
    
    # Calculate statistics
    success_count = sum(1 for j in jobs_with_status if j["execution"]["status"] == "success")
    error_count = sum(1 for j in jobs_with_status if j["execution"]["status"] == "error")
    pending_count = sum(1 for j in jobs_with_status if j["execution"]["status"] in ["no_output_dir", "no_runs"])
    
    # Get execution times
    durations = [j["execution"]["duration"] for j in jobs_with_status if j["execution"].get("duration")]
    avg_duration = sum(durations) / len(durations) if durations else 0
    max_duration = max(durations) if durations else 0
    
    # Build report
    report_lines = [
        f"# Hermes Agent Cronjob Daily Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"## Summary",
        f"- Total Jobs: {total_jobs}",
        f"- ✅ Success: {success_count}",
        f"- ❌ Error: {error_count}",
        f"- ⏳ Pending (no runs): {pending_count}",
        f"",
        f"## Execution Time Statistics",
        f"- Average: {avg_duration:.2f}s",
        f"- Max: {max_duration:.2f}s",
        f"",
        f"## Job Details",
        f""
    ]
    
    for job in jobs_with_status:
        job_name = job.get("name", "Unknown")
        status = job["execution"]["status"]
        duration = job["execution"].get("duration")
        latest_run = job["execution"].get("latest_run")
        error = job["execution"].get("error")
        
        status_symbol = "✅" if status == "success" else "❌" if status == "error" else "⏳"
        duration_str = f"{duration:.2f}s" if duration else "N/A"
        
        report_lines.append(f"### {status_symbol} {job_name}")
        report_lines.append(f"- Status: {status}")
        report_lines.append(f"- Duration: {duration_str}")
        report_lines.append(f"- Latest Run: {latest_run or 'N/A'}")
        
        if error:
            report_lines.append(f"- Error: {error[:100]}...")
        
        report_lines.append("")
    
    return "\n".join(report_lines)


def send_email(subject: str, body: str, to_email: str) -> bool:
    """Send email via Gmail SMTP"""
    try:
        email_address, app_password = load_env_credentials()
        
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = email_address
        msg['To'] = to_email
        
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(email_address, app_password)
            server.send_message(msg)
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Monitor Hermes Agent cronjobs and send email alerts")
    parser.add_argument("--mode", choices=["check", "summary", "alert"], default="check",
                       help="Operation mode: check (alert on failures), summary (daily report), alert (threshold)")
    parser.add_argument("--threshold", type=int, default=300,
                       help="Execution time threshold in seconds (for --mode alert)")
    parser.add_argument("--recipient", type=str, default=None,
                       help="Email recipient (defaults to GMAIL_ADDRESS)")
    
    args = parser.parse_args()
    
    # Load credentials
    email_address, _ = load_env_credentials()
    recipient = args.recipient or email_address
    
    # Get cronjob list
    print("📋 Fetching cronjob list...")
    jobs = get_cronjob_list()
    
    if not jobs:
        print("❌ No cronjobs found")
        sys.exit(1)
    
    print(f"✅ Found {len(jobs)} cronjobs")
    
    if args.mode == "check":
        # Check for failures
        print("🔍 Checking for failed executions...")
        issues = check_jobs(jobs)
        
        if issues:
            issue_lines = ["⚠️ Hermes Agent Cronjob Alert", ""]
            
            for issue in issues:
                if issue["type"] == "failure":
                    issue_lines.append(f"❌ {issue['job_name']} (ID: {issue['job_id']})")
                    issue_lines.append(f"   Error: {issue['error'][:100]}")
                    issue_lines.append(f"   Latest Run: {issue['latest_run']}")
                elif issue["type"] == "slow":
                    issue_lines.append(f"⏱️ {issue['job_name']} (ID: {issue['job_id']})")
                    issue_lines.append(f"   Duration: {issue['duration']:.2f}s (threshold: {issue['threshold']}s)")
                    issue_lines.append(f"   Latest Run: {issue['latest_run']}")
                
                issue_lines.append("")
            
            body = "\n".join(issue_lines)
            send_email(f"⚠️ Cronjob Alert ({len(issues)} issues)", body, recipient)
        else:
            print("✅ No issues found")
    
    elif args.mode == "summary":
        # Generate and send daily summary
        print("📊 Generating daily summary report...")
        report = generate_summary_report(jobs)
        send_email(f"📊 Cronjob Daily Report - {datetime.now().strftime('%Y-%m-%d')}", report, recipient)
    
    elif args.mode == "alert":
        # Check for long-running jobs
        print(f"⏱️ Checking for jobs exceeding {args.threshold}s threshold...")
        issues = check_jobs(jobs, threshold=args.threshold)
        
        if issues:
            issue_lines = [f"⏱️ Cronjob Execution Time Alert (threshold: {args.threshold}s)", ""]
            
            for issue in issues:
                issue_lines.append(f"⏱️ {issue['job_name']} (ID: {issue['job_id']})")
                issue_lines.append(f"   Duration: {issue['duration']:.2f}s")
                issue_lines.append(f"   Latest Run: {issue['latest_run']}")
                issue_lines.append("")
            
            body = "\n".join(issue_lines)
            send_email(f"⏱️ Execution Time Alert ({len(issues)} jobs)", body, recipient)
        else:
            print("✅ No jobs exceeded threshold")


if __name__ == "__main__":
    main()

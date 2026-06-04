#!/usr/bin/env python3
"""
Cronjob Execution Time Monitor

Analyzes all Hermes cronjobs to collect execution metrics:
- Execution duration (started_at → completed_at)
- Success/failure status
- Last execution timestamp
- Error messages

Usage: python3 scripts/cron-execution-monitor.py
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import sys

def get_cronjob_list():
    """Get all cronjobs via cronjob tool"""
    try:
        result = subprocess.run(
            ['cronjob', 'action=list'],
            capture_output=True,
            text=True,
            check=True
        )
        # Parse JSON output
        jobs = json.loads(result.stdout)
        return jobs.get('jobs', [])
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error fetching cronjob list: {e}", file=sys.stderr)
        return []

def parse_run_timestamp(ts_str):
    """Parse timestamp string to datetime with KST conversion"""
    if not ts_str:
        return None
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        # Convert to KST (+9)
        dt_kst = dt + timedelta(hours=9)
        return dt_kst
    except (ValueError, AttributeError):
        return None

def analyze_job_execution(job_id, job_name):
    """Analyze execution history for a single job"""
    cron_output_base = Path.home() / ".hermes" / "cron" / "output"
    job_output_dir = cron_output_base / job_id
    
    if not job_output_dir.exists():
        return {
            "status": "no_output_dir",
            "latest_run": None,
            "duration": None,
            "started_at": None,
            "error": None
        }
    
    # Find latest run directory (sorted by name, which is timestamp-based)
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
            "started_at": None,
            "error": None
        }
    
    latest_run = run_dirs[0]
    metadata_file = latest_run / "metadata.json"
    
    if not metadata_file.exists():
        return {
            "status": "no_metadata",
            "latest_run": latest_run.name,
            "duration": None,
            "started_at": None,
            "error": None
        }
    
    # Read metadata
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
        "duration": duration,
        "started_at": started_at,
        "completed_at": completed_at,
        "error": error
    }

def format_duration(seconds):
    """Format duration in human-readable format"""
    if seconds is None:
        return "N/A"
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.1f}s"

def print_report(jobs):
    """Print formatted execution report"""
    print("=" * 150)
    print(f"{'Job ID':<14} {'Status':<10} {'Name':<30} {'Duration':<12} {'Started At (KST)':<20} {'Error'}")
    print("=" * 150)
    
    results = []
    for job in jobs:
        job_id = job['job_id']
        job_name = job['name']
        
        analysis = analyze_job_execution(job_id, job_name)
        results.append({
            'job_id': job_id,
            'job_name': job_name,
            'analysis': analysis
        })
    
    # Sort by status (success first, then error, then pending)
    status_order = {'success': 0, 'error': 1, 'no_runs': 2, 'no_output_dir': 2, 'no_metadata': 3}
    results.sort(key=lambda x: status_order.get(x['analysis']['status'], 99))
    
    for r in results:
        job_id = r['job_id']
        job_name = r['job_name'][:28]  # Truncate if too long
        analysis = r['analysis']
        
        status_symbol = "✅" if analysis['status'] == "success" else "❌" if analysis['status'] == "error" else "⏳"
        
        duration_str = format_duration(analysis['duration'])
        started_at_kst = parse_run_timestamp(analysis.get('started_at'))
        started_at_str = started_at_kst.strftime("%Y-%m-%d %H:%M") if started_at_kst else "N/A"
        
        print(f"{status_symbol} {job_id[:12]:<12} {analysis['status']:<10} {job_name:<30} {duration_str:<12} {started_at_str:<20}")
        
        if analysis['error']:
            error_preview = analysis['error'][:60] + "..." if len(analysis['error']) > 60 else analysis['error']
            print(f"  └─ Error: {error_preview}")
    
    print("=" * 150)
    
    # Summary statistics
    total = len(results)
    success = sum(1 for r in results if r['analysis']['status'] == 'success')
    errors = sum(1 for r in results if r['analysis']['status'] == 'error')
    pending = sum(1 for r in results if r['analysis']['status'] in ['no_runs', 'no_output_dir'])
    
    print(f"\n📊 Summary: {total} total jobs")
    print(f"  ✅ Success: {success}")
    print(f"  ❌ Error: {errors}")
    print(f"  ⏳ Pending (no runs): {pending}")
    
    # Execution time statistics
    durations = [r['analysis']['duration'] for r in results if r['analysis']['duration'] is not None]
    if durations:
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        print(f"\n⏱️  Execution Time Statistics:")
        print(f"  Average: {format_duration(avg_duration)}")
        print(f"  Max: {format_duration(max_duration)}")
        print(f"  Min: {format_duration(min_duration)}")
        
        # Slowest jobs
        sorted_by_duration = sorted(
            [(r['job_name'], r['analysis']['duration']) for r in results if r['analysis']['duration']],
            key=lambda x: x[1],
            reverse=True
        )
        if sorted_by_duration:
            print(f"\n🐌 Slowest Jobs (Top 3):")
            for name, duration in sorted_by_duration[:3]:
                print(f"  - {name}: {format_duration(duration)}")

def main():
    """Main execution"""
    jobs = get_cronjob_list()
    
    if not jobs:
        print("No cronjobs found or error fetching job list.")
        return 1
    
    print_report(jobs)
    return 0

if __name__ == "__main__":
    sys.exit(main())

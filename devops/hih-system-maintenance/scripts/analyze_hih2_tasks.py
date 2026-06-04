#!/usr/bin/env python3
"""
HIH_2 Task Analyzer - Task 파일을 분석하여 자동화 후보(cronjob)를 식별

Usage:
    python3 analyze_hih2_tasks.py

Output:
    - 자동화 패턴별 그룹핑
    - 우선순위별 cronjob 후보
    - 주간 스케줄 제안
"""

import re
from collections import defaultdict
from pathlib import Path


def parse_tasks(file_path):
    """Markdown 테이블에서 태스크 파싱"""
    tasks = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        if line.startswith('| C-') and '| ---' not in line and '| #' not in line:
            parts = [p.strip() for p in line.split('|')]
            parts = parts[1:-1]  # Remove empty first/last
            
            if len(parts) >= 2:
                tasks.append({
                    'id': parts[0],
                    'title': parts[1],
                    'priority': parts[2] if len(parts) > 2 else '',
                    'depends': parts[3] if len(parts) > 3 else '',
                    'extra': parts[4] if len(parts) > 4 else ''
                })
    
    return tasks


def analyze_automation_patterns(tasks):
    """자동화 패턴 분석"""
    
    patterns = {
        'daily': ['데일리', 'standup', '브리핑', '진행사항', 'daily'],
        'weekly': ['주간', 'weekly', 'week'],
        'sync': ['노션', 'Notion', '동기화', 'sync', '갱신', '업데이트'],
        'monitoring': ['DFMEA', '이슈', '모니터링', '점검', 'health', '체크', '검증'],
        'reporting': ['보고서', 'report', 'Excel', '생성', '작성', '주간보고'],
        'data_collection': ['데이터', 'CSV', 'collect', 'fetch', 'DB', 'database', '발굴'],
        'documentation': ['문서', '작성', '정리', '매뉴얼', 'SOP'],
        'quality': ['품질', 'QC', 'IQC', 'EOL', '검사', '시험', 'DVP']
    }
    
    cron_candidates = []
    
    for task in tasks:
        combined = (task['title'] + ' ' + task['extra'] + ' ' + task['priority'] + ' ' + task['depends']).lower()
        
        detected = []
        for pattern_type, keywords in patterns.items():
            if any(kw.lower() in combined for kw in keywords):
                detected.append(pattern_type)
        
        if detected:
            cron_candidates.append({
                'id': task['id'],
                'title': task['title'],
                'priority': task['priority'],
                'patterns': detected
            })
    
    # 우선순위 정렬
    priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3, '': 4}
    cron_candidates.sort(key=lambda x: (priority_order.get(x['priority'], 99), x['id']))
    
    return cron_candidates, patterns


def print_report(current_tasks, prepared_tasks):
    """분석 보고서 출력"""
    
    print(f"=== HIH_2 Task Analysis ===\n")
    print(f"Current: {len(current_tasks)}")
    print(f"Prepared: {len(prepared_tasks)}")
    print(f"Total Active: {len(current_tasks) + len(prepared_tasks)}")
    
    # Prepared tasks 분석
    cron_candidates, patterns = analyze_automation_patterns(prepared_tasks + current_tasks)
    
    print(f"\n=== Cron Job Candidates: {len(cron_candidates)} ===\n")
    
    for c in cron_candidates:
        patterns_str = ', '.join(c['patterns'])
        print(f"[{c['priority']}] {c['id']}: {c['title'][:60]}")
        print(f"     → {patterns_str}")
    
    # 패턴별 그룹핑
    print(f"\n=== Pattern Groups ===\n")
    
    pattern_groups = defaultdict(list)
    for c in cron_candidates:
        for pattern in c['patterns']:
            pattern_groups[pattern].append(c)
    
    for pattern in ['daily', 'weekly', 'sync', 'monitoring', 'reporting', 'data_collection', 'documentation', 'quality']:
        if pattern in pattern_groups:
            tasks = pattern_groups[pattern]
            print(f"{pattern.upper()}: {len(tasks)} tasks")
            for t in tasks[:3]:
                print(f"  - {t['id']}: {t['title'][:40]}")
            if len(tasks) > 3:
                print(f"  ... and {len(tasks)-3} more")
            print()


def main():
    """메인 실행 함수"""
    
    project_root = Path.cwd()
    
    # 태스크 파일 경로
    current_file = project_root / "CURRENT_TASK.md"
    prepared_file = project_root / "PREPARED_TASK.md"
    
    if not current_file.exists() or not prepared_file.exists():
        print("Error: CURRENT_TASK.md or PREPARED_TASK.md not found")
        return 1
    
    # 태스크 파싱
    current_tasks = parse_tasks(current_file)
    prepared_tasks = parse_tasks(prepared_file)
    
    # 보고서 출력
    print_report(current_tasks, prepared_tasks)
    
    return 0


if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""
Safe Cron Batch Update Template

cron 일괄 변경 전 백업 + 검증 + 적용 + 롤백 프로시저.
PM이 crontab을 안전하게 수정할 때 사용.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

BACKUP_DIR = Path("/tmp/cron_backups")

def backup_current():
    """현재 crontab 백업"""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"crontab_backup_{timestamp}.txt"
    
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    backup_path.write_text(result.stdout)
    
    print(f"✅ 백업 완료: {backup_path}")
    return backup_path

def preview_changes(new_crontab_path: Path):
    """변경사항 미리보기"""
    print("\n## 변경사항 미리보기")
    print("=" * 60)
    
    current = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
    new = new_crontab_path.read_text()
    
    current_lines = set(current.strip().split('\n'))
    new_lines = set(new.strip().split('\n'))
    
    added = new_lines - current_lines
    removed = current_lines - new_lines
    
    if added:
        print("\n### 추가될 항목:")
        for line in added:
            if line.strip() and not line.startswith('#'):
                print(f"+ {line}")
    
    if removed:
        print("\n### 제거될 항목:")
        for line in removed:
            if line.strip() and not line.startswith('#'):
                print(f"- {line}")
    
    if not added and not removed:
        print("변경사항 없음")
    
    print("=" * 60)
    return len(added), len(removed)

def validate_syntax(crontab_path: Path):
    """cron 문법 검증"""
    content = crontab_path.read_text()
    errors = []
    
    for i, line in enumerate(content.split('\n'), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parts = line.split()
        if len(parts) < 6:
            errors.append(f"Line {i}: 필드 부족 ({len(parts)}개, 최소 6개 필요)")
    
    if errors:
        print("\n❌ 문법 오류:")
        for err in errors:
            print(f"  {err}")
        return False
    
    print("✅ 문법 검증 통과")
    return True

def apply_crontab(new_crontab_path: Path, backup_path: Path):
    """crontab 적용"""
    print(f"\n적용 중: {new_crontab_path}")
    
    if not validate_syntax(new_crontab_path):
        return False
    
    result = subprocess.run(["crontab", str(new_crontab_path)], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 적용 실패: {result.stderr}")
        return False
    
    print("✅ 적용 완료")
    
    print("\n## 적용 후 crontab 확인")
    print("=" * 60)
    subprocess.run(["crontab", "-l"])
    print("=" * 60)
    
    return True

def rollback(backup_path: Path):
    """롤백"""
    print(f"\n롤백 중: {backup_path}")
    result = subprocess.run(["crontab", str(backup_path)], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ 롤백 완료")
    else:
        print(f"❌ 롤백 실패: {result.stderr}")

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <new_crontab_file>")
        sys.exit(1)
    
    new_file = Path(sys.argv[1])
    if not new_file.exists():
        print(f"❌ 파일 없음: {new_file}")
        sys.exit(1)
    
    backup_path = backup_current()
    added, removed = preview_changes(new_file)
    
    if added or removed:
        confirm = input("\n적용하시겠습니까? (y/N): ")
        if confirm.lower() != 'y':
            print("취소됨")
            sys.exit(0)
    
    if apply_crontab(new_file, backup_path):
        print(f"\n✅ 완료. 롤백: crontab {backup_path}")
    else:
        print("\n❌ 적용 실패. 자동 롤백합니다...")
        rollback(backup_path)

if __name__ == "__main__":
    main()

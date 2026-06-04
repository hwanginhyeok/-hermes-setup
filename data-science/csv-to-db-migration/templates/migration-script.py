#!/usr/bin/env python3
"""CSV 시드 데이터 → DB 마이그레이션 스크립트 템플릿

멱등성 (재실행해도 중복 INSERT X) + dry-run 모드 + 백업 자동 생성 포함.

Usage:
    python3 scripts/migrate_csv_to_db.py                    # 실제 적용
    python3 scripts/migrate_csv_to_db.py --dry-run          # 미리보기만

특징:
- 백업 자동 생성 (db.bak.YYYYMMDD_HHMMSS)
- 트랜잭션 단위 (실패 시 롤백)
- UPSERT로 중복 방지 (ON CONFLICT DO UPDATE)
- JSON properties로 카테고리/메타데이터 보존
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

# =============================================================================
# 설정 (프로젝트별 수정)
# =============================================================================

CSV_PATH = Path("data/research/stocks/tesla/issues.csv")
DB_PATH = Path("data/db/stock_rich.db")
ENTITY_TYPE = "tesla_issue"  # 단일 entity_type (카테고리는 properties로)
TICKER = "TSLA"
MARKET = "US"

# CSV → DB 매핑표
COLUMN_MAPPING = {
    "issue_id": "id",  # 기본키
    "title": "name",  # 엔티티 이름
    "category": "properties->>'$.category'",  # TSLA-E → 'E'로 변환 후 properties
    "status": "status",  # 그대로
    "severity": "properties['severity']",  # JSON
    "thesis_side": "properties['thesis_side']",  # JSON
    # 필요한 만큼 추가
}

# =============================================================================
# 유틸리티
# =============================================================================

def backup_db(db_path: Path) -> Path:
    """DB 백업 생성 (원본 보존)
    
    Returns:
        백업 파일 경로
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"{db_path.stem}.bak.{timestamp}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def extract_category(category_code: str) -> str:
    """카테고리 코드 추출: TSLA-E-001 → E
    
    Args:
        category_code: TSLA-E, TSLA-P, TSLA-C 등
    
    Returns:
        단일 문자 카테고리 (E, P, C, I, F, R, M 등)
    """
    if "-" in category_code:
        return category_code.split("-")[1]
    return category_code


def build_properties(row: dict) -> dict:
    """properties JSON 빌드
    
    Args:
        row: CSV 한 행 (dict)
    
    Returns:
        properties dict
    """
    props = {}
    
    # 카테고리 (TSLA-E → 'E')
    if "category" in row:
        props["category"] = extract_category(row["category"])
    
    # severity (JSON)
    if "severity" in row and row["severity"]:
        props["severity"] = row["severity"]
    
    # thesis_side (JSON)
    if "thesis_side" in row and row["thesis_side"]:
        props["thesis_side"] = row["thesis_side"]
    
    # related IDs (JSON 배열)
    if "related_entity_ids" in row and row["related_entity_ids"]:
        props["related_entity_ids"] = eval(row["related_entity_ids"])  # CSV가 "[...]" 문자열일 때
    
    # 필요한 만큼 추가
    # ...
    
    return props


# =============================================================================
# 마이그레이션 핵심 로직
# =============================================================================

def migrate_csv_to_db(
    csv_path: Path,
    db_path: Path,
    entity_type: str,
    ticker: str,
    market: str,
    dry_run: bool = False
) -> dict:
    """CSV → ontology_entities 마이그레이션
    
    Args:
        csv_path: CSV 파일 경로
        db_path: SQLite DB 경로
        entity_type: entity_type 값 (예: 'tesla_issue')
        ticker: ticker (예: 'TSLA')
        market: market (예: 'US')
        dry_run: True면 DB 미수정, 예상만 출력
    
    Returns:
        결과 dict {count, duplicates, backup_path}
    """
    import pandas as pd
    
    # CSV 로드
    df = pd.read_csv(csv_path)
    total_count = len(df)
    
    if dry_run:
        print(f"## Dry-run 결과")
        print(f"- CSV 경로: {csv_path}")
        print(f"- DB 경로: {db_path}")
        print(f"- 총 {total_count}건 INSERT 예정")
        print()
        
        # 샘플 2건 출력
        print("### 샘플 (2건)")
        for idx, row in df.head(2).iterrows():
            props = build_properties(row.to_dict())
            print(f"**{row['issue_id']}**: {row['title']}")
            print(f"  - entity_type: {entity_type}")
            print(f"  - properties: {json.dumps(props, ensure_ascii=False)}")
            print()
        
        return {"count": total_count, "duplicates": 0, "backup_path": None}
    
    # 백업 생성
    backup_path = backup_db(db_path)
    print(f"✅ 백업 완료: {backup_path}")
    
    # DB 연결
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 기존 카운트 확인
    cursor.execute("SELECT COUNT(*) FROM ontology_entities;")
    before_count = cursor.fetchone()[0]
    
    try:
        # 트랜잭션 시작
        conn.execute("BEGIN TRANSACTION")
        
        insert_count = 0
        duplicate_count = 0
        
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            entity_id = row_dict["issue_id"]
            entity_name = row_dict["title"]
            status = row_dict.get("status", "open")
            props = build_properties(row_dict)
            
            # UPSERT (INSERT ON CONFLICT)
            cursor.execute("""
                INSERT INTO ontology_entities (
                    id, name, entity_type, status, properties, ticker, market
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    properties = excluded.properties,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                entity_id,
                entity_name,
                entity_type,
                status,
                json.dumps(props, ensure_ascii=False),
                ticker,
                market
            ))
            
            if cursor.rowcount > 0:
                insert_count += 1
            else:
                duplicate_count += 1
        
        # 커밋
        conn.commit()
        
        # 적용 후 카운트 확인
        cursor.execute("SELECT COUNT(*) FROM ontology_entities;")
        after_count = cursor.fetchone()[0]
        
        print(f"✅ 마이그레이션 완료")
        print(f"  - INSERT/UPDATE: {insert_count}건")
        print(f"  - 중복 (UPDATE): {duplicate_count}건")
        print(f"  - 전후 카운트: {before_count} → {after_count} (+{after_count - before_count}건)")
        
        return {
            "count": insert_count,
            "duplicates": duplicate_count,
            "backup_path": str(backup_path)
        }
        
    except Exception as e:
        # 롤백
        conn.rollback()
        print(f"❌ 실패 (롤백 완료): {e}")
        raise
    finally:
        conn.close()


# =============================================================================
# CLI 엔트리포인트
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CSV → DB 마이그레이션 (멱등성 + dry-run 지원)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="DB 미수정, 예상만 출력"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=str(CSV_PATH),
        help=f"CSV 파일 경로 (기본값: {CSV_PATH})"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=str(DB_PATH),
        help=f"DB 파일 경로 (기본값: {DB_PATH})"
    )
    
    args = parser.parse_args()
    
    # 경로 검증
    csv_path = Path(args.csv)
    db_path = Path(args.db)
    
    if not csv_path.exists():
        print(f"❌ CSV 파일 없음: {csv_path}")
        exit(1)
    
    if not db_path.exists():
        print(f"❌ DB 파일 없음: {db_path}")
        exit(1)
    
    # 마이그레이션 실행
    result = migrate_csv_to_db(
        csv_path=csv_path,
        db_path=db_path,
        entity_type=ENTITY_TYPE,
        ticker=TICKER,
        market=MARKET,
        dry_run=args.dry_run
    )
    
    if not args.dry_run:
        print()
        print(f"## 역호환 검증 (필요 시)")
        print(f"```bash")
        print(f"# 랜덤 샘플 5건 확인 (기존 데이터 손상 없는지)")
        print(f"sqlite3 {db_path} \"SELECT id, name FROM ontology_entities WHERE id NOT LIKE 'TSLA-%' ORDER BY RANDOM() LIMIT 5;\"")
        print(f"```")

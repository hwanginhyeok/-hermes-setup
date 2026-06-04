---
name: csv-to-db-migration
description: CSV 시드 데이터 → DB 마이그레이션 패턴. 매핑표 설계, 충돌 해결, 카테고리 보존, 멱등성, dry-run 검증 포함.
user_invocable: true
---

# CSV → DB Migration

CSV 시드 데이터를 SQLite/PostgreSQL 등의 DB로 마이그레이션할 때의 **정석 패턴**.

## 언제 사용

- 프로젝트에 CSV 형태의 시드 데이터가 있고 이를 DB로 로드해야 할 때
- ontology_entities, ontology_events 같은 테이블에 연관 데이터를 넣을 때
- **중복 ID 충돌 가능성**이 있는 여러 CSV를 통합할 때
- **카테고리/분류 체계**를 보존해야 할 때

## 실행 프로세스

### 1. 설계 먼저 (test-first 룰)

코드 작성 전 **매핑표**를 먼저 작성하고 PM/사용자 승인을 받는다.

```python
# 매핑표 포맷
| CSV 컬럼 | DB 컬럼 | 매핑 규칙 |
|-----------|----------|-----------|
| issue_id | id | 그대로 (TSLA-E-001 형식) |
| title | name | 그대로 |
| category | properties['category'] | JSON으로 저장 ('E'/'P'/'C'/...) |
```

**필수 확인사항**:
- [ ] CSV 컬럼 → DB 컬럼 매핑 (1:1 vs JSON properties)
- [ ] 기존 DB 스키마 확인 (`PRAGMA table_info`)
- [ ] 카테고리/분류 정보 보존 방법 (entity_type vs properties)
- [ ] 중복 ID 충돌 처리 룰

### 2. 충돌 점검 (여러 CSV 통합 시)

```python
import pandas as pd

issues_df = pd.read_csv("issues.csv")
tagged_df = pd.read_csv("tagged_issues.csv")

issues_ids = set(issues_df['issue_id'].tolist())
tagged_ids = set(tagged_df['issue_id'].tolist())

duplicates = issues_ids & tagged_ids
only_issues = issues_ids - tagged_ids
only_tagged = tagged_ids - issues_ids

print(f"중복: {len(duplicates)}건")
print(f"issues만: {len(only_issues)}건")
print(f"tagged만: {len(only_tagged)}건")
```

**충돌 처리 룰**:
- **옵션 B1 (권장)**: 상세한 CSV 우선 + 단순 CSV의 고유 컬럼만 병합
  - 이유: 더 많은 컬럼 = 더 풍부한 데이터
  - 방식: 기준 CSV INSERT → 나머지 CSV의 고유 컬럼을 properties에 UPDATE
- **옵션 B2**: 단순 CSV 우선 (sentiment 같은 중요 컬럼이 있을 때)
- **옵션 B3**: 병합 (properties['conflict']에 두 데이터 모두 저장)

### 3. 카테고리 보존 (Pitfall 주의)

**❌ 나쁜 예**: 카테고리를 entity_type으로 분리
```python
# entity_type 종류 폭발!
'tesla_issue_E', 'tesla_issue_P', 'tesla_issue_C', ...  # 7종 이상
```

**✅ 좋은 예**: entity_type은 단일, 카테고리는 properties
```python
entity_type = 'tesla_issue'  # 단일
properties['category'] = 'E'/'P'/'C'/...  # JSON으로 저장
```

**이유**:
1. **데이터 모델 정석**: entity_type은 '개체 유형', properties는 '속성'
2. **쿼리 성능**: `WHERE properties->>'$.category' = 'E'` (SQLite JSON1 지원)
3. **확장성**: 향후 카테고리 추가 시 entity_type 폭발 방지
4. **조인 간소**: `WHERE entity_type = 'tesla_issue'`로 전체 조회 후 필터링

### 4. 마이그레이션 스크립트 작성

**필수 기능**:
- `--dry-run` 모드 (DB 미수정 + 변경 사항만 출력)
- 멱등성 (재실행해도 중복 INSERT X → UPSERT 또는 EXISTS 체크)
- 트랜잭션 단위 (실패 시 롤백)
- 백업 자동 생성 (`cp db db.bak.YYYYMMDD`)

```python
#!/usr/bin/env python3
"""CSV → DB 마이그레이션 (멱등성 + dry-run 지원)"""

import argparse
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

def backup_db(db_path: Path) -> Path:
    """DB 백업 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"{db_path.stem}.bak.{timestamp}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    return backup_path

def migrate_issues(csv_path: Path, db_path: Path, dry_run: bool = False):
    """issues.csv → ontology_entities 마이그레이션"""
    
    if not dry_run:
        backup_path = backup_db(db_path)
        print(f"✅ 백업 완료: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # CSV 로드
    df = pd.read_csv(csv_path)
    
    if dry_run:
        print(f"## Dry-run 결과")
        print(f"- 총 {len(df)}건 INSERT 예정")
        print(f"- 중복 체크: ...")
        return
    
    try:
        # 트랜잭션 시작
        conn.execute("BEGIN TRANSACTION")
        
        for _, row in df.iterrows():
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
                row['issue_id'],
                row['title'],
                'tesla_issue',
                row['status'],
                json.dumps({
                    'category': row['category'].split('-')[1],  # 'TSLA-E' → 'E'
                    'severity': row['severity'],
                    # ... 기타 properties
                }),
                'TSLA',
                'US'
            ))
        
        conn.commit()
        print(f"✅ {len(df)}건 INSERT 완료")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 실패: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    migrate_issues(
        csv_path=Path("data/research/stocks/tesla/issues.csv"),
        db_path=Path("data/db/stock_rich.db"),
        dry_run=args.dry_run
    )
```

### 5. Dry-run 검증

```bash
# 1. 카운트 검증
python3 scripts/migrate_tesla_csv_to_db.py --dry-run | grep "INSERT 예정"

# 2. 샘플 출력 (1~2건)
python3 scripts/migrate_tesla_csv_to_db.py --dry-run | grep -A 10 "샘플"

# 3. 중복 체크
# - 기존 ontology_entities 카운트: 15954건
# - 새 TSLA 관련: 10건
# - 적용 후: 15964건 (기대값)
```

### 6. 실제 적용 + 역호환 검증

**적용 전 체크리스트**:
- [ ] DB 백업 완료 (`cp db db.bak.YYYYMMDD`)
- [ ] Dry-run 결과 카운트 확인
- [ ] 중복 ID 충돌 처리 룰 승인

**적용 후 검증**:
```python
import sqlite3

conn = sqlite3.connect("data/db/stock_rich.db")
cursor = conn.cursor()

# 1. 전후 카운트 확인
cursor.execute("SELECT COUNT(*) FROM ontology_entities;")
before = 15954  # 적용 전
after = cursor.fetchone()[0]
print(f"카운트 변화: {before} → {after} (+{after - before}건)")

# 2. 신규 데이터 확인
cursor.execute("""
    SELECT id, name, properties FROM ontology_entities
    WHERE ticker = 'TSLA' AND entity_type = 'tesla_issue'
    LIMIT 5;
""")
for row in cursor.fetchall():
    print(f"- {row[0]}: {row[1]}")

# 3. 기존 데이터 손상 확인 (랜덤 샘플)
cursor.execute("""
    SELECT * FROM ontology_entities
    WHERE id NOT LIKE 'TSLA-%'
    ORDER BY RANDOM() LIMIT 5;
""")
sample = cursor.fetchall()
assert len(sample) == 5, "기존 데이터 손상 의심"

conn.close()
```

## Pitfalls

### Pitfall 1: 카테고리 정보 손실 (가장 치명적)

**문제**: CSV의 TSLA-E/P/C/F/I/R/M 체계를 단일 entity_type으로 통합하면 카테고리 구분 불가

**해결**: `properties['category']`에 보존

**실수 사례** (2026-05-19 Stock 1-47):
- 초기 매핑: `entity_type = 'tesla_issue'` 단일값 → **7개 카테고리 다 사라짐**
- PM 수정 요청: 3가지 우려 중 "가장 큰 문제"로 지적됨
- 수정: `entity_type = 'tesla_issue'` 유지 + `properties['category'] = 'E'/'P'/'C'/...` 보존
```python
# ❌ 나쁨
entity_type = f"tesla_issue_{category}"  # tesla_issue_E, tesla_issue_P, ...

# ✅ 좋음
entity_type = 'tesla_issue'
properties['category'] = category  # 'E', 'P', 'C', ...
```

### Pitfall 2: 중복 ID 조용한 덮어쓰기

**문제**: `INSERT`만 쓰면 중복 ID 있을 때 error 조용히 발생

**해결**: UPSERT 사용
```sql
INSERT INTO ontology_entities (...) VALUES (...)
ON CONFLICT(id) DO UPDATE SET
  name = excluded.name,
  properties = excluded.properties
```

또는 사전 EXISTS 체크:
```python
cursor.execute("SELECT 1 FROM ontology_entities WHERE id = ?", (row['issue_id'],))
if cursor.fetchone() is None:
    cursor.execute("INSERT ...")
```

### Pitfall 3: 여러 CSV 간 PK 중복 미검증

**문제**: issues.csv와 tagged_issues.csv의 중복 ID를 확인하지 않고 무조건 병합

**해결**: 전수 비교 후 충돌 처리 룰 정의

**실수 사례** (2026-05-19 Stock 1-47):
- 중복 ID: 9건 (TSLA-C-001/002, E-001, F-001, I-001, M-001, P-001/002, R-001)
- 충돌 예시: TSLA-C-001 (issues.csv: "FSD v13 unsupervised" vs tagged.csv: "FSD v13.5 Wide Release")
- 수정: issues.csv 우선(18컬럼 vs 7컬럼) + tagged 고유 컬럼만 병합
```python
duplicates = issues_ids & tagged_ids
if duplicates:
    print(f"⚠️ 중복 {len(duplicates)}건 발견:")
    for dup_id in duplicates:
        print(f"  - {dup_id}")
        # 사용자/PM에 어떻게 처리할지 묻기
```

### Pitfall 4: 관계형 데이터 저장소 미확인

**문제**: milestone-issue 관계를 ontology_links 테이블에 넣을지 properties에 넣을지 결정 안 함

**해결**: 기존 DB 데이터 패턴 확인 후 결정

**실수 사례** (2026-05-19 Stock 1-47):
- PM 우려: "ontology_links 테이블 있음 → milestone 관계 정석적으로는 여기에 들어가야 함"
- 확인: ontology_links 스키마 11컬럼, sample data 5건 확인 → milestone 링크 0건
- 결정: properties['issue_id']만 (간단, 기존 패턴 따름)
```python
# ❌ 복잡
cursor.execute("""
    INSERT INTO ontology_links (source_type, source_id, target_type, target_id, link_type)
    VALUES ('event', milestone_id, 'entity', issue_id, 'part_of')
""")

# ✅ 간단
properties['issue_id'] = issue_id  # JSON 필드에 저장
# 조회 시: WHERE properties->>'$.issue_id' = 'TSLA-E-001'
```

**이유**: ontology_links는 '대등한 관계'(entity ↔ entity)에 적합, milestone은 issue의 하위 이벤트

## 참고 문서

- SQLite JSON1: `properties->>'$.category'` 쿼리
- UPSERT 문법: `INSERT ... ON CONFLICT DO UPDATE`
- 트랜잭션: `BEGIN TRANSACTION` / `COMMIT` / `ROLLBACK`

## 지원 파일

- `templates/migration-script.py` — CSV → DB 마이그레이션 스크립트 템플릿 (dry-run, 백업, UPSERT 포함)

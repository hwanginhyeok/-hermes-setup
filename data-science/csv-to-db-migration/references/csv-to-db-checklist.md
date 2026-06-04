# CSV → DB 마이그레이션 설계 체크리스트

## 목적
CSV 시드 데이터를 DB에 마이그레이션할 때 설계 검증 → PM 승인 → 코드 작성 순서를 보장하는 체크리스트.

## 필수 단계 (순서 준수)

### 1. 데이터 모델 확인
- [ ] DB 스키마 확인 (`PRAGMA table_info`, `\d table`)
- [ ] SQLAlchemy/ORM 모델 정의 확인 (models.py)
- [ ] 기존 데이터 카운트 (마이그레이션 전후 비교용)

### 2. CSV 컬럼 분석
- [ ] CSV 파일별 컬럼 리스트 추출
- [ ] 데이터 타입 추정 (str/int/float/date/json)
- [ ] 필수값 vs nullable 확인
- [ ] 중복 ID 파악 (여러 CSV 간 PK 충돌)

### 3. 매핑표 작성 (PM 승인 전 필수)
- [ ] CSV 컬럼 → DB 컬럼 1:1 매핑
- [ ] 복합 컬럼 → JSON properties 매핑
- [ ] 자동 생성 컬럼 명시 (ticker, market, created_at 등)
- [ ] **카테고리 정보 보존 여부 검토** (entity_type 분리 vs properties)

### 4. 중복/충돌 처리
- [ ] 여러 CSV 간 PK 중복 확인 (예: issues.csv vs tagged_issues.csv)
- [ ] 중복 시 우선순위 규칙 정의 (어떤 CSV를 기준으로 할지)
- [ ] 병합 전략: (A) 기준 CSV 우선 + 나머지 properties 병합, (B) 독립 INSERT

### 5. 관계형 데이터 처리
- [ ] 1:N 관계 (issue ↔ milestone) 어떻게 저장?
  - (A) properties['parent_id']만 (간단)
  - (B) 별도 link 테이블 (ontology_links)
  - (C) 둘 다 (이중)
- [ ] 기존 DB 패턴 확인 (sample data로 link 테이블 사용 여부)

### 6. 멱등성 설계
- [ ] UPSERT 또는 EXISTS 체크 (재실행해도 중복 INSERT 방지)
- [ ] 트랜잭션 단위 (실패 시 롤백)
- [ ] 백업 계획 (`cp db db.bak.YYYYMMDD`)

### 7. PM 승인
- [ ] 매핑표 + 충돌 처리 룰 PM 보고
- [ ] PM 승인 후에만 코드 작성 시작

## 실수 사례 (2026-05-19 Stock 1-47)

### ❌ 카테고리 정보 손실
- **문제**: TSLA-E/P/C/F/I/R/M 7개 카테고리 → `entity_type='tesla_issue'` 단일로 통합 예정
- **수정**: `properties['category']`에 'E'/'P'/'C' 등 보존
- **교훈**: 분류 체계는 properties로, entity_type은 '개체 유형'만 담당

### ❌ 중복 ID 미검증
- **문제**: issues.csv와 tagged_issues.csv에서 TSLA-C-001 등 9건 중복
- **수정**: 중복 전수 비교 → issues.csv 우선 + tagged 고유 컬럼만 병합
- **교훈**: CSV 간 PK 교집합 확인 후 병합 전략 수립

### ❌ 관계형 데이터 저장소 미확인
- **문제**: milestone의 issue_id를 properties에 저장 vs ontology_links 테이블 사용 결정 안 함
- **수정**: 기존 DB 패턴 확인 (ontology_links 0건) → properties['issue_id']만 간단 저장
- **교훈**: 기존 데이터 사용 패턴 먼저 확인 후 결정

## Dry-run 검증 항목
- [ ] 카운트: CSV 행 수 vs DB INSERT 예상 건 수 일치
- [ ] 샘플 출력: 1~2건 매핑 결과 실제 데이터 확인
- [ ] 중복 체크: PK 중복 시 어떻게 처리되는지 로그 확인

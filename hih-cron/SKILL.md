---
name: hih-cron
description: cron 점검 + 추가/수정 시 자동 호출. 기존 cron에 합칠 수 있으면 합치고, 아니면 추가. 충돌·중복 방지.
user_invocable: true
---

# /hih-cron

cron 작업을 추가/수정할 때 호출한다. 무작정 새 줄 추가하지 말고, **기존 cron과 합칠 수 있는지 먼저 검토**한 후 결정한다.

상세 cron 스케줄 SSOT: `~/project-manager/global-rules/cron.md`

## 실행 시 동작

### 0. SSOT vs 실제 crontab 정합성 검증 (MUST)
```bash
# PM 검증 룰: 글로벌 cron.md(SSOT)에 기재된 cron이 실제 crontab에 등록됐는지 확인
# 문제: 문서만 "✅ 작동 중"인데 실제 등록 안 된 케이스 다수 발견 (be-a-studio run_daily.sh 등)
crontab -l | grep -E "(project|script_name)"
# 또는
crontab -l > /tmp/crontab_current.txt && grep "pattern" /tmp/crontab_current.txt
```
- SSOT(`global-rules/cron.md`) 기재 → 실제 crontab 등록 여부 1:1 매칭 검증
- 문서와 실제가 다르면: (1) crontab 등록 우선, (2) 문서 갱신 후
- 로그 파일 존재 ≠ cron 등록됨 (수동 실행으로 로그 남을 수도 있음)

### 1. 현재 cron 스냅샷 확인
```bash
crontab -l
```

### 2. 추가하려는 작업 분류 (필수 출력)
```
## 추가/수정 요청
- 작업: <스크립트 경로 + 인자>
- 시각: <cron expression>
- 목적: <왜 필요한가>
- 로그 위치: <log path>
```

### 3. 합치기 후보 탐색 (필수 출력)
```
## 합치기 검토
- 같은 시각 항목: <crontab에서 매칭되는 줄들>
- 같은 디렉토리/스크립트 패밀리: <같은 프로젝트의 다른 cron>
- 합칠 수 있는가? Y / N
- 합치기 방식:
  - (A) 한 스크립트에 모드 인자 추가 (예: briefing.sh morning|evening)
  - (B) 같은 시각이면 && 또는 ; 로 체이닝
  - (C) 새 wrapper 스크립트로 묶기
  - (D) 합칠 수 없음 → 새 줄로 추가
```

### 4. 충돌 체크 (필수 출력)
```
## 충돌 체크
- 동시 실행 부담: 같은 시각에 무거운 작업 중복 시 분리
- 의존성: A가 B 결과 필요하면 시각 차이 두기
- 락 파일/DB 접근 충돌: 동일 리소스 접근하는 작업은 직렬화
```

### 5. 추천 결정 (필수 출력)
```
## 결정
- 권고: 합치기 / 추가 / 분리
- 이유: <왜>
- 적용 cron expression:
  <줄 그대로>
- 등록 방법:
  사용자가 `crontab -e`로 직접 추가 (룰: cron 등록은 사용자 직접)
- 검증: 등록 후 다음 실행 시각에 로그 확인
```

## 룰

1. **무조건 추가 금지** — 합치기 검토 거치지 않으면 진행 안 함
2. **사용자 직접 등록** — `crontab -e`만 사용. 스크립트가 자동 등록 금지 (글로벌 룰 cron.md)
3. **SSOT 정합성 필수** — `global-rules/cron.md` 기재내용 vs 실제 crontab 1:1 검증. 문서만 "작동 중"인데 실제 미등록 케이스 방지
4. **백업 필수** — crontab 변경 전 `crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt`
5. **30일+ 로그 자동 삭제 검토** — 새 cron 추가 시 로그 회전 룰 동시 검토
6. **시각 충돌 회피** — 정각(:00)에 작업이 너무 몰리면 :05/:10/:15로 분산
7. **기존 cron 수정 시** — 변경 전후 diff 보고 후 진행

## Pitfalls

### ❌ 문서만 믿고 실제 crontab 확인 안 함
- 증상: `global-rules/cron.md`에 "✅ 작동 중"인데 실제 `crontab -l`에 없음
- 원인: (1) 과거에 cron 등록 후 문서만 갱신, (2) crontab 초기화/재설정으로 등록 사라짐
- 해결: **0단계 정합성 검증** 필수 실행
- 사례 (2026-05-19): be-a-studio `run_daily.sh` — 문서엔 "05:30 매일"인데 crontab엔 `enrich_news_v2.py` 단독만 등록됨

### ❌ Partial vs Full pipeline 혼동
- 증상: 단일 스크립트(enrich_news_v2.py)는 cron 있는데 전체 파이프라인(run_daily.sh)는 누락
- 원인: 파이프라인 내부 단계를 개별적으로 등록하고, wrapper(run_daily.sh)는 빠먹음
- 해결: wrapper cron 존재 확인 → 단일 스크립트 cron은 중복이면 제거
- 사례 (2026-05-19): be-a-studio enrich_news_v2.py는 있고 run_daily.sh는 없음 → run_daily.sh로 통합

## 합치기 패턴 예시

### 패턴 A: 모드 인자
```
# Before (2줄):
0 6 * * * /path/morning_brief.sh
0 22 * * * /path/evening_brief.sh

# After (1 스크립트 + 2 cron 줄, 그러나 스크립트 내부 로직 통합):
0 6 * * * /path/brief.sh morning
0 22 * * * /path/brief.sh evening
```

### 패턴 B: 같은 시각 체이닝
```
# Before (2줄, 같은 06:00):
0 6 * * * /path/sync_a.sh
0 6 * * * /path/sync_b.sh

# After (1줄):
0 6 * * * /path/sync_a.sh && /path/sync_b.sh
```

### 패턴 C: wrapper로 묶기
```
# Before (3줄, 같은 패밀리):
0 7 * * * /path/daily_part1.sh
0 7 * * * /path/daily_part2.sh
0 7 * * * /path/daily_part3.sh

# After (1줄):
0 7 * * * /path/daily_pipeline.sh   # 내부에서 part1/2/3 순차 호출
```

## 참고 문서

- 📋 **Partial vs Full Pipeline Cron 혼동**: `references/partial-vs-full-pipeline-cron.md` — 단일 스크립트 cron vs wrapper 스크립트 cron 식별, 진단, 해결 사례
  - 증상: enrich_news_v2.py만 등록되고 run_daily.sh(전체 파이프라인) 누락
  - 진단: raw 파일 생성 여부, 로그 오류 메시지, wrapper 스크립트 내용 확인
  - 해결: partial cron 제거 + full pipeline cron 추가

## Pitfalls (주의사항)

### Cron이 등록됐는데 실행 안 되는 경우 (RC 추적)

**증상**: `crontab -l`에 있는데 로그 파일이 안 생김

**실제 사례**: screener_vwma100.py (05:00 평일) → 로그 미생성
- 원인: 05:00 시간대에 평일이 한 번도 없음 (마지막 05:00: 토요일 13:14 데몬 재시작 이후)
- 결론: 스크립트/PATH 문제 아님, **요일/시간대 문제**

**체크리스트**:
1. **요일 제한 확인**: `1-5` (평일만)인데 주말이라 안 돌 수 있음
   ```bash
   # 평일 05:00인데 오늘이 토요일이면 실행 안 됨
   0 5 * * 1-5 /path/script.sh
   
   # 확인 방법
   date +%A  # 오늘이 Saturday/Sunday인지
   crontab -l | grep "0 5.*1-5"  # 평일만 설정인지
   ```

2. **Cron 데몬 재시작 후력 확인**: 
   ```bash
   systemctl status cron  # active (running) 확인
   journalctl -u cron -n 30 --no-pager | grep RELOAD
   # 마지막 RELOAD 시간 이후 해당 시간(05:00)이 지났는지 확인
   ```

3. **다음 실행 시간 계산**:
   ```bash
   # 예: 오늘이 일요일이면 다음 05:00은 월요일
   # 평일 1-5 설정이면 주말 건너뜀
   date -d "next monday 05:00"  # 다음 평일 05:00 시각
   ```

4. **수동 실행 테스트**:
   ```bash
   cd /home/window11/stock
   python3 scripts/screener_vwma100.py --dry-run
   # 스크립트 자체 에러가 없는지 확인
   ```

5. **로그 경로 확인**:
   ```bash
   ls -lh ~/.pm_logs/screener_vwma100.log
   # 파일 없음 = 아직 실행 안 된 것 (정상)
   ```

**결론 기준**:
- 수동 실행 성공 + cron 로그에 실행 흔적 없음 → **요일/시간대 문제** 또는 **데몬 재시작 후 미도래**
- `/var/log/syslog`에 해당 시간대 실행 흔적 있음 → 로그 경로/권한 문제

### Cron vs APScheduler 구분

일부 프로젝트는 **cron이 아닌 내장 스케줄러**를 사용함:
- **stock 프로젝트**: `run_workflow.py schedule` (APScheduler 데몬)
- **특징**: `crontab -l`에 없음, `config.schedule.*` 설정 파일에 시간 정의
- **확인 방법**:
  ```bash
  ps aux | grep -E "(run_workflow|APScheduler|python.*schedule)"
  grep -r "APScheduler\|BlockingScheduler" /path/to/project/scripts/
  ```
- **권고**: SSOT(cron.md)에 "별도 cron 미필요, APScheduler로 실행" 주석 추가

**혼동 방지**: 브리핑 같은 작업이 cron에 없다고 바로 "누락" 판단 금지 → 프로젝트 코드 확인 먼저

## 출처
- 글로벌 룰: `~/project-manager/global-rules/cron.md` (전체 스케줄 SSOT)
- "cron 등록/변경은 사용자가 직접" 원칙 (cron.md)

## 지원 파일
- `references/cron-debugging-checklist.md` — cron이 등록됐는데 실행 안 될 때 RC 추적 체크리스트
- `scripts/safe-cron-update.py` — 백업 + 미리보기 + 문법검증 + 롤백 포함 일괄 변경 스크립트


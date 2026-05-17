# PM 시스템 정밀 분석 (2026-05-15)

> 분석 배경: 사용자가 "프로젝트 관리 최적화 관련해서 할게 없는지 정밀 분석해봐" 요청
> 분석 방법: pm.py status/health/tasks/validate 실행 + CLAUDE.md/projects.yaml/CURRENT_TASK.md 검토 + tmux 세션 확인 + 로그 파악

## 실행된 분석 명령어

```bash
# 통합 현황 확인
python3 pm.py status

# 전체 태스크 현황
python3 pm.py tasks

# 건강 진단
python3 pm.py health

# 태스크 일관성 검증
python3 pm.py validate

# tmux 세션 상태
tmux list-sessions -F "#{session_name}: #{session_windows} windows, #{?session_attached,attached,not attached}"

# PM 본체 파일 구조
find ~/project-manager -name "*.md" | wc -l
du -sh ~/project-manager/.git

# 프로젝트별 태스크 불일치 확인
cat ~/project-manager/docs/projects/인성이/TASK.md | grep "Current:"
cat ~/project-manager/docs/projects/인성이/CURRENT_TASK.md | grep -E "^\|" | wc -l

# cron 상태 확인 (35일+ dead job 제거 후)
crontab -l | grep -E "(pm\.py|daily_report|weekly_report|overnight)"

# 로그 파일 현황
ls -lh ~/.pm_logs/*.json | tail -5
```

## 주요 발견사항

### 1. 구조적 건전성 ✅

- **PM 본체**: 깔끔하게 정리됨
  - 209개 MD 파일
  - git 크기 6.9M (적절)
  - PREPARED_TASK.md 수정됨 (1 uncommitted)
  - docs/systems/ 디렉토리 신규 (memory-update-guide.md)

- **tmux 세션**: 10개 정상 작동
  - PM: 1 window, attached
  - 프로젝트: bea, hermes, insung, music, polistat, stock (각 1 window, not attached)
  - 한국어 세션: 인성이, 자율주행, 주식부자 (각 1 window, not attached)

- **파일 구조**: 4단계 체계 정착
  - CLAUDE.md/TASK.md/CURRENT_TASK.md/PREPARED_TASK.md/FINISHED_TASK.md

- **심링크**: `docs/projects/`에서 각 프로젝트 문서 연결 완료

### 2. 운영 효율성 ⚠️ 일부 개선 필요

**잘 되는 부분:**
- `pm.py status` - 통합 현황 (git, task, disk 한눈에)
- `pm.py health` - 건강 진단 (용량/의심항목/gitignore/venv)
- `pm.py validate` - 태스크 일관성 검증
- cron 관리 - 최근 35일+ dead job 정리로 가벼워짐

**개선 필요:**

#### 2.1 태스크 수동 동기 문제
- **증상**: 인성이 TASK.md says "Current: 5개" → 실제 CURRENT_TASK.md는 3개
- **원인**: 자식 프로젝트가 CURRENT_TASK 업데이트해도 TASK.md 요약을 갱신 안 함
- **영향**: PM이 `pm.py tasks`로 전체 현황 보더라도 개별 프로젝트 내부 불일치를 못 잡음
- **해결 방향**: PM이 자동으로 요약 갱신하는 로직 필요

#### 2.2 블로커 시각화 부족
- **증상**: `pm.py tasks`에서 블로커를 보여주지만, 어디서 막혔는지 한눈에 안 들어옴
- **원인**: 블로커별 의존성 맵(DAG)이 없어서 해소 순서 판단 어려움
- **현재 블로커**: 
  - icloud-blog: ICB-HOLD (인성이 우선)
  - 인성이: EXT-NEIGHBOR-REQUEST (집 PC 실측)
  - 자율주행: T08 (네트워크 연결), T07 (Foxglove 실행 확인)
  - music-lab: 5-19, 5-20 (⏸️ 보류), 6-1 (채널 콘텐츠 누적 후 평가)
  - HIH_2: C-175 (Notion 스케줄), C-176 (노트북 엑셀)
  - 포트폴리오: 4-5 (노트북 엑셀), 4-7 (범퍼 사진)
  - be-a-studio: BAS-57 (수동 로그인 사용자 결정 보류)
- **해결 방향**: 의존성 그래프 시각화 (graphviz DOT 출력)

#### 2.3 cron health 모니터링 부재
- **증상**: be-a-studio cron 간헐적 segfault (메모리 참고) → PM이 자동 감지 못 함
- **현재 cron**: 
  - 주식부자: 매시 13분(kr), 43분(us) / 05:53, 17:47 평일 브리핑
  - PM 공통: 07:30 md_size_check / 03:00 wsl_backup
  - be-a-studio: 05:30 run_daily.sh / 03:30 cleanup_pipeline_artifacts.py
- **해결 방향**: 각 로그의 마지막 timestamp 체크 → 24h+ 멈추면 알림

### 3. PM 역할 수행 효율성 ⚠️

#### READ 단계
- ✅ 데이터 직조회 도구 풍부 (Supabase, git, logs)
- ✅ 심링크로 빠른 문서 접근
- ⚠️ 프로젝트별 CURRENT_TASK를 일일이 열어야 함 → `pm.py tasks`로 일부 해결
- ⚠️ daily_latest.json (20K)이 존재하지만 생성 메커니즘 불명확
  - daily_report.py는 35일+ dead로 제거됨 (2026-05-12)
  - 그러나 weekly_latest.json (20K)는 최신 (2026-05-10)
  - 어떤 메커니즘으로 생성되는지 확인 필요

#### REVIEW 단계
- ✅ uncommitted 파일 감지 (현재 3개: 인성이 2, be-a-studio 1)
- ✅ validate로 태스크 불일치 감지
  - ⚠ 인성이: TASK.md Current 5개 ≠ 실제 3개
  - ⚠ Engiuniverse: 태스크 파일 누락 (CURRENT/PREPARED/FINISHED/TASK)
  - ⚠ knowledge-base: TASK.md 누락
- ⚠️ "지시 vs 실행 갭 리뷰"가 자동화되어 있지 않음 → 수동으로 커밋 확인 필요

#### RE-DIRECT 단계
- ✅ tmux send-keys로 지시 전달 가능
- ⚠️ 현재 active pane을 모르면 send-keys 타겟 불확실
- **해결 방향**: PM이 현재 작업 중인 세션/pane 트래커 필요

#### VERIFY 단계
- ⚠️ L2 hunk 검증이 완전 수동
- ⚠️ 산출물 확인(ls, ffprobe, DB query)도 수동
- **해결 방향**: 자동 검증 스크립트(`pm.py verify <commit-hash>`) 추가 가치

### 4. 아키텍처 개선 기회

#### A. 병렬 워커 활용도
- **현재**: tmux 세션 = 프로젝트 고정, pane2~ = 병렬 슬롯
- **문제**: 병렬 활용 패턴이 수동으로만 작동
- **개선**: `pm.py parallel <project> --workers 3 --file list` 같은 래퍼 가치

#### B. 태스크 의존성 관리
- **현재**: PREPARED_TASK에 `depends` 컬럼 있지만, 의존성 해소가 자동이 아님
- **문제**: 부모 태스크 완료 → 자식 `depends` 갱신 수동
- **개선**: 간단한 의존성 그래프 + 자동 의존 해제 스크립트

#### C. 리포트 자동화
- **현황**: daily_report.py, weekly_report.py가 35일+ dead로 제거됨
- **그러나**: 주간 리포트(20K)는 여전히 생성되고 있음
- **질문**: 어떤 메커니즘으로 생성되는지?
- **개선**: 리포트 생성 경로 명확화 후 PM health 통합

## 우선순위 제언

### 즉시 실행 (low-hanging fruit)
1. **태스크 요약 자동 갱신**: 자식 프로젝트에서 CURRENT_TASK 변경 시 TASK.md 요약도 업데이트하는 hook 추가
2. **uncommitted 파일 정리**: 현재 3개(인성이 2, be-a-studio 1) 커밋
3. **블로커 집계**: `pm.py blocked`로 전체 블로커 + 원인 + 해소 액션 한눈에 보기

### 중기 (high-value)
4. **cron health 모니터**: 각 cron 로그의 마지막 timestamp 체크 → 24h+ 멈추면 알림
5. **지시-실행 갭 자동 검증**: 커밋 메시지에서 태스크 ID 파싱 → 관련 파일 hunk 추출 → PM이 리뷰
6. **의존성 그래프**: PREPARED_TASK의 depends로 DOT graph 생성 → 블로커 체인 시각화

### 장기 (architectural)
7. **PM 대시보드 웹 인터페이스**: 현재 TUI지만, 웹에서 접근하면 모바일에서도 PM 가능
8. **자식 세션 결과 자동 수집**: 각 프로젝트 세션이 완료 보고를 PM DB에 직접写入 → PM이 READ 단계 스킵 가능

## 결론

현재 시스템은 이미 상당히 성숙해 있습니다. PM 오케스트레이터 역할을 수행할 수 있는 기반은 확보되어 있습니다.

다만, **자동화가 부족한 영역**(태스크 요약 갱신, 검증, cron health)을 개선하면 PM이 READ-REVIEW-RE-DIRECT-VERIFY를 더 빠르게 순환할 수 있습니다.

## 참고 명령어 (재검증 시 사용)

```bash
# 현재 상태 전체 확인
python3 pm.py status && python3 pm.py health && python3 pm.py validate

# 태스크 불일치 확인
for proj in $(ls ~/project-manager/docs/projects/); do
  echo "=== $proj ==="
  cat ~/project-manager/docs/projects/$proj/TASK.md 2>/dev/null | grep "Current:" | head -1
  cat ~/project-manager/docs/projects/$proj/CURRENT_TASK.md 2>/dev/null | grep -E "^\|" | wc -l
done

# 블로커 집계
python3 pm.py tasks | grep -A 20 "🛑 블로커"

# cron 로그 timestamp 확인
for log in ~/.pm_logs/*.log; do
  echo "=== $log ==="
  ls -l "$log"
  tail -1 "$log" | head -c 20
done
```

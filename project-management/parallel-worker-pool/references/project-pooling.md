# 프로젝트 풀링 전략 (Project Pooling)

## 워커 풀 상태 확인

```bash
# PM에서 전체 워커 상태 확인
cd ~/project-manager && python3 pm.py sessions
```

출력 예시:
```
w1 [Opus 92%] stock — 1-58 차트 마커
w2 [Opus 89%] insung_blog — REVIEW-AGGREGATOR
w3 [Opus 84%] be-a-studio — BAS-107
```

## 프로젝트 전환

### 전체 전환 (프로젝트 완료 후)
```bash
# stock → insung_blog로 전환 예시
for w in w1 w2 w3; do
  tmux send-keys -t $w "/exit" Enter
done

sleep 3

for w in w1 w2 w3; do
  tmux send-keys -t $w "cd ~/insung_blog && claude --add-dir ~/insung_blog --add-dir ~/project-manager" Enter
done
```

### 단일 워커 전환 (필요시만)
```bash
# w1만 다른 프로젝트로 전환
tmux send-keys -t w1 "/exit" Enter
sleep 3
tmux send-keys -t w1 "cd ~/be-a-studio && claude --add-dir ~/be-a-studio --add-dir ~/project-manager" Enter
```

## 프로젝트별 우선순위 규칙

### 우선순위 정의
| 순위 | 프로젝트 | 이유 | 워커 배분 |
|------|----------|------|-----------|
| 1 | stock | 테슬라 집중, 시황 민감 | w1+w2+w3 |
| 2 | insung_blog | 댓글봇/UX 개선 | w1+w2 |
| 3 | be-a-studio | 콘텐츠 통합 발행 | w1+w2+w3 |

### 우선순위 동적 조정
- **시장 개장 전**: stock 최우선 (10:00 KST)
- **마켓 마감 후**: insung_blog 우선 (16:00 KST)
- **야간**: be-a-studio 우선 (콘텐츠 큐 정리)

## 풀 관리

### 혼합 풀 (일반적)
```
w1: 주 프로젝트 핵심 작업
w2: 보조 작업 / 텍스트 / 데이터
w3: UI / 시각화 / 문서
```

### 전문 풀 (프로젝트 전환 필요 시)
```
[stock 전용 풀]
w1: 차트/시그널
w2: 백테스트/데이터
w3: UI/시각화

[insung_blog 전용 풀]
w1: 댓글봇 로직
w2: 스크롤 수집
w3: UX/UI
```

## 부하 균형

### ctx 모니터링
- 90% 초과 시 워커별 `/clear` 실행
- 같은 프로젝트에서 60분 이상 작업 시 커밋 권장
- 3개 워커 ctx가 모두 80% 이하면 병렬 늘림

### 작업 큐
PM이 작업 큐를 관리:
```
큐 예시:
1. 1-58 차트 시그널 (w1) → w2 테스트 → w3 UI
2. 1-59 모멘텀 카드 (w3) → w2 데이터 → w1 API
3. 1-60 타임라인 (w1) → w3 UI → w2 데이터
```

## 워커 할당 모범 사례

### 사례 1: 1-58 차트 시그널 병렬 작업
```bash
# 동시 할당 (3개 워커)
tmux send-keys -t w1 "sma_signals.py에 정배열/역배열 시그널 함수 만들어." Enter
tmux send-keys -t w2 "과거 매수 시그널 발동 N일 후 수익률 계산 로직." Enter
tmux send-keys -t w3 "tesla.html 차트에 매수/매도 시그널 마커 렌더링." Enter

# 순차 결과 통합 (w2→w3→w1)
# w2 완료 후 → w3이 활용 → w3 완료 후 → w1이 API로 반영
```

### 사례 2: 1-59 모멘텀 카드 작업
```bash
# 단일 워커 먼저 (UI 먼저)
tmux send-keys -t w3 "Essence 상단 3카드 UI 만들어." Enter

# 결과 활용 (w3→w1)
# w3 완료 후 w1이 API 엔드포인트 추가
```

## 장애 대응

### 워커 장애
- **세션 중단**: `/exit` → 재시작
- **ctx 꽉 참**: `/clear` → 작업 분할
- **무한 루프**: Ctrl+C → 작업 재정의

### 프로젝트 차단
- **종속성 충돌**: 병렬 작업을 순차화
- **데이터 부정합**: 작업 전 DB 백업 후 진행

## 참고 문서
- `CLAUDE.md` — 각 프로젝트의 규칙
- `pm.py` — 워커 상태 확인 명령
- `open-all.sh` — 워커 풀 시작 스크립트

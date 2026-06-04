---
name: parallel-worker-pool
description: "tmux 워커 풀 병렬 작업 관리 — 한 프로젝트에서 여러 워커 동시 작업으로 속도 최적화"
user_invocable: true
---

# 병렬 워커 풀 (Parallel Worker Pool)

**원칙**: 한 프로젝트에서 3개 워커(w1/w2/w3)가 **동시 병렬 작업**을 진행한다.

## 왜 병렬인가?

| 방식 | 속도 | 깊이 | 컨텍스트 | 사용성 |
|------|------|------|----------|--------|
| 고정 할당 (프로젝트별) | 느림 | 깊음 | 누적됨 | 관리 편함 |
| **병렬 풀 (한 프로젝트)** | **빠름** | 얕음 | **새로 시작됨** | PM이 할당 |

**사용자 선호**: "한 프로젝트에서 여러 워커가 병렬로 돌아가는 게 좋다"
- 병렬 효율성(속도) > 프로젝트 깊이
- 같은 패턴/도구를 여러 워커가 공유하면 학습됨

---

## 워커 할당 패턴

### 단일 프로젝트 집중
```
w1 → 메인 작업 (차트/시그널 등 핵심 기능)
w2 → 보조 작업 (백테스트/데이터)
w3 → 보조 작업 (UI/텍스트/문서)
```

### 작업 분배 원칙
1. **독립성** — 각 워커의 작업이 파일 충돌 방지
   - 다른 파일 작업 (w1: chart_api.py, w2: tesla_api.py, w3: tesla.html)
   - 또는 같은 파일의 다른 함수

2. **순서 의존** — w1 → w2 → w3 순으로 결과 활용
   - w1이 API 엔드포인트 만듦 → w2가 사용
   - w2가 테스트 데이터 만듦 → w3이 UI에 반영

3. **프로젝트 전환** — 한 프로젝트 끝나면 전체 워커 이동
   ```bash
   # stock → insung_blog로 전환 예시
   tmux send-keys -t w1 "/exit" Enter
   tmux send-keys -t w2 "/exit" Enter
   tmux send-keys -t w3 "/exit" Enter
   sleep 3
   for w in w1 w2 w3; do
     tmux send-keys -t $w "cd ~/insung_blog && claude --add-dir ~/insung_blog --add-dir ~/project-manager" Enter
   done
   ```

---

## PM 작업 지시 플로우

### 1. 작업 분해
```
단일 태스크(예: 1-58 차트 시그널)를 3개 독립 서브태스크로 분해:
  - w1: sma_signals.py 시그널 함수 생성
  - w2: 백테스트 데이터 생성 + 검증 로직
  - w3: 차트 시각화에 마커 렌더링
```

### 2. 동시 할당
```bash
# PM이 3개 워커에 동시 지시
tmux send-keys -t w1 "sma_signals.py에 정배열/역배열 시그널 함수 만들어." Enter
tmux send-keys -t w2 "백테스트용 가짜 데이터 생성해. N일 후 수익률 패턴 100건." Enter
tmux send-keys -t w3 "tesla.html 차트에 시그널 마커 포맷 정의해." Enter
```

### 3. 결과 통합
```
w1 완료 → w2/w3에서 활용
w2 완료 → w3 UI에 반영
w3 완료 → 전체 검증 → 커밋
```

---

## 워커 상태 확인

```bash
# PM에서 전체 워커 상태 체크
cd ~/project-manager && python3 pm.py sessions

# 개별 워커 상태 확인
tmux capture-pane -t w1 -p -S -20 | tail -10
tmux capture-pane -t w2 -p -S -20 | tail -10
tmux capture-pane -t w3 -p -S -20 | tail -10
```

---

## 장단점 인지

### 장점
- **속도**: 3배 병렬
- **컨텍스트 깊이**: 각 워커 새로 시작 → 깊은 생각 가능
- **학습 효과**: 같은 패턴 3개 워커가 동시 학습

### 단점
- **중복 작업**: 같은 패턴을 3번 반복할 가능성
- **PM 부하**: 작업 분배 + 결과 통합에 PM 시간 소요

### 완화책
- **분해 전략** — 각 워커가 할일 뚜렬하게 정의
- **코드 공유** — 결과를 API로 분리하여 재사용
- **PM 검증** — 중복 감지 시 즉시 중단

---

---

## 장애 해결 (Troubleshooting)

### Pane 수 부족 / 세션 중복

**증상**: `open-all.sh` 실행 후 pane이 4개가 아님, 또는 같은 프로젝트 세션이 2개 존재

**원인**: `open-all.sh`의 하드코딩된 영문 세션명(`stock`, `insung`)과 `projects.yaml`의 한글 프로젝트명(`주식부자`, `인성이`) 불일치

```bash
# 진단
tmux list-sessions  # 중복 세션 확인 (stock + 주식부자, insung + 인성이)
tmux list-panes -t 주식부자:1 | wc -l  # 1이면 문제 (3이어야 함)

# 해결 1: 한글 세션 삭제 후 재생성 (빠름)
tmux kill-session -t 주식부자
tmux kill-session -t 인성이
cd ~/project-manager && ./open-all.sh

# 해결 2: open-all.sh 수정 (근본) — projects.yaml의 세션명 사용
```

**예방**: `open-all.sh`와 `projects.yaml`의 세션명을 일치시킬 것. tmux는 세션명이 대소문자/유니코드敏感함.

---

## 참고 자료
- `references/parallel-strategies.md` — 병렬 작업 패턴 사례
- `references/project-pooling.md` — 프로젝트 풀링 전략

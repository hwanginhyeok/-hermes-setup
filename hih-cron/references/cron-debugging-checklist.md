# Cron 디버깅 체크리스트

cron이 등록됐는데 실행 안 될 때의 **원인 추적 절차**.

## 증상

```bash
# 1. crontab에는 있는데
crontab -l | grep screener
# 0 5 * * 1-5 cd /home/window11/stock && python3 scripts/screener_vwma100.py >> ~/.pm_logs/screener_vwma100.log 2>&1

# 2. 로그 파일이 없음
ls -lh ~/.pm_logs/screener_vwma100.log
# ls: cannot access '...': No such file or directory
```

## 체크리스트 (순서대로)

### ✅ 1. 요일 확인

```bash
# 오늘이 평일인가?
date +%A
# Saturday / Sunday → 평일 1-5 설정이면 실행 안 됨

# crontab의 요일 제한 확인
crontab -l | grep "0 5.*1-5"
# 1-5 = 월~금만
```

**결과**: 주말이면 **정상**. 다음 평일 05:00에 실행 예정.

---

### ✅ 2. Cron 데몬 재시작 후력 확인

```bash
# 데몬 상태
systemctl status cron
# ● cron.service - Regular background program processing daemon
# Active: active (running) since Sun 2026-05-17 13:14:04 KST

# 재시작 시간 이후 해당 시간(05:00)이 지났는지?
journalctl -u cron -n 30 --no-pager | grep RELOAD
# May 17 13:14:04 ... cron[161]: (window11) RELOAD (crontabs/window11)
# May 17 16:53:01 ... cron[161]: (window11) RELOAD (crontabs/window11)

# 마지막 RELOAD: 16:53 → 05:00는 이미 지남 (내일 05:00 예정)
```

**결과**: 13:14나 16:53에 재시작 → 그 시각 이후 05:00는 지남 → **내일 05:00에 실행 예정**.

---

### ✅ 3. 다음 실행 시간 계산

```bash
# 오늘이 일요일이면?
date -d "next monday 05:00"
# Mon May 18 05:00:00 AM KST 2026

# 평일 1-5 설정 → 월요일 05:00에 실행
```

---

### ✅ 4. 수동 실행 테스트 (스크립트 문제 확인)

```bash
cd /home/window11/stock
python3 scripts/screener_vwma100.py --dry-run

# 에러가 없으면 스크립트는 정상
# 에러가 있으면 스크립트 수정 필요
```

---

### ✅ 5. 로그 경로 확인

```bash
# 로그 파일이 생겼는지?
ls -lh ~/.pm_logs/screener_vwma100.log

# 파일이 없으면 아직 실행 안 된 것 (정상)
# 파일이 있으면 내용 확인
tail -20 ~/.pm_logs/screener_vwma100.log
```

---

## 결론 트리

```
수동 실행 성공?
├─ Yes → cron 문제 (요일/시간대/데몬 재시작)
│  └─ 해결: 다음 실행 시간까지 대기
└─ No → 스크립트 문제
   └─ 해결: 스크립트 수정 (PATH, import 에러 등)
```

---

## 실제 사례: screener_vwma100.py (2026-05-17)

**상황**:
- crontab: `0 5 * * 1-5` (평일 05:00)
- 현재: 일요일 17:35
- 데몬 재시작: 13:14 (토요일 오후 5시 재부팅)

**분석**:
1. 재시작 후 첫 평일 05:00 = **월요일 05:00** (내일)
2. 아직 실행 시간 안 됨 → **로그 파일 없는 것은 정상**

**결론**:
- 내일 05:00에 정상 실행 예상
- **스크립트 문제 아님**
- 요일/시간대 이슈

---

## 빠른 확인 명령어

```bash
# 한 줄로 전체 확인
echo "요일: $(date +%A)" && \
crontab -l | grep "0 5" && \
systemctl status cron | head -3 && \
ls -lh ~/.pm_logs/screener_vwma100.log 2>&1 || echo "로그 파일 없음 (아직 실행 안 됨)"
```

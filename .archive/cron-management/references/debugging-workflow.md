# Cron 디버깅 워크플로우

**Goal:** "Cron 문제" 보고가 들어왔을 때 체계적으로 원인 파악 및 해결

## 워크플로우

### STEP 1: 문제 정의 (READ)

**사용자 보고:**
- "간헐적 Segfault" → 실제로는 실행 안 될 수도 있음
- "Cron이 안 작동해" → 여러 원인 가능
- "자동화가 멈췄어" → 로그 확인 필요

**질문:**
1. 마지막 정상 실행 언제?
2. 어떤 로그/에러 메시지?
3. Cron 등록되어 있나?

### STEP 2: 기본 확인 (REVIEW)

```bash
# 1. Cron 등록 확인
crontab -l | grep <job_name>

# 2. 최근 로그 확인
ls -lht ~/.pm_logs/<job>*.log | head -3
tail -30 ~/.pm_logs/<job>*.log

# 3. 실행 권한 확인
ls -la /path/to/script.py  # 755 필요

# 4. 최근 실행 이력
journalctl --user -u <service> --since "3 days ago" -n 50 --no-pager 2>/dev/null
grep -i "job_name" /var/log/syslog 2>/dev/null | tail -20
```

### STEP 3: 원인 분석 (RE-DIRECT)

**False Positive 탐지:**

| 보고 | 실제 원인 | 확인 방법 |
|------|----------|----------|
| "Segfault" | Cron 미등록 | crontab -l |
| "자동화 멈춤" | 실행 권한 부족 | ls -la (664→755) |
| "로그 없음" | 로그 경로 잘못됨 | tail -f /dev/null |

**실제 Segfault 탐지:**
- core dump 파일 확인
- Segfault 메시지 확인
- 재현 시도

### STEP 4: 해결 (TRACK)

**Cron 미등록:**
```bash
# Cron 등록
(crontab -l 2>/dev/null; echo "MM HH * * * cd /path && command >> log 2>&1") | crontab -

# 검증
crontab -l | grep <job_name>
```

**실행 권한 부족:**
```bash
chmod +x /path/to/script.py
```

**Segfault (실제):**
- V2 개선 (에러 핸들링 + 리소스 모니터링)
- 텔레그램 알림 추가

### STEP 5: 검증 (VERIFY)

**수동 실행:**
```bash
cd /path/to/project
python3 script.py --test
```

**로그 확인:**
```bash
tail -20 logs/enrich_news_v2_20260517.log
```

**Cron 등록:**
```bash
crontab -l | grep <job_name>
```

## be-a-studio enrich_news.py 사례

**초기 보고:** "간헐적 Segfault"

**실제 원인:**
1. 로그 파일: 최근 4/28 (3주 전)
2. Cron 등록: 없음
3. 실행 권한: 664 (rw-rw-rw)

**해결:**
1. chmod +x scripts/enrich_news.py
2. Cron 등록 (05:30)
3. V2 개선 (에러 핸들링 + 리소스 모니터링)

**결과:** Cron 정상 작동

## 교훈

**False Positive 방지:**
1. 먼저 로그 파일 확인 (최근 날짜)
2. Cron 등록 확인 (crontab -l)
3. 실행 권한 확인 (ls -la)
4. 마지막으로 Segfault 확인

**세션 관리:**
- PM 세션 → READ → REVIEW → RE-DIRECT → TRACK → VERIFY
- bea 세션 → 직접 작업
- Claude CLI 응답 중 → Bash pane 사용
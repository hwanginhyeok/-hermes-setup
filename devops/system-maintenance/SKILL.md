---
name: system-maintenance
description: Automated system maintenance workflows — disk cleanup, file management, project monitoring, and cron automation for development environments.
---

# System Maintenance

> Automated maintenance patterns for development environments — disk space management, file cleanup, project monitoring, and cron-based automation.

## When to Use This Skill

Trigger this skill when:
- "cleanup", "disk space", "memory management" for projects
- "analyze disk usage", "check disk space", "why is disk full"
- "automate cleanup", "cron job", "schedule cleanup"
- "delete old files", "free up space", "reduce storage"
- "monitor project changes", "track file modifications"
- "Google Drive backup verification"
- "WSL2 disk full", "C drive 100%", "move WSL to another drive"
- "tmux sessions", "pane count wrong", "open-all.sh not creating panes correctly"

## Core Principles

### 1. Safety-First Deletion Pattern
All automated cleanup follows this sequence:
```
1. Verify work completion (DB queries, file existence checks)
2. Backup to remote storage (Google Drive, S3, etc.)
3. Confirm backup exists (rclone ls, md5 verification)
4. Only then delete local file
```

### 2. Multi-Layer Backup Verification
- **Database**: Check completion status, timestamps, status flags
- **Remote**: Verify file exists on backup location (`rclone ls`)
- **Checksum**: Compare local/remote hashes for critical files

### 3. Scheduled Automation
- **Low-impact times**: Evening (22:00), early morning (03:00)
- **Log rotation**: Prevent log file bloat (7-30 day retention)
- **Error handling**: Don't fail entire job on single file error

## Common Cleanup Patterns

### Music/Audio Files
**Work complete indicators**:
- YouTube URL populated in database
- Final rendered file exists (e.g., `final.mp4`)
- Status field = `complete` / `published`

**Example**:
```python
# Database query for completed work
cursor.execute("""
    SELECT song_id, local_path, drive_url 
    FROM suno_songs 
    WHERE status = 'complete' AND youtube_url IS NOT NULL
""")
```

### Build/Cache Directories
**Safe to delete**:
- `node_modules/.cache`
- `.npm/_cacache`, `.npm/_npx`
- `.cache/uv`, `.cache/pip`
- `.pytest_cache`, `__pycache__`

**Safe cleanup commands**:
```bash
npm cache clean --force
uv cache clean
rm -rf ~/.cache/uv
hermes checkpoints clear-legacy -f
```

### Temporary Files
**Cleanup criteria**:
- Age: 7-30 days
- Pattern: `*.tmp`, `*.temp`, `*.log.old`
- Location: Dedicated temp directories only

## Project Change Monitoring

### Automated Memory Updates
**Pattern for tracking project changes**:

```python
# 1. MD5 hash comparison for change detection
def get_file_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# 2. Compare against previous state
if current_hash != previous_state.get(key):
    changes.append({
        'project': project_name,
        'type': 'file_change',
        'file': filename,
        'timestamp': datetime.now().isoformat()
    })

# 3. Categorize by priority
priority_rules = {
    'HIGH': ['.claude/rules/', 'DIFFICULTY.md'],
    'MEDIUM': ['CLAUDE.md', 'TASK.md', 'CURRENT_TASK.md']
}
```

### Priority Levels
| Priority | Triggers | Action Required |
|-----------|-----------|----------------|
| 🚨 HIGH | Rule files, DIFFICULTY.md | Memory update required |
| 📋 MEDIUM | CLAUDE.md, TASK files | Review in next session |
| ℹ️ LOW | README, documentation | Informational |

## Disk Space Management

### Discovery Phase (Before Cleanup)
**Always start with analysis to identify the actual problem**:
```bash
# 1. Check overall disk health
df -h

# 2. Find largest directories in WSL home
du -sh ~/* 2>/dev/null | sort -hr | head -20

# 3. Check Python package bloat
du -sh ~/.local/lib/python*/site-packages/* 2>/dev/null | sort -hr | head -30

# 4. Check Windows-side WSL2 disk usage (CRITICAL for C drive issues)
du -sh /mnt/c/Users/*/AppData/Local/wsl/ 2>/dev/null

# 5. Check Windows Temp and WSL VHDX size
echo "C drive usage:"
df -h /mnt/c
echo "WSL VHDX:"
ls -lh /mnt/c/Users/*/AppData/Local/wsl/*/ext4.vhdx 2>/dev/null
```

**See `references/wsl2-disk-analysis.md` for complete WSL2 disk investigation procedures.**

## Tmux Session Management

The PM workspace uses tmux sessions with specific pane architectures:

**Standard layout**:
- `PM`: 4 panes (orchestrator)
- `bea`, `stock`, `insung`, `music`: 2 panes each (claude + bash)
- `hermes`: 2 panes (chat + bash)

**Common issues**:
- Korean/English session name conflicts (old sessions with Korean names)
- Pane count mismatches after script changes
- Sessions not rebuilding with new configuration

**Quick fix**:
```bash
# Diagnose
tmux list-sessions -F "#{session_name}: #{window_panes} panes"

# Full rebuild
cd ~/project-manager && ./open-all.sh --kill-all && ./open-all.sh
```

**See `references/tmux-session-management.md` for complete troubleshooting and architecture details.**

### Common Space Hogs
| Category | Typical Size | Cleanup Method |
|----------|--------------|----------------|
| Hermes legacy checkpoints | 5-10GB | `hermes checkpoints clear-legacy -f` |
| npm cache | 1-5GB | `npm cache clean --force` |
| Python cache | 500MB-2GB | `uv cache clean`, `pip cache purge` |
| Browser cache | 500MB-3GB | Remove specific cache dirs |
| Build artifacts | 1-10GB | Clean `node_modules/.cache` |

### Verification Steps
1. Check disk usage before cleanup: `df -h /home`
2. Run cleanup
3. Check disk usage after cleanup
4. Verify critical systems still work

## Cron Automation

### Cron Entry Pattern
```bash
# Standard pattern
M H * * * /usr/bin/python3 /path/to/script.py >> /path/to/log_$(date +\%Y\%m\%d).log 2>&1

# Example: Daily cleanup at 22:00
0 22 * * * /usr/bin/python3 /home/window11/scripts/cleanup_completed_files.py >> /home/window11/.pm_logs/cleanup_$(date +\%Y\%m\%d).log 2>&1
```

### Scheduling Best Practices
- **Avoid**: Peak hours (09:00-18:00), system boot time
- **Prefer**: Evening (21:00-23:00), early morning (02:00-05:00)
- **Log files**: Include date in filename, rotate monthly
- **Error capture**: Always include `2>&1` in redirect

### Hermes Cron vs System Cron

**Current setup uses system crontab** - verified with `crontab -l`:
```bash
# Health monitoring (every 6 hours)
0 */6 * * * /usr/bin/python3 /home/window11/project-manager/scripts/cron_health_monitor.py >> ~/.pm_logs/cron_health.log 2>&1

# Daily alert to Telegram (09:00)
0 9 * * * /usr/bin/python3 /home/window11/project-manager/scripts/cron_health_monitor.py --telegram >> ~/.pm_logs/cron_health_alert.log 2>&1
```

**Hermes cron requires Gateway running**:
```bash
# List Hermes cron jobs
hermes cron list

# Gateway status check
hermes gateway status

# Gateway not running = jobs won't fire automatically
# Start in tmux session for persistence:
tmux new -s hermes 'hermes gateway run'
```

**⚠️ Common confusion**:
- System cron (crontab) works independently
- Hermes cron requires `hermes gateway run` in background
- Logs show "Gateway is not running" → jobs won't execute
- pm-bot.py can send Telegram alerts when issues detected

## Pitfalls

### ❌ Don't Do These
- **Delete without backup verification**: Always confirm remote backup exists
- **Clear active caches mid-session**: Wait for work to complete
- **Use interactive commands in cron**: Commands that prompt will hang
- **Delete based only on age**: Check completion status first
- **Mix Korean/English tmux session names**: Causes duplicate sessions and pane count mismatches
- **Expect pane count reduction to auto-apply**: Must kill session and recreate when reducing panes in script

### ⚠️ Common Issues

**Tmux sessions not matching expected pane count**:
```bash
# Diagnose: List all sessions with pane counts
tmux list-sessions -F "#{session_name}: #{window_panes} panes"

# Common cause: Korean/English name conflicts
# Old sessions: 주식부자, 인성이, 자율주행
# Script expects: stock, insung, autonomous

# Fix: Kill old sessions and rebuild
tmux kill-session -t 주식부자
tmux kill-session -t 인성이
tmux kill-session -t 자율주행
cd ~/project-manager && ./open-all.sh
```

**Pane count reduction doesn't apply**:
- `open-all.sh` will add missing panes but won't remove extra panes
- Must kill session and recreate to reduce pane count
- Or manually remove panes: `tmux kill-pane -t session:1.3`

**Hermes cleanup hangs**:
```bash
# Wrong: Interactive prompt
hermes checkpoints clear-legacy

# Right: Force mode
hermes checkpoints clear-legacy -f
```

**WSL disk space not reflecting after cleanup**:
- WSL caches disk usage; needs restart to reflect
- Windows side: `wsl --shutdown` to see actual space freed
- VHDX files don't auto-shrink; need manual compaction or export/import

**C drive 100% due to WSL2**:
- WSL2 virtual disk can grow to 100GB+ and doesn't auto-shrink
- Check: `du -sh /mnt/c/Users/*/AppData/Local/wsl/`
- Solution: Move WSL2 to D drive or compact VHDX (see `references/wsl2-disk-analysis.md`)

**Disk usage volatility - WSL2 VHDX bloat**:
- Real WSL usage: 60GB / 1007GB (6%)
- VHDX file size: 77GB (wastes ~17GB)
- Dynamic VHD grows on file create, doesn't shrink on delete
- **Fix**: Monthly VHDX compaction required
  ```bash
  # Inside WSL: Zero free space
  sudo dd if=/dev/zero of=/zero bs=1M || rm -f /zero
  sudo poweroff -f  # WSL shutdown

  # PowerShell (Admin): Compact VHDX
  wsl --shutdown
  Optimize-VHD -Path "C:\Users\window11\AppData\Local\wsl\{GUID}\ext4.vhdx" -Mode Full
  ```

**Infrastructure monitoring setup**:
- Created `infra_monitor.sh` script (now in `~/.hermes/scripts/`)
- Checks C drive usage (90% threshold), WSL2 VHDX size (70GB threshold), Windows Temp (10GB threshold)
- Registered as Hermes cron job: `인프라 모니터링` (every 6 hours)
- Delivers to `origin` (PM session) when thresholds exceeded
- Logs health data to `~/.pm_logs/infra_health.log`

**Monitoring alerts not firing**:
- `cron_health_monitor.py` checks logs but doesn't fix issues
- C drive usage NOT monitored (only cron logs)
- **Recommendation**: Add disk usage check to cron_health_monitor.py

**PowerShell command failures from WSL**:
- Avoid complex PowerShell pipes from Bash (escaping hell)
- Use simple commands or create .ps1 scripts on Windows side first

**Cron jobs not running**:
- Check cron service: `systemctl status cron`
- Verify crontab: `crontab -l`
- Check logs: `tail -f /var/log/cron.log` or user log file

## Templates and Scripts

Use reference scripts in `scripts/` directory:
- `cleanup-template.py` — Base cleanup script with backup verification
- `memory-monitor.py` — Project change monitoring framework
- `cron-setup.sh` — Cron installation helper
## References

- `references/wsl2-disk-analysis.md` - Complete WSL2 disk investigation and recovery procedures
- `references/tmux-session-management.md` - PM + project session architecture, pane count management, and troubleshooting
- `references/wsl2-locale-and-input-issues.md` - WSL locale configuration, Korean input issues in tmux, UTF-8 setup
- `references/cleanup-patterns.md` - Project-specific cleanup workflows
- `references/hermes-cron-migration-guide.md` - Migrating from system crontab to Hermes cron with examples

## Verification

After any maintenance task:
1. **Disk space check**: `df -h /home`
2. **Critical services**: Restart and verify (systemd services)
3. **Project functionality**: Run one test command per project
4. **Log review**: Check for errors in cleanup logs

## Related Skills

- `cron-management` — Cron job lifecycle and debugging (absorbed below)
- `kanban-worker` — Worker pool orchestration (for parallel cleanup)

---

## 부록: Cron Job Management & Monitoring

이 섹션은 `cron-management` 스킬에서 흡수되었습니다.

### 하이브리드 크론 인프라

사용자는 세 가지 실행 메커니즘의 하이브리드 크론 인프라를 보유하고 있습니다. 예약된 자동화를 검토할 때 항상 세 가지 모두 확인하세요.

| 타입 | 목적 | 상태 확인 | 로그 위치 |
|------|----------|--------------|--------------|
| **Hermes cron** | AI 기반 예약 작업 (`hermes cron` 통해) | `hermes cron list` | 대상으로 전달 (local/email) |
| **Hermes Gateway** | Hermes cron 작동에 필수 | `hermes gateway status` | `~/.hermes/logs/gateway.log` |
| **crontab** | 전통적 Unix 예약 작업 | `crontab -l` | `~/.pm_logs/<name>.log` |
| **systemd timers** | 서비스 수준 반복 작업 | `systemctl --user list-units --type=service` | `journalctl -u <service>` |

### 빠른 확인 워크플로우

1. **Hermes Gateway 상태 확인** (필수 - 실행 안 하면 Hermes cron 작동 안 함)
   ```bash
   hermes gateway status
   # "not running"이면 Hermes cron 작업이 실행되지 않음
   # 시작: tmux new -s hermes 'hermes gateway run'
   ```

2. **Hermes cron 작업 나열**
   ```bash
   hermes cron list
   ```
   확인: `next_run_at`, `last_run_at`, `last_status`

3. **전통적 crontab 확인**
   ```bash
   crontab -l
   ```

4. **systemd 서비스 확인** (해당 시)
   ```bash
   systemctl --user list-units --type=service
   systemctl --user status <service-name>
   ```

### 일반적인 문제

#### Gateway 미작동으로 Hermes cron 실패
**증상**: Hermes cron 작업이 실행되지 않음

**원인**: `hermes gateway run`이 백그라운드에서 실행 중이 아님

**해결**:
```bash
# tmux 세션에서 시작 (지속성)
tmux new -s hermes 'hermes gateway run'

# 또는 open-all.sh 사용
cd ~/project-manager && ./open-all.sh
```

#### Hermes vs System Cron 혼동
- System cron (crontab)은 cron 데몬으로 독립 실행
- Hermes cron은 `hermes gateway run` 필요
- 로그에 "Gateway is not running" → 작업 실행 안 됨

#### Hermes cron에서 스크립트 경로 요구사항
Hermes cron은 **`~/.hermes/scripts/` 하의 상대 경로만** 허용:

```bash
# ❌ 실패: 절대 경로
hermes cron create "0 */2 * * *" "desc" --script "/absolute/path/script.sh"

# ✅ 성공: 스크립트를 복사 후 파일명만 사용
cp /path/to/script.sh ~/.hermes/scripts/
hermes cron create "0 */2 * * *" "desc" --script "script.sh"
```

#### 전달 대상 선택
- `origin`: PM 주의 필요한 알림 (디스크 공간, 치명적 실패)
- `local`: 루틴 로깅 (뉴스 수집, 브리핑)
- `telegram`: pm-bot 통해 Telegram 전송

### 로그 위치 규칙

모든 crontab 작업은 이 로깅 패턴을 따름:
```
~/.pm_logs/<job_name>.log                    # 롤링 로그
~/.pm_logs/<job_name>_YYYYMMDD.log          # 날짜 스탬프 로그 (보고서, 백업)
```

---

## 부록: WSL 환경 설정 및 문제 해결

이 섹션은 `wsl-setup` 스킬에서 흡수되었습니다.

### 한글 입력 안 됨 (tmux)

**증상**: tmux 세션에서 한글 입력이 불가능하거나 깨짐

**해결**:

1. 한국어 로케일 설치 (sudo 필요):
```bash
sudo sed -i 's/^# ko_KR.UTF-8 UTF-8/ko_KR.UTF-8 UTF-8/' /etc/locale.gen
sudo locale-gen ko_KR.UTF-8
sudo update-locale LANG=ko_KR.UTF-8
```

2. .bashrc에 환경변수 추가:
```bash
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8
export LC_CTYPE=ko_KR.UTF-8
```

3. .tmux.conf에 UTF-8 설정 추가:
```bash
set -g default-terminal "screen-256color"
set -ga terminal-overrides ",*256col*:Tc"
```

4. tmux 세션 재시작:
```bash
tmux kill-server
tmux new -s test
```

### systemd 서비스 동작 안 함

**증상**: `systemctl start` 명령이 실패

**해결**: `/etc/wsl.conf`에 systemd 활성화
```ini
[boot]
systemd=true
```

WSL 재시작 (PowerShell):
```powershell
wsl --shutdown
```

### GPU 접근 불가

**확인**:
```bash
nvidia-smi
```

**해결**: Windows에서 NVIDIA WSL 드라이버 설치 (Linux가 아님)
- https://developer.nvidia.com/cuda/wsl

### 성능 최적화

- 모델 파일을 Linux home(~/.ollama/models/)에 저장 - /mnt/c/ 접근 느림
- GPU 앱 닫기 - WSL이 Windows와 VRAM 공유
- Network: Ollama은 localhost:11434에서 Windows에서도 접근 가능

---

## Appendix: Windows C 드라이브 정리

이 섹션은 `c-drive-cleanup` 스킬에서 흡수되었습니다.

### 문제 증상

- C 드라이브가 갑자기 ~10GB 증가함
- Chrome AI 가중치 파일이 용량 점유

### 원인 분석

| 순위 | 항목 | 용량 | 상태 |
|--------|--------|--------|------|
| 1 | Chrome AI 가중치 | 3.4GB | 누적 |
| 2 | Git objects (be-a-studio) | 590MB | 정상 |
| 3 | Git objects (HIH_2) | 1.5GB | 정상 |
| 4 | 로그 파일 (.pm_logs) | 254MB | 정상 |
| 5 | Python PyTorch | 996MB | 정상 |
| 6 | CUDA libraries | 523MB | 정상 |

### 해결 방법

**1. Chrome AI 가중치 정리 (즉시 3.4GB 확보)**:
```bash
rm -rf ~/.config/google-chrome/OptGuideOnDeviceModel/*/{weights,cache,adapter,encoder}.bin
rm -rf ~/.config/chrome-suno/OptGuideOnDeviceModel/*/{weights,cache,adapter,encoder}.bin
```
- **효과**: 3.4GB 확보
- **주의**: 웹 브라우저 캐시로 재생성될 수 있음
- **권장**: Chrome 설정에서 AI features 비활성화

**2. Git repository 최적화 (200~500MB 확보)**:
```bash
cd ~/be-a-studio
git gc --aggressive --prune=now --expire=now
```
- **효과**: 200~500MB 확보
- **주의**: 오래된 pack 파일 삭제

**3. 로그 파일 정리 (50MB 확보)**:
```bash
# 30일 이상 로그 삭제
find ~/.pm_logs -name "*.log*" -mtime +30 -delete
```

**4. 미사용 프로젝트 삭제 (5~10GB 확보)**:
```bash
# 삭제 전 확인
du -sh ~/physical_AI_Engiuniverse
du -sh ~/icloud-blog
du -sh ~/icloud

# 확인 후 삭제
rm -rf ~/physical_AI_Engiuniverse
rm -rf ~/icloud-blog
rm -rf ~/icloud
```

### 정기 관리

```bash
# 매월 1일 크론 등록
0 2 1 * * bash ~/project-manager/scripts/cleanup_completed_files.py
```

### 참고

- `scripts/cleanup_completed_files.py` - Music Lab/Politics Stats 정리
- Git GC 주기적 실행 권장 (월 1회)

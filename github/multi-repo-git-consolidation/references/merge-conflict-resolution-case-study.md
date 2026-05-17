# Merge Conflict Resolution Case Study: 포트폴리오 Project

**Date**: 2026-05-12
**Scenario**: Cross-machine editing (desktop vs laptop) caused rebase conflict during push

## Problem Statement

After successful batch commit/push of 9/10 projects, `포트폴리오` project failed:

```bash
cd /home/window11/포트폴리오
git pull --rebase
# CONFLICT (content): Merge conflict in CURRENT_TASK.md
# CONFLICT (content): Merge conflict in FINISHED_TASK.md
# CONFLICT (content): Merge conflict in TASK.md
# error: could not apply ac26a88... chore: 태스크 좀비 라인 정리 — 4건 FINISHED 이동
```

## Conflict Analysis

### File 1: CURRENT_TASK.md

**Conflict markers:**
```markdown
<<<<<<< HEAD
| B1-01 | 자산 인벤토리 작성 — 있는 것 / 대기 / 잠재 전수 등록 + 품질 등급 | 2026-04-24 |  |
=======
> **노트북 작업 필요**: 4-5는 엑셀 필요. 4-7은 범퍼 사진만 핸드폰에서 옮기면 완료.
| 4-5 | SVPWM 수치 검증 — 효율 향상(1%/4%) + 온도 저감 확인 | 2026-04-04 | 노트북 엑셀 |
| 4-7 | 시험기획 이미지 업그레이드 | 2026-04-06 | 범퍼 사진 |
>>>>>>> ac26a88 (chore: 태스크 좀비 라인 정리 — 4건 FINISHED 이동)
```

**Root cause:**
- Desktop (HEAD): Added new B1-01 task (inventory work)
- Laptop (ac26a88): Removed old 4-5/4-7 tasks (they were moved to FINISHED)

**Resolution strategy**: Union merge - keep B1-01 from desktop, retain 4-5/4-7 from laptop with blocker notes

### File 2: FINISHED_TASK.md

**Conflict:**
```markdown
<<<<<<< HEAD
| 4-8 | EOP 다이나모 이미지 적용 — 전원통합 회로도 + 응답성 시험 | 2026-04-07 | dynamo-schematic + dynamo-response 추출 |
| 6-4 | 프로필 사진 준비 — 증명사진 WebP 변환, About 섹션 연결 | 2026-04-08 | profile.webp |
=======
| 4-8 | EOP 다이나모 이미지 적용 | 2026-04-07 | dynamo-schematic + dynamo-response 추출 완료 |
| 6-4 | 프로필 사진 준비 | 2026-04-08 | 증명사진_사복.png → profile.webp, About 섹션 연결 |
>>>>>>> ac26a88 (chore: 태스크 좀비 라인 정리 — 4건 FINISHED 이동)
```

**Root cause**: Desktop had more verbose notes, laptop had concise notes

**Resolution strategy**: Take laptop version (concise), as desktop notes were redundant

### File 3: TASK.md

**Conflict:**
```markdown
<<<<<<< HEAD
- Current: 1개 (blocked: 0)
- Prepared: 21개 (B1: 8, B2: 1, B4: 1, B5: 4, JD-Apple: 4, JD-xAI: 3)
- Finished: 34개
=======
- Current: 2개 (blocked: 2)
- Prepared: 11개 (P1: 1, P2: 7, P3: 3)
- Finished: 9개
>>>>>>> ac26a88
```

**Root cause**: Task count divergence after "좀비 라인 정리" (zombie task cleanup)

**Resolution strategy**: Recalculate actual counts from merged files

## Resolution Execution

```bash
# Step 1: Read all conflicted files to understand full context
read_file CURRENT_TASK.md
read_file FINISHED_TASK.md
read_file TASK.md

# Step 2: Write merged versions manually
# Strategy: Prioritize laptop's cleanup work, add desktop's new B1-01
write_file CURRENT_TASK.md  # Merged 3 tasks
write_file FINISHED_TASK.md  # 38 tasks (laptop count)
write_file TASK.md  # Recalculated: Current 3, Prepared 11, Finished 38

# Step 3: Stage resolved files
git add CURRENT_TASK.md FINISHED_TASK.md TASK.md

# Step 4: Continue rebase (hit editor error)
git rebase --continue
# error: There was a problem with the editor 'editor'
# Please supply the message using either -m or -F option

# Step 5: Manual commit with message
git commit -m "Merge conflict resolution - 집/노트북 병합"
git rebase --continue

# Step 6: Verify and push
git status  # Should show "rebasing" completed
git push
# Success: b2b85d7..master
```

## Key Learnings

1. **Union merge for task lists**: When machines add different tasks, merge both sets
2. **Recalculate aggregates**: After merge, always recalculate summary counts
3. **Editor fallback**: If `git rebase --continue` triggers editor error, use `git commit -m` directly
4. **Preserve cleanup work**: Laptop's "좀비 라인 정리" removed stale tasks - keep this cleanup
5. **Update metadata**: Change "최종 수정" date to resolution date

## Prevention

```bash
# Before starting work on a machine, always:
cd /project/path
git status  # Check for uncommitted changes
git pull --rebase  # Sync with remote

# After finishing work:
git add -A
git commit -m "$(date +'%Y-%m-%d') Work from $(hostname)"
git push
```

## Verification Commands

```bash
# After resolution, verify:
cd /home/window11/project-manager
python3 pm.py status
# Expected: "✅ 전체 정상"
# Expected: "Git: ✅ 0 uncommitted"
```

## Related Skills

- **multi-repo-git-consolidation**: Main workflow for batch git operations
- **systematic-debugging**: 4-phase root cause analysis (used to understand conflict)

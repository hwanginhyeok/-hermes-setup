# 모델 업데이트 패턴

HiH 스킬의 모델 버전을 일관되게 업데이트하는 패턴과 검증 방법.

## 업데이트 대상

### 1. 스킬 파일 (SKILL.md)

모델 참조가 있는 모든 스킬:
- hih-dual: builder (Opus), reviewer (GLM), Codex
- hih-design-fix: builder (Opus), reviewer (GLM)
- hih-design-new: builder (Opus), reviewer (GLM)
- hih-glm: GLM 버전 (정확도 우선으로 최신 유지)

### 2. Config 파일

두 곳 모두 업데이트 필요:
- 전역: `~/.hermes/config.yaml`
- 프로필: `~/.hermes/profiles/pm/config.yaml`

## 업데이트 절차

### STEP 1: 스킬 파일 업데이트

```bash
# hih-dual 예시
# Sonnet 4.6 → Opus 4.8, GLM 4.7 → GLM 5.0, Codex 4.0 → 5.5
skill_manage action=patch name=hih-dual old_string="..." new_string="..."
```

**패턴**:
- 모델 표준어: `Opus 4.8`, `GLM 5.0`, `Codex 5.5`
- SKILL.md 내용 검색: grep으로 모델 버전 찾기

### STEP 2: Config 파일 업데이트

```python
#!/usr/bin/env python3
from pathlib import Path
import yaml

# 전역 config
config_path = Path.home() / ".hermes" / "config.yaml"
# 프로필 config
profile_path = Path.home() / ".hermes" / "profiles" / "pm" / "config.yaml"

# GLM default 업데이트
content = (config_path).read_text()
content = content.replace('default: glm-4.7', 'default: glm-5.0')
(config_path).write_text(content)

# custom_providers에 신규 추가
# codex, opus 등 필요한 provider 추가
```

**custom_providers 추가 패턴**:
```yaml
custom_providers:
- name: codex
  base_url: https://api.openai.com
  key_env: OPENAI_API_KEY
  api_mode: openai_chat
  model: gpt-4o-5.5-preview
- name: opus
  base_url: https://api.anthropic.com
  key_env: ANTHROPIC_API_KEY
  api_mode: anthropic_messages
  model: claude-opus-4-8
```

### STEP 3: 검증

**스킬 파일 검증**:
```python
#!/usr/bin/env python3
from pathlib import Path

# 모델 버전 추출
skill_path = Path.home() / ".hermes" / "skills" / "hih-dual" / "SKILL.md"
content = skill_path.read_text()

if "Opus 4.8" in content:
    print("✅ Opus 4.8 발견")
if "GLM 5.0" in content:
    print("✅ GLM 5.0 발견")
if "5.5" in content:
    print("✅ 5.5 발견 (Codex)")
```

**스킬 경로 검색 패턴** (여러 경로에 분산 가능):
```python
skills_base = Path.home() / ".hermes" / "skills"
skill_paths = [
    skills_base / skill_name / "SKILL.md",           # 직접 경로
    skills_base / "ui-ux" / skill_name / "SKILL.md", # 카테고리 하위
    skills_base / "project-management" / skill_name / "SKILL.md",
]

for path in skill_paths:
    if path.exists():
        print(f"✅ 발견: {path}")
        break
else:
    print("❌ 없음")
```

**config.yaml 검증**:
```bash
# 전역 config
grep "default:" ~/.hermes/config.yaml | head -1

# custom_providers 확인
grep -A 3 "custom_providers:" ~/.hermes/config.yaml | head -10
```

## 검증 사례: 2026-06-02

### 업데이트 대상
- hih-dual: Opus 4.8 + GLM 5.0 + Codex 5.5
- hih-design-fix: Opus 4.8 + GLM 5.0
- hih-design-new: Opus 4.8 + GLM 5.0 + 3자 리뷰 추가

### 검증 결과
- 스킬 파일: 21/21 정상 ✅
- 모델 버전: 모든 스킬에서 업데이트 확인 ✅
- config.yaml: 전역 + 프로필 모두 업데이트 ✅

### 발견된 패턴

1. **스킬 경로 다양성**: 스킬은 여러 경로에 분산 가능
   - 직접: `~/.hermes/skills/hih-dual/`
   - 카테고리: `~/.hermes/skills/ui-ux/hih-design-fix/`

2. **find + pathlib 패턴**: 실제 경로 찾을 때
   ```bash
   find ~/.hermes/skills -name 'SKILL.md' -path '*hih-dual*'
   ```

3. **config 이중 구조**: 전역 + 프로필 모두 확인 필요
   - 프로필이 전역보다 우선순위 높음

## Git 동기화

```bash
# 변경된 스킬 커밋
cd ~/.hermes/skills
git add hih-dual/SKILL.md ui-ux/hih-design-fix/SKILL.md ui-ux/hih-design-new/SKILL.md
git commit -m "feat: update hih skills to latest models"
git push origin main

# 노트북 동기화 스크립트
bash ~/sync_skills_from_repo.sh
```

## Pitfalls

1. **경로 찾기 오류**: 특정 경로만 확인하면 누락 발생
   - 해결: 여러 경로 패턴 검색 또는 find 명령 사용

2. **config 우선순위**: 프로필 config가 전역보다 우선
   - 해결: 두 곳 모두 확인 후 업데이트

3. **hih-glm 정확도 우선**: GLM 5.0 → 5.1로 유지하는 케이스
   - 해결: 스킬 설명에 "정확도 우선" 명시

4. **세션 적용 지연**: config 변경은 새 세션에서만 적용
   - 해결: 사용자에게 명시

## 관련 사례

- 2026-06-02: GLM 5.0, Opus 4.8, Codex 5.5 업데이트
  - 스킬: hih-dual, hih-design-fix, hih-design-new
  - Config: custom_providers에 codex, opus 추가
  - 검증: Python 자동화 스크립트로 스킬 21개 전체 확인
# Hermes 환경 설정 + 스킬 동기화

PC와 노트북 간 Hermes 환경을 동일하게 유지합니다.

## 구조

- `skills/`: 스킬 (gstack, hih 등)
- `config.yaml`: 환경 설정 템플릿
- `SOUL.md`: 페르소나
- `skins/`: 스킨 (gothic-neon, hanbok, fantasy)
- `profiles/`: 프로필 (pm)

## 사용법

### 초기 설정

1. 레포 클론:
```bash
git clone https://github.com/hwanginhyeok/hermes-setup.git ~/.hermes/skills
```

2. 설정 적용:
```bash
cd ~/.hermes
cp skills/config.yaml ./config.yaml
cp skills/SOUL.md ./SOUL.md
cp -r skills/skins/* ./skins/
```

3. 개인 설정 (.env):
```bash
# ~/.hermes/.env
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
Z_AI_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### 업데이트

```bash
cd ~/.hermes/skills
git pull origin main
```

### 설정 변경

1. PC에서 설정 변경 후 커밋:
```bash
git add .
git commit -m "feat: 스킨 추가"
git push origin main
```

2. 노트북에서 풀:
```bash
git pull origin main
```

## 스킬 목록

- **gstack**: 46개 AI 엔지니어링 스킬 (office-hours, ship, qa 등)
- **hih**: 12개 PM/작업 스킬 (hih-dev, hih-task, hih-git 등)
- **기타**: 28개 스킬 (creative, mlops, github 등)

# Hermes Skills + Environment Sync Workflow

## Context

**Problem:**
- PC와 노트북에서 Hermes 환경 동일하게 유지 필요
- 스킬(29MB) + 환경 설정(16MB) 분리 관리 불편
- 수동 복사 어려움

## Solution: Unified Hermes Setup Repo

**Repository:** https://github.com/hwanginhyeok/-hermes-setup

**Structure:**
```
~/.hermes/skills/
├── skills/              # 29MB (gstack v1.39.2.0 + hih 12개)
├── config.yaml          # 환경 설정 템플릿
├── SOUL.md              # 페르소나
├── skins/               # 스킨 3종
│   ├── gothic-neon.yaml
│   ├── hanbok.yaml
│   └── fantasy.yaml
├── README.md            # 사용법
└── .gitignore
```

## Setup Workflow (PC → 노트북)

### 1. Clone
```bash
cd ~
git clone https://github.com/hwanginhyeok/-hermes-setup.git
```

### 2. Link Skills
```bash
cd -hermes-setup
ln -sf $(pwd) ~/.hermes/skills
```

### 3. Copy Environment Files
```bash
cp config.yaml ~/.hermes/
cp SOUL.md ~/.hermes/
cp -r skins/* ~/.hermes/skins/
```

### 4. Update
```bash
cd ~/.hermes/skills
git pull
```

## Security Considerations

**Files to NEVER commit:**
```
.env                           # API keys, secrets
auth.json / auth.lock          # Authentication tokens
sessions/                      # Session data
logs/                          # Logs (may contain sensitive data)
state.db*                      # Local databases
profiles/                      # User profiles with auth
```

**Files SAFE to commit:**
```
config.yaml.template          # Template without secrets
SOUL.md                       # Persona (public)
skins/                        # Theme configs
SKILL.md                      # Skill documentation
```

## Session Context

**2026-05-17 PM Session:**
- Issue: Hermes 환경 동기화 필요
- Solution: 통합 레포 생성 (skills + config)
- Status: ✅ Successfully pushed to GitHub
- Security: Removed profiles/ to avoid secret exposure
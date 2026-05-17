## Git 정리 보고서

### 전체 현황

```
총 N개 프로젝트 중 uncommitted 파일:
  ⚠️ 프로젝트명       : N파일   (마지막 커밋: N일 전)
  ⚠️ 프로젝트명       : N파일   (마지막 커밋: 오늘)
  ⚠️ 프로젝트명       : N파일   (마지막 커밋: 어제)
  ⚠️ 프로젝트명       : N파일   (마지막 커밋: N일 전) ← 주의
  ✅ 프로젝트명      : 0파일   (N일 전)
  ✅ 프로젝트명  : 0파일   (N일 전)
```

### 원격 저장소 설정

모든 프로젝트가 GitHub에 연동됨:
- hwanginhyeok/repo1
- hwanginhyeok/repo2
- hwanginhyeok/repo3
...

### Hermes 설정 비교 (if applicable)

| 항목 | ~/.hermes (실사용) | hermes-eval/.hermes (평가용) |
|------|-------------------|------------------------------|
| Git 관리 | ❌ 없음 | ❌ 없음 |
| 모델 | zai-glm/glm-4.7 | anthropic/claude-opus-4.6 |
| custom_providers | zai-glm 등록됨 | 없음 (기본 설정) |
| 설정 버전 | v23 | 템플릿 (주석 많음) |
| 용도 | 실사용 | 평가/테스트용 |

### 권장 사항

1. **[프로젝트명] 긴급 커밋 필요**: N파일 uncommitted → [사유]
2. **[프로젝트명]**: 정기 커밋 권장 (N파일)
3. **Hermes 자체는 Git으로 관리 안 됨**: ~/.hermes도 Git으로 관리하면 설정 변경 추적 가능
4. **[기타]**: [비고]

일괄 push/진행하시겠습니까?

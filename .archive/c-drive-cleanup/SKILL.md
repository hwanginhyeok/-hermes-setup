---
name: c-drive-cleanup
description: C 드라이브 용량 관리 스킬
tags: [troubleshooting, maintenance, cleanup]
---

# C 드라이브 용량 관리

## 문제 증상
- C 드라이브가 갑자기 ~10GB 증가함
- Chrome AI 가중치 파일이 용량 점유

## 원인 분석
| 순위 | 항목 | 용량 | 상태 |
|--------|--------|--------|------|
| 1 | Chrome AI 가중치 | 3.4GB | 누적 |
| 2 | Git objects (be-a-studio) | 590MB | 정상 |
| 3 | Git objects (HIH_2) | 1.5GB | 정상 |
| 4 | 로그 파일 (.pm_logs) | 254MB | 정상 |
| 5 | Python PyTorch | 996MB | 정상 |
| 6 | CUDA libraries | 523MB | 정상 |

## 해결 방법

### 1. Chrome AI 가중치 정리 (즉시 3.4GB 확보)
```bash
# Chrome AI 가중치 삭제
rm -rf ~/.config/google-chrome/OptGuideOnDeviceModel/*/{weights,cache,adapter,encoder}.bin
rm -rf ~/.config/chrome-suno/OptGuideOnDeviceModel/*/{weights,cache,adapter,encoder}.bin
```
- **효과**: 3.4GB 확보
- **주의**: 웹 브라우저 캐시로 재생성될 수 있음
- **권장**: Chrome 설정에서 AI features 비활성화

### 2. Git repository 최적화 (200~500MB 확보)
```bash
cd ~/be-a-studio
git gc --aggressive --prune=now --expire=now
```
- **효과**: 200~500MB 확보
- **주의**: 오래된 pack 파일 삭제

### 3. 로그 파일 정리 (50MB 확보)
```bash
# 30일 이상 로그 삭제
find ~/.pm_logs -name "*.log*" -mtime +30 -delete
```
- **효과**: ~50MB 확보

### 4. 미사용 프로젝트 삭제 (5~10GB 확보)
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
- **효과**: 5~10GB 확보
- **주의**: 삭제 전 git/데이터 백업 확인

## 정기 관리
```bash
# 매월 1일 크론 등록
0 2 * * bash ~/project-manager/scripts/cleanup_completed_files.py
```

## 참고
- `scripts/cleanup_completed_files.py` - Music Lab/Politics Stats 정리
- Git GC 주기적 실행 권장 (월 1회)

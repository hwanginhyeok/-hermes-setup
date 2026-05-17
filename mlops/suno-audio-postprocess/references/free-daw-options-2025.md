# 무료 DAW 옵션 2025 (Suno 후처리용)

> 리서치 날짜: 2026-05-14

## 실전 3강

| DAW | 가격 | 트랙 | 플랫폼 | 비고 |
|-----|------|------|--------|------|
| **Cakewalk Sonar Free** | 무료 (BandLab 계정) | 무제한 | Win + Mac | 옛 Sonar. 2025-06 재출시. VST3, 64-bit, 스펙트럼 분석기 포함. 가장 강력한 무료 DAW. |
| **Tracktion Waveform Free 13.5** | 무료 (제약 없음) | 무제한 | Win/Mac/**Linux** | 유일한 Linux 트랙 무제한 무료 DAW. 내보내기/워터마크 제한 없음. |
| **Reaper** | 60일 평가 후도 전기능 | 무제한 | Win/Mac/Linux | 시작 시 5초 nag 화면만. 사실상 무제한. 양심값 $60. |

## 제한 있는 무료

| DAW | 핵심 제약 | 비고 |
|-----|----------|------|
| BandLab 웹 | 16트랙, 브라우저 전용 | AI 스플리터(스템 분리) 내장. 설치 불필요. |
| Pro Tools Intro | 8+8+8 트랙 | AAX 서드파티 가능. 옛 "First" 교체작. |
| SoundBridge | 10트랙 | 영상 작업 강함. |
| Ableton Live Lite | 8트랙 | 하드웨어 구매 시에만 입수 가능. |

## 단종/변경 (주의)

- **Studio One Prime/Artist** → 2024-10 폐지. Pro 단일 에디션으로 통합됨.
- **Cakewalk by BandLab** → 2025-08 종료. **Cakewalk Sonar Free**로 이관.

## 환경별 추천

- **Windows 풀 프로덕션** → Cakewalk Sonar Free
- **Linux(WSL2 외부)** → Waveform Free 13.5
- **WSL2/CLI 자동화** → Demucs + Pedalboard + Matchering (DAW 없이 가능)
- **브라우저/모바일 스케치** → BandLab 웹

## WSL2 환경 정리

WSL2에서는 GUI DAW 직접 실행 불가. 선택지:
1. VNC(`DISPLAY=:1`)로 Linux GUI DAW 실행 (Waveform Free 설치 후)
2. Windows 호스트에 Cakewalk Sonar Free 설치 후 `/mnt/c/...`로 파일 공유
3. **CLI 파이프라인** (권장) — Demucs + Pedalboard + Matchering으로 DAW 불필요

## Sources
- [Cakewalk Sonar Free - BPB](https://bedroomproducersblog.com/2025/06/23/cakewalk-sonar-free/)
- [Waveform Free 13.5 - Mixdown](https://mixdownmag.com.au/news/tracktion-releases-waveform-free-13-5-the-only-truly-unrestricted-free-daw/)
- [Reaper License](https://www.reaper.fm/purchase.php)
- [Studio One Prime 단종 - PreSonus Support](https://support.presonus.com/hc/en-us/articles/210050033)

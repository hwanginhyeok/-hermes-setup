# Suno 후처리 의존성 버전 & 트러블슈팅

## 검증된 조합 (WSL2 Ubuntu 24.04, 2026-05-13)

| 패키지 | 버전 | 비고 |
|--------|------|------|
| Python | 3.12 | |
| torch | 2.10.0+cu128 | CUDA 버전이어도 CPU로 Demucs 돌림 |
| torchaudio | 2.11.0+cpu | **CPU 버전 필수** — CUDA 버전 설치 시 import 실패 |
| demucs | 4.0.1 | |
| pedalboard | 0.9.22 | |
| matchering | 2.0.6 | |
| soundfile | 0.13.1 | |
| ffmpeg | 7:6.1.1 (apt) | |
| torchcodec | — | **설치 불필요** — Demucs CLI용이지만 Python API 우회로 필요 없음 |

## 설치 순서

```bash
# 1. 기본 패키지
pip install demucs pedalboard matchering soundfile pydub

# 2. torchaudio CPU 버전 (CUDA 환경이어도)
pip install torchaudio --index-url https://download.pytorch.org/whl/cpu

# 3. ffmpeg (이미 있으면 skip)
sudo apt install ffmpeg
```

## 에러 → 원인 → 수정 매핑

### `OSError: libcudart.so.13: cannot open shared object file`
- **원인**: torchaudio가 CUDA 빌드로 설치됨
- **수정**: `pip install --force-reinstall torchaudio --index-url https://download.pytorch.org/whl/cpu`

### `ImportError: TorchCodec is required for save_with_torchcodec`
- **원인**: `python -m demucs` CLI가 torchaudio.save() 호출 → torchcodec 필요
- **수정**: CLI 대신 Python API + soundfile 직접 저장 방식 사용 (SKILL.md 코드 참조)

### `RuntimeError: Could not load libtorchcodec`
- **원인**: torchcodec 설치해도 ffmpeg 공유 라이브러리 버전 불일치
- **수정**: torchcodec 필요 없음. Python API 방식으로 우회.

### `AttributeError: 'BagOfModels' object has no attribute 'name'`
- **원인**: `get_model()` 반환값이 BagOfModels. `.name` 없음
- **수정**: `.name` → `.sources` 사용 (`['drums', 'bass', 'other', 'vocals']`)

### Demucs 분리 중 `100%` 표시 후 에러
- **원인**: 분리 연산 자체는 성공, 저장 단계에서 torchaudio 실패
- **수정**: Python API로 전환하면 분리+저장 모두 정상 작동

## 성능 메모

- htdemucs: 10초 클립 → 분리 8초 (CPU). GPU 있으면 ~1초
- htdemucs_ft (fine-tuned): 품질 약간 높음, 속도 동일
- mdx_extra: 보컬 분리 품질 최상. 4-스템 아닌 2-스템 (vocals/no-vocals)
- 풀곡 3분 → CPU에서 약 2분 소요

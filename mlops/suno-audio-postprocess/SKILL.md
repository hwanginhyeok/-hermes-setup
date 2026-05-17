---
name: suno-audio-postprocess
description: "Suno AI 출력물 후처리 파이프라인 — Demucs 스템 분리 + Pedalboard 장르별 이펙트 + Matchering 마스터링. CLI 자동화로 DAW 없이 구현."
version: 1.0.0
author: session-2026-05-13
license: MIT
metadata:
  hermes:
    tags: [Audio, Suno, Demucs, Pedalboard, Mastering, PostProcess, Music]
    related_skills: [audiocraft-audio-generation, ollama-local-llm]
---

# Suno 오디오 후처리 파이프라인

Suno AI가 생성한 WAV/MP3를 스템 분리 → 장르별 이펙트 → 마스터링까지 CLI 자동화로 처리하는 파이프라인.
DAW 없이 Python CLI만으로 구현. `~/music-lab/scripts/postprocess.py`가 실제 구현체.

## 핵심 스택

| 도구 | 버전 | 역할 |
|------|------|------|
| **Demucs** (Meta) | 4.0.1 | 4-스템 분리 (drums/bass/other/vocals) |
| **Pedalboard** (Spotify) | 0.9.22 | EQ/컴프/리버브/코러스/딜레이/디스토션/비트크러시 |
| **Matchering** | 2.0.6 | 레퍼런스 트랙 기반 마스터링 |
| **soundfile** | 0.13.1 | WAV 읽기/쓰기 (torchaudio 대체) |
| **ffmpeg** | 7.x | 포맷 변환 (MP3→WAV 등) |

## 파이프라인 흐름

```
입력 WAV/MP3
    ↓
[1] Demucs htdemucs — 4-스템 분리
    drums.wav / bass.wav / other.wav / vocals.wav
    ↓
[2] 각 스템별 Pedalboard 이펙트 (장르 프리셋)
    - Gain → Compressor → EQ (low cut/shelf/high shelf/high cut) →
      Distortion/Bitcrush → Chorus → Delay → Reverb → Limiter
    ↓
[3] 4스템 믹싱 (합산)
    ↓
[4] 마스터 버스: Compressor → LUFS 타겟 게인 → Limiter
    ↓
출력 WAV
```

## 장르 프리셋별 특성

| 장르 | 보컬 | 드럼 | 베이스 | 특수 이펙트 | 타겟 LUFS |
|------|------|------|--------|-------------|-----------|
| jazz | 따뜻한 리버브, 낮은 컴프 | 브러시 질감, 소프트 | 고역컷 800Hz | — | -14 |
| ballad | 보컬 +3dB, 코러스, 풍부한 리버브 | 소프트, 리버브 | — | 보컬 코러스 | -14 |
| pop | 보컬 밝게, 고역 +3dB | 펀치, 저역 +3dB | — | — | -11 |
| rock | 디스토션, 고역 부스트 | 저역 +4dB, 강한 컴프 | 디스토션 | 전 스템 드라이브 | -10 |
| hiphop | 드라이, 고역 +2dB | 저역 +5dB, 크랙 | 808 저역 +6dB | — | -9 |
| edm | 밝은 고역, 리버브 | 타이트 저역 | 고역컷 300Hz | Chorus+Delay | -8 |
| bossa | 부드러운 보컬, 코러스 | 퍼커션 느낌 | 부드러운 컴프 | 보컬/other 코러스 | -15 |
| lofi | 비트크러시, 고역컷 6kHz | 비트크러시, 고역컷 5kHz | 고역컷 400Hz | 전체 빈티지 | -14 |

## 사용법

```bash
# 기본 (스템 분리 포함)
python scripts/postprocess.py input.wav --genre jazz

# 스템 분리 없이 빠른 처리 (~1초)
python scripts/postprocess.py input.wav --genre lofi --skip-stems

# 커스텀 프리셋 JSON
python scripts/postprocess.py input.wav --preset my_preset.json

# 프리셋 목록
python scripts/postprocess.py --list-presets

# 출력 경로 지정
python scripts/postprocess.py input.wav --genre hiphop --output output.wav
```

## Demucs 직접 API 호출 방식 (torchaudio CLI 우회)

Demucs 4.0.1에서 `python -m demucs` CLI는 torchaudio/torchcodec으로 저장하려다 실패.
**soundfile로 직접 저장하는 Python 코드가 정답.**

```python
import torch
import soundfile as sf
from demucs.pretrained import get_model
from demucs.apply import apply_model
from demucs.audio import AudioFile

model = get_model('htdemucs')   # BagOfModels — .sources 속성으로 스템 이름 접근
model.eval()

wav = AudioFile(input_path).read(streams=0, samplerate=44100, channels=2)
ref = wav.mean(0)
wav_input = (wav - ref.mean()) / ref.std()

with torch.no_grad():
    sources = apply_model(model, wav_input[None], progress=True)[0]

sources = sources * ref.std() + ref.mean()

for i, name in enumerate(model.sources):   # ['drums', 'bass', 'other', 'vocals']
    audio = sources[i].numpy().T           # (channels, samples) → (samples, channels)
    sf.write(f'{output_dir}/{name}.wav', audio, 44100)
```

## Pedalboard 이펙트 체인 패턴

```python
from pedalboard import (
    Pedalboard, Gain, Compressor, HighpassFilter, LowShelfFilter,
    HighShelfFilter, LowpassFilter, Distortion, Bitcrush,
    Chorus, Delay, Reverb, Limiter
)

board = Pedalboard([
    Gain(gain_db=2.0),
    Compressor(threshold_db=-18, ratio=2.5, attack_ms=10, release_ms=100),
    HighpassFilter(cutoff_frequency_hz=80),          # 저역 컷
    LowShelfFilter(cutoff_frequency_hz=200, gain_db=2.0),
    HighShelfFilter(cutoff_frequency_hz=8000, gain_db=-1.0),
    Reverb(room_size=0.35, dry_level=0.8, wet_level=0.15),
    Limiter(threshold_db=-1.0),
])

# (channels, samples) 형태로 입력
audio = audio.reshape(1, -1) if audio.ndim == 1 else audio
processed = board(audio, sample_rate)
```

## 커스텀 프리셋 JSON 구조

```json
{
  "description": "내 커스텀 프리셋",
  "stems": true,
  "vocal": {
    "gain_db": 2.0,
    "compressor_threshold_db": -18,
    "compressor_ratio": 2.5,
    "eq_low_cut_hz": 80,
    "eq_high_shelf_hz": 8000,
    "eq_high_shelf_gain_db": 1.5,
    "reverb_room_size": 0.4,
    "reverb_wet": 0.2,
    "limiter_db": -1.0
  },
  "drums": { "gain_db": 0.0, "..." : "..." },
  "bass":  { "gain_db": 0.0, "..." : "..." },
  "other": { "gain_db": -1.0, "..." : "..." },
  "master": {
    "compressor_threshold_db": -14,
    "compressor_ratio": 2.0,
    "limiter_db": -1.0,
    "target_lufs": -14
  }
}
```

지원하는 config 키: `gain_db`, `compressor_threshold_db`, `compressor_ratio`,
`compressor_attack_ms`, `compressor_release_ms`, `eq_low_cut_hz`, `eq_low_shelf_hz`,
`eq_low_shelf_gain_db`, `eq_high_shelf_hz`, `eq_high_shelf_gain_db`, `eq_high_cut_hz`,
`distortion_db`, `bitcrush_bit_depth`, `chorus_rate_hz`, `chorus_depth`,
`delay_seconds`, `delay_feedback`, `delay_mix`, `reverb_room_size`, `reverb_wet`,
`reverb_width`, `limiter_db`

## 처리 시간 기준 (CPU, WSL2)

| 작업 | 10초 클립 | 3분 풀곡 |
|------|-----------|---------|
| 스템 분리 (htdemucs) | ~8초 | ~2분 |
| Pedalboard 이펙트 | <1초 | ~5초 |
| 합계 (전체 파이프라인) | ~9초 | ~2분 |
| --skip-stems 모드 | <1초 | ~5초 |

## 설치

```bash
pip install demucs pedalboard matchering soundfile
# torchaudio CPU 버전 (CUDA 없는 환경)
pip install torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## Pitfalls

1. **`python -m demucs` CLI 저장 실패** — Demucs 4.0.1 + torchaudio 2.11 조합에서
   `torchaudio.save()`가 torchcodec을 요구하다 실패. CLI 대신 Python API + soundfile 직접 저장으로 우회. 위 코드 패턴 사용.

2. **torchaudio가 CUDA 버전으로 설치된 경우** — `libcudart.so.13` 찾지 못해 import 실패.
   `pip install torchaudio --index-url https://download.pytorch.org/whl/cpu`로 CPU 버전 재설치.

3. **BagOfModels에 `.name` 속성 없음** — `get_model('htdemucs')`는 `BagOfModels`를 반환.
   `.name` 대신 `.sources`로 스템 이름 접근 (`['drums', 'bass', 'other', 'vocals']`).

4. **스템 믹싱 시 길이 불일치** — 각 스템의 샘플 수가 약간 다를 수 있음.
   합산 시 `min(stem_a.shape[1], stem_b.shape[1])`으로 길이 맞추고 슬라이싱.

5. **Demucs 스템 블리드** — 재생성 방식이라 drums 스템에 보컬 잔향, vocals 스템에 악기 노이즈 포함.
   각 스템에 NoiseGate 추가하거나 EQ로 보완. 완벽한 분리는 불가.

6. **LUFS 조정은 RMS 근사치** — `process_master()`의 LUFS 계산은 실제 BS.1770 측정이 아닌
   RMS 기반 근사. 정밀 마스터링이 필요하면 Matchering으로 대체.

## 관련 파일

- 구현체: `~/music-lab/scripts/postprocess.py`
- 가이드: `~/music-lab/docs/suno-advanced-guide.md` (Suno 프롬프트 + 후처리 워크플로우)
- 참조: `references/suno-postprocess-deps.md` — 의존성 버전/설치 트러블슈팅
- 참조: `references/free-daw-options-2025.md` — 무료 DAW 옵션 비교 (Waveform Free, Sonar Free, Reaper)

# Post-Processing Pipeline — DAW & CLI Tools

> Suno output → stem separation → mix/master → publish.
> Last updated: 2026-05-14

## Working Pipeline Script

**`~/music-lab/scripts/postprocess.py`** — full automated post-processing.

```
Usage:
  python scripts/postprocess.py input.wav --genre jazz
  python scripts/postprocess.py input.wav --genre lofi --skip-stems
  python scripts/postprocess.py input.wav --preset custom.json
  python scripts/postprocess.py --list-presets
```

### Pipeline flow
```
Suno output (WAV/MP3)
    ↓
Demucs htdemucs → 4 stems (drums / bass / other / vocals)
    ↓
Per-stem Pedalboard effects (EQ + compress + reverb + genre-specific)
    ↓
4-stem sum → master bus (compress + LUFS target + limiter)
    ↓
Final WAV output
```

### 8 genre presets

| Preset | Character | Target LUFS |
|--------|-----------|-------------|
| `jazz` | Warm lows, subtle reverb, preserved dynamics | -14 |
| `ballad` | Vocal-forward, lush reverb, soft chorus | -14 |
| `pop` | Punchy drums, bright vocals, loud | -11 |
| `rock` | Distortion, aggressive drums, punch | -10 |
| `hiphop` | 808 bass boost, dry vocals, crack hats | -9 |
| `edm` | Bright leads, tight bass, sidechain feel | -8 |
| `bossa` | Nylon guitar texture, soft vocals | -15 |
| `lofi` | Bitcrush, vintage warp, tape reverb | -14 |

### Per-stem processing (each preset configures these independently)

| Stem | Typical chain |
|------|--------------|
| **vocals** | gain → compressor → HPF → low shelf → high shelf → chorus/opt → reverb → limiter |
| **drums** | gain → compressor → low shelf boost → high shelf → reverb → limiter |
| **bass** | gain → compressor → LPF (cut highs) → limiter (no reverb on bass) |
| **other** | gain → compressor → EQ → reverb → limiter |

Custom presets: pass a JSON file with `--preset`. Keys: `vocal`, `drums`, `bass`, `other`, `master`. Each stem config supports: `gain_db`, `compressor_threshold_db`, `compressor_ratio`, `eq_low_cut_hz`, `eq_low_shelf_hz`, `eq_low_shelf_gain_db`, `eq_high_shelf_hz`, `eq_high_shelf_gain_db`, `eq_high_cut_hz`, `reverb_room_size`, `reverb_wet`, `chorus_rate_hz`, `chorus_depth`, `delay_seconds`, `delay_feedback`, `delay_mix`, `distortion_db`, `bitcrush_bit_depth`, `limiter_db`.

---

## Demucs — Stem Separation

### Installed version
- `demucs 4.0.1` with `htdemucs` model (4 stems: drums, bass, other, vocals)

### Critical: Direct API call (NOT CLI)

The Demucs CLI (`python -m demucs`) crashes on save due to torchaudio/torchcodec incompatibility.
Use the **direct Python API** instead:

```python
import torch
import numpy as np
import soundfile as sf
from demucs.pretrained import get_model
from demucs.apply import apply_model
from demucs.audio import AudioFile

model = get_model('htdemucs')  # Returns BagOfModels
model.eval()
sources = model.sources  # ['drums', 'bass', 'other', 'vocals']

wav = AudioFile(input_path).read(streams=0, samplerate=44100, channels=2)
ref = wav.mean(0)
wav_input = (wav - ref.mean()) / ref.std()

with torch.no_grad():
    separated = apply_model(model, wav_input[None], progress=True)[0]

separated = separated * ref.std() + ref.mean()

# Save with soundfile (NOT torchaudio.save)
for i, name in enumerate(model.sources):
    audio = separated[i].numpy().T  # (samples, channels)
    sf.write(f"{name}.wav", audio, 44100)
```

### Pitfalls

1. **`get_model()` returns `BagOfModels`** — access `.sources` directly on it, NOT on sub-models
2. **torchaudio.save is broken** — torch 2.10+cu128 + torchaudio CPU = torchcodec crash. Use soundfile instead.
3. **Normalize before separation** — `(wav - ref.mean()) / ref.std()`, then denormalize after
4. **GPU available but CPU works fine** — htdemucs on CPU: ~7s per 10s clip (~0.7x realtime)

### torchaudio fix

If `import torchaudio` fails with `libcudart.so.13` error:
```bash
pip install --user --break-system-packages --force-reinstall \
  torchaudio --index-url https://download.pytorch.org/whl/cpu
```
This installs CPU-only torchaudio that doesn't need CUDA runtime.

---

## Pedalboard — Audio Effects (Spotify)

Installed: `pedalboard 0.9.22`. Works perfectly.

### Available effects
```
Gain, Compressor, Limiter, Reverb, Chorus, Delay, Phaser,
HighpassFilter, LowpassFilter, HighShelfFilter, LowShelfFilter,
PeakFilter, Distortion, Bitcrush, NoiseGate, Clipping,
GSMFullRateCompressor, MP3Compressor, PitchShift, Convolution,
IIRFilter, Invert, Mix, Chain, ExternalPlugin (VST3)
```

### Usage pattern
```python
from pedalboard import Pedalboard, Compressor, Reverb, Gain, Limiter

board = Pedalboard([
    Gain(gain_db=2.0),
    Compressor(threshold_db=-18, ratio=3.0),
    Reverb(room_size=0.3, wet_level=0.15),
    Limiter(threshold_db=-1.0),
])

# audio shape: (channels, samples) for stereo, or (samples,) for mono
processed = board(audio_float32, sample_rate)
```

---

## Other Installed CLI Audio Tools

| Package | Version | Purpose |
|---------|---------|---------|
| `matchering` | 2.0.6 | LUFS loudness matching (import error on 3.12 — use Pedalboard gain instead) |
| `pydub` | 0.25.1 | Audio segment manipulation |
| `soundfile` | 0.13.1 | WAV/FLAC read/write |
| `ffmpeg` | 7:6.1.1 | Format conversion, normalization |
| `fluidsynth` | 2.3.4 | MIDI → audio rendering |

---

## Free DAW Options (2025)

### Tier 1 — No crippling limits

| DAW | Price | Tracks | Platform | Notes |
|-----|-------|--------|----------|-------|
| **Cakewalk Sonar Free** | Free (BandLab account) | Unlimited | Win + Mac | Former Sonar. VST3, 64-bit. 2025-06 re-released. |
| **Tracktion Waveform Free 13.5** | Free | Unlimited | **Win/Mac/Linux** | Only unlimited free DAW on Linux. |
| **Reaper** | 60-day eval → nag screen | Unlimited | Win/Mac/Linux | $60 conscience fee. Fully functional. |

### Tier 2 — Restricted

| DAW | Limitation |
|-----|-----------|
| **BandLab Web** | 16 tracks, browser, AI Splitter |
| **Pro Tools Intro** | 8+8+8 tracks |
| **Ableton Live Lite** | 8 tracks, hardware purchase only |

### Dead
- **Studio One Prime** — Killed 2024. PreSonus went Pro-only.

### Recommendation
- **Windows**: Cakewalk Sonar Free
- **Linux/WSL2**: Waveform Free 13.5 or Reaper
- **CLI automation**: Use the postprocess.py pipeline (this is what music-lab uses)

# Suno v4.5 / v5 / v5.5 Feature Summary

> Quick reference for features not yet in the main SKILL.md Suno section.
> Full guide: `~/music-lab/docs/suno-advanced-guide.md` (793 lines, 2026-05-13)

## Model Timeline

| Model | Released | Key Change |
|-------|----------|------------|
| v4.5 | 2025-05-01 | 1000-char style field, 8-min songs, natural language prompts |
| v4.5+ | 2025-07-17 | Vocal Swap, Instrumental Flip, Spark from Playlist |
| v5 | 2025-09 | Korean/multilingual pronunciation overhaul |
| v5.5 | 2025-late | Voice Persona (clone from 3-5 min dry vocal upload) |

## Style Prompt (v4.5+)

- **Limit**: 1,000 chars (up from 200). Silent truncation if exceeded.
- **Priority**: First 20-30 words are most important. Put genre + vocal + mood + key instruments there.
- **Natural language works better** than keyword lists in v4.5+. Use descriptive sentences, NOT commands.
  - Bad: `Create an upbeat pop track...`
  - Good: `Upbeat pop track with bright analog synths and gated drums...`
- **Rule of thumb**: 1-2 genres / 2-3 instruments / 1-2 moods. More = generic noise.

## Negative Prompt (Exclude Styles)

- Field name: "Exclude Styles" in Custom Mode
- Max 200 chars
- Use for: unwanted instruments, genres, vocal effects
- Example: `EDM drum, autotune, choir, crowd vocals, electric guitar`

## Korean Language (v5+)

- v5 dramatically improved Korean pronunciation. Use v5+ for Korean vocals.
- Always write lyrics in Hangul (never romanized)
- Keep 6-10 syllables per line
- Add `clear pronunciation` or `high fidelity vocals` to style prompt

## Structure Tags with Timing

New in v4.5+: specify duration for sections
```
[Intro - solo piano, 12s]
[Verse 1]
[Chorus - full band]
[Solo: Tenor Sax, 16s]
[Bridge - building]
[Outro - fade]
[End]
```

## Backup Vocal Syntax (v5+)

- `{backup vocals: "ohh ahh"}` — group vocal directive
- ` (whispered)`, `(belted)`, `(falsetto)` — inline vocal delivery

## Key Features

### Extend
- Appends new sections to existing song
- Preserves previous section's tone/mix at ~99%
- Good for: good verse+chorus but weak bridge/outro

### Cover
- Keeps melody + structure, changes genre/instruments/vocals
- v4.5+ handles genre transitions smoothly
- Use for: same song in 5 different genres for channel diversity

### Persona (Voice Character Lock)
- Create from existing song: Library → ⋮ → Create Persona
- v5.5: Upload your own voice (3-5 min dry vocal, no reverb/BGM)
- Use across multiple songs for consistent vocal identity

### Vocal Swap (v4.5+)
- Keep lyrics + melody, swap vocalist only
- Library → ⋮ → Vocal Swap

### Instrumental Flip (v4.5+)
- Keep vocals, change backing track genre
- Combine with Vocal Swap for full genre migration

### Spark from Playlist
- Feed 5-10 of your songs as reference → generate new song in same style
- Good for channel identity consistency

### Stem Extraction Pro
- Up to 12 stems: drums, bass, lead vox, bg vox, guitar, piano, synths, strings, brass, effects, etc.
- Output: MP3 / WAV / Tempo-Locked WAV / MIDI / WAV+MIDI combo
- **Warning**: AI regeneration-based separation, NOT subtraction. Bleed and level imbalance are common. Always EQ + gain-stage in DAW before use.

## Production Pipeline

- Generate 3-5 variants → pick best → Extend for structure → Stem Export → DAW post-process
- Track prompts + results in `suno_runs.jsonl` for version control
- Use `songs/{number}_{name}/suno_prompt_final.md` for prompt storage
- Final mastering target: -14 LUFS loudness

## Sources

- Suno Help Center (help.suno.com)
- Jack Righteous guides (jackrighteous.com)
- HookGenius guides (hookgenius.app)
- Civitai ultimate v4.5 how-to
- Full guide at `~/music-lab/docs/suno-advanced-guide.md`

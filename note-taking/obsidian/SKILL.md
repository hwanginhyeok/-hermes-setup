---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
platforms: [linux, macos, windows]
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.

## WSL / Headless Linux Installation

Obsidian is not in apt/snap/flatpak on a base WSL install. Use AppImage extraction (no FUSE needed):

```bash
# Download
wget -q "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.8.10/Obsidian-1.8.10.AppImage" -O ~/apps/Obsidian.AppImage
chmod +x ~/apps/Obsidian.AppImage

# Extract (avoids FUSE dependency — common in WSL)
cd ~/apps && ./Obsidian.AppImage --appimage-extract
# Creates squashfs-root/ directory

# Launch (VNC display required — check with xdpyinfo)
cd ~/apps/squashfs-root && APPDIR=$PWD DISPLAY=:1 ./obsidian --no-sandbox --disable-gpu &
```

**Key flags:**
- `APPDIR=$PWD` — required; the AppRun script resolves binaries relative to this
- `--no-sandbox` — required in WSL/container environments
- `--disable-gpu` — avoids GPU crashes in VNC/headless
- `DISPLAY=:1` — target VNC display

**First-run vault setup:**
- Obsidian shows "Open folder as vault" dialog on first launch
- Pre-create vault directory with `.obsidian/` subdir to skip initial prompts
- Vault path persists in `~/.config/obsidian/vault.json` across restarts

**Running Obsidian without a terminal present (remote access):**
- Access the VNC session (see memory for Tailscale URL)
- Obsidian will already be running if launched before — check taskbar
- To relaunch: open terminal in VNC → `cd ~/apps/squashfs-root && APPDIR=$PWD ./obsidian --no-sandbox --disable-gpu &`

## Vault for Project Content Curation

Obsidian works well as a content reservoir / curation interface:
- **Dataview plugin**: SQL-like queries over frontmatter (`TABLE quality_score, brand FROM "Reservoir" WHERE status = "inbox" SORT quality_score DESC`)
- **Kanban plugin**: Drag-and-drop status boards; each item is a wikilink
- **Folder structure**: `Inbox/` (new), `Reservoir/` (curated top N%), `Rejected/` (with reasons), `Published/` (done), `Dashboard/`, `Templates/`
- **Python automation**: Scripts generate notes with YAML frontmatter; user browses/selects in Obsidian
- **Plugin installation**: Create `.obsidian/plugins/<name>/manifest.json` + `community-plugins.json`. Actual `.js` files are auto-downloaded on first Obsidian launch when community plugins are enabled.

### Content Note Frontmatter Schema
```yaml
---
id: SRC-20260514-001
title: "제목"
source: "TechCrunch"
source_type: rss           # rss | youtube
brand: dg                  # an | dg
category: 테크_AI_개발
quality_score: 8.5
status: inbox              # inbox → reservoir → selected → planned → rendered → published
reject_reason: ""          # filled when status=rejected
tags: [AI, 개발]
collected: 2026-05-14
published_card_id: ""      # DG-20260514-01 when published
---
```

### Key Plugins for Content Management
- **Dataview**: SQL-like queries over frontmatter
- **Kanban**: Drag-and-drop status boards from markdown lists

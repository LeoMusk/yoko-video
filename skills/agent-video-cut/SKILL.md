---
name: agent-video-cut
description: Agent-planned short video editing and repurposing workflow for local spoken videos, keynote clips, demos, livestream excerpts, and source material. Use when Codex/Claude needs to turn an input video into a high-quality short-form clip by using multimodal understanding or extracted frames/transcripts, planning the viral angle and timeline, writing a Hyperframes HTML composition, installing/running Hyperframes CLI, validating layout, and rendering MP4 output.
---

# Agent Video Cut

Turn a local video into a short-form edited clip by combining agent planning with Hyperframes rendering.

The agent owns content understanding, viral-angle selection, timeline design, Chinese/English copy, and visual composition. Hyperframes owns deterministic rendering. Do not treat ASR/OCR as the product core; use them only when the task needs exact timestamps or text recovery.

## Required Capabilities

- Use video understanding directly when available.
- If direct video understanding is unavailable, extract representative frames with `ffmpeg` and inspect them visually.
- Use ASR/transcription only when exact speech timing matters. Hyperframes provides `npx hyperframes transcribe`, and other ASR tools are acceptable.
- Use `npx hyperframes` for CLI operations. It auto-installs from npm when needed.
- Require local `ffmpeg`/`ffprobe` and Node.js. Run `npx hyperframes doctor` when unsure.

## Quick Workflow

1. Create an isolated work directory for the edit.
2. Copy or stage the source video under `public/assets/`.
3. Inspect source metadata with `ffprobe`.
4. Understand the video using direct multimodal perception, extracted frames, ASR, or a mix.
5. Write `storyboard.json`: viral angle, target duration, scenes/cards, text overlays, source-video timing.
6. Build `public/index.html` as a Hyperframes composition.
7. Validate with `npx hyperframes lint`, `npx hyperframes inspect`, and snapshots.
8. Render with `npx hyperframes render`.
9. Re-encode sparse-keyframe source videos before final render if Hyperframes warns about seek failures.

For the full command-level SOP, read [references/sop.md](references/sop.md).

## Default Output

Unless the user specifies otherwise:

- Format: `9:16`, `1080x1920`, `30fps`
- Duration: `25-45s` for social clips
- Audio: keep source audio when the speaker is the authority
- Layout: source video top/background, agent-written cards at the 60-80% vertical band
- Bottom safe area: leave space for platform captions/buttons
- Style: high-contrast tech editorial, large readable text, one accent color per card

## Planning Rules

- Lead with a concrete hook in the first 1-3 seconds.
- Preserve authority moments: speaker face, product demo, slide title, or key visual proof.
- Convert source material into a viewer-relevant angle; do not merely summarize.
- Prefer 3-5 cards for a 30s clip.
- Each card must carry one idea only.
- Let cards intentionally cover noisy or redundant source subtitles when useful.
- Avoid placing important text in the bottom 12-15% of the frame.
- If the source already has large burned-in captions, use your overlays to add interpretation, not duplicate the same text.

Read [references/timeline-and-style.md](references/timeline-and-style.md) before designing a new visual style or layout.

## Hyperframes Build Contract

Create a `public/index.html` composition with:

- A root element with `data-composition-id`, `data-duration`, `data-fps`, `data-width`, and `data-height`.
- Timed video/audio elements using `data-start`, `data-duration`, and `data-track-index`.
- `data-has-audio="true"` on the source video when the video contributes audio.
- Timed overlay/card elements with class `clip`.
- One paused GSAP timeline registered as `window.__timelines["<composition-id>"]`.
- No `Math.random()`, `Date.now()`, async timeline construction, or infinite repeats in render paths.

Use [assets/templates/hyperframes-index.html](assets/templates/hyperframes-index.html) as a starting point when building a fresh composition.
Copy [assets/vendor/gsap.min.js](assets/vendor/gsap.min.js) into `public/vendor/gsap.min.js` when using the template, or replace the script path with another local GSAP copy.

## Quality Gates

Before final delivery:

- `npx hyperframes lint .` has no errors.
- `npx hyperframes inspect . --samples 8 --json` returns `ok: true`.
- Capture snapshots at hook, middle, and final card moments.
- Visually confirm faces are not badly cropped.
- Confirm platform bottom safe area is preserved.
- Confirm text is readable on mobile and does not collide with source captions unless intentionally covering them.
- Confirm final MP4 has expected dimensions, duration, and audio via `ffprobe`.

Read [references/quality-gates.md](references/quality-gates.md) for common fixes.

## Report

Return:

- Final MP4 path
- `storyboard.json` path
- `public/index.html` path
- Validation summary
- Any accepted warnings, such as dense timeline warnings in a proof of concept

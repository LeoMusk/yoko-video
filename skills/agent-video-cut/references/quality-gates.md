# Quality Gates and Fixes

## Hyperframes Lint

Run:

```powershell
npx hyperframes lint .
```

Fix errors before rendering. Warnings may be acceptable for proofs of concept, but report them.

Common issues:

- `video_missing_muted`: add `muted` for silent video or `data-has-audio="true"` for source audio.
- `timed_element_missing_clip_class`: add class `clip` to timed overlays.
- `timeline_track_too_dense`: acceptable for quick prototypes; split cards into sub-compositions for production.
- `font_family_without_font_face`: use generic font stacks or add local `@font-face` files.

## Layout Inspect

Run:

```powershell
npx hyperframes inspect . --samples 8 --json
```

Fix:

- Text outside cards
- Text clipped by fixed-height boxes
- Cards outside canvas
- Faces hidden by overlays
- Important text in bottom platform-safe area

If source video intentionally scales beyond its clipping container for a slow zoom, add `data-layout-allow-overflow` to the video element.

## Snapshot Review

Capture at least three moments:

```powershell
npx hyperframes snapshot . --at 1.2 --out ..\snapshot-hook.png
npx hyperframes snapshot . --at 12 --out ..\snapshot-mid.png
npx hyperframes snapshot . --at 25 --out ..\snapshot-end.png
```

Review:

- Hook is understandable without audio.
- Speaker or important object remains visible.
- Text is readable at phone size.
- Cards are high enough to avoid platform description overlays.
- Overlays intentionally cover source captions only when adding higher-value interpretation.

## Render Warnings

If Hyperframes warns about sparse keyframes:

```powershell
ffmpeg -y -i assets\source.mp4 `
  -c:v libx264 -preset fast -crf 18 -r 30 -g 30 -keyint_min 30 `
  -movflags +faststart -c:a copy assets\source-gop30.mp4
```

Update the composition to use `source-gop30.mp4` and render again.

## Final MP4 Check

Run:

```powershell
ffprobe -v quiet -print_format json -show_streams -show_format "..\output.mp4"
```

Confirm:

- Correct aspect ratio
- Correct duration
- Video stream exists
- Audio stream exists when expected
- File size is reasonable for the platform

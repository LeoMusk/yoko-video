# Agent Video Cut SOP

Use this command-level workflow when editing a source video into a short-form clip.

## 1. Create Workspace

Use an isolated directory per clip:

```powershell
$root = "experiments/<clip-name>"
New-Item -ItemType Directory -Force -Path "$root\public\assets" | Out-Null
Copy-Item -LiteralPath "<input-video>" -Destination "$root\public\assets\source.mp4" -Force
```

Do not edit the original source file in place.

## 2. Check Tools

```powershell
npx hyperframes --help
npx hyperframes doctor
ffprobe -v quiet -print_format json -show_streams -show_format "$root\public\assets\source.mp4"
```

`npx hyperframes` installs Hyperframes automatically if it is not already installed.

## 3. Understand the Video

Prefer direct multimodal video understanding when available. If not, extract frames:

```powershell
$frames = "$root\analysis_frames"
New-Item -ItemType Directory -Force -Path $frames | Out-Null
ffmpeg -y -i "$root\public\assets\source.mp4" `
  -vf "fps=1,scale=960:-1" `
  "$frames\frame_%03d.jpg"
```

For short clips, inspect frames around likely hooks: start, scene changes, speaker closeups, slide titles, and visible captions.

Use ASR only when exact wording/timing matters:

```powershell
npx hyperframes transcribe "$root\public\assets\source.mp4" --out "$root\transcript.json"
```

If ASR is unavailable, do not fabricate exact quotes. Use visible captions and frame-level understanding as approximate source evidence.

## 4. Plan the Storyboard

Write `$root/storyboard.json` with:

```json
{
  "schemaVersion": 1,
  "source": {
    "path": "public/assets/source.mp4",
    "durationSec": 59.1,
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "analysisMode": "agent video understanding + extracted frames"
  },
  "composition": {
    "id": "short-video",
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "durationSec": 29,
    "format": "9:16"
  },
  "viralAngle": {
    "oneSentence": "The viewer-relevant takeaway.",
    "hook": "The first 1-3 seconds."
  },
  "cards": [
    {
      "id": "hook",
      "startSec": 0,
      "endSec": 3,
      "intent": "Open with the viral framing.",
      "title": "Short title",
      "detail": "One explanatory sentence."
    }
  ]
}
```

Keep the storyboard honest: include only claims supported by the video or by sources the user provided.

## 5. Build Hyperframes Composition

Start from `assets/templates/hyperframes-index.html` or write equivalent HTML.

Typical structure:

```text
public/
  index.html
  assets/
    source.mp4
  vendor/
    gsap.min.js
```

Important rules:

- Add `data-has-audio="true"` to the video if its audio is used.
- Add class `clip` to timed overlays.
- Register a paused GSAP timeline.
- Keep platform-safe space at the bottom.
- Use one card idea per timed section.
- Copy the skill asset `assets/vendor/gsap.min.js` into `public/vendor/gsap.min.js` when using the bundled template.

## 6. Validate

```powershell
cd "$root\public"
npx hyperframes lint .
npx hyperframes inspect . --samples 8 --json
npx hyperframes snapshot . --at 1.2 --out ..\snapshot-hook.png
npx hyperframes snapshot . --at 12 --out ..\snapshot-mid.png
npx hyperframes snapshot . --at 25 --out ..\snapshot-end.png
```

Open snapshots and inspect them visually. Fix text overflow, face cropping, and bottom-safe-area issues before render.

## 7. Render

```powershell
npx hyperframes render . --output ..\output.mp4 --quality standard --fps 30
```

If Hyperframes reports sparse keyframes, re-encode the source video:

```powershell
ffmpeg -y -i assets\source.mp4 `
  -c:v libx264 -preset fast -crf 18 -r 30 -g 30 -keyint_min 30 `
  -movflags +faststart -c:a copy assets\source-gop30.mp4
```

Then update `index.html` to use `source-gop30.mp4` and render again.

## 8. Final Probe

```powershell
ffprobe -v quiet -print_format json -show_streams -show_format "..\output.mp4"
```

Confirm:

- `width=1080`, `height=1920` for vertical output
- expected duration
- audio stream exists when source audio should be preserved

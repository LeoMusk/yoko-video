# Agent Instructions

This project turns recent AI news into short-video topics and scripts.

## Read First

- `README.md`
- `docs/USAGE.md`
- `docs/OUTPUTS.md`
- `docs/AGENT_WORKFLOW.md`

## Main Commands

```powershell
python -m yoko_video.m1.collect --since-days 3
python -m yoko_video.m2.score --only-unscored --max-unscored 120 --top-n 40
python -m yoko_video.m3.script --ids <id-prefix>
python scripts/script_to_remotion_props.py --latest --index 1
```

## Rules

- Do not treat LLM output as verified facts.
- Verify source links before finalizing a video script.
- Keep user-specific style in `config/profile.json`, not hardcoded Python prompts.
- Do not commit `.env`, `config/profile.json`, local `data/` outputs, or rendered videos.
- Preserve existing user changes, especially experimental Remotion files.

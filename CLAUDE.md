# Claude Code Notes

Use `AGENTS.md` and `docs/AGENT_WORKFLOW.md` as the source of truth.

Typical workflow:

1. Read the latest `data/scored/*_brief.md`.
2. Pick one topic and verify the original source.
3. Run `python -m yoko_video.m3.script --ids <id-prefix>`.
4. Improve the script for natural spoken Chinese.
5. Optionally run `python scripts/script_to_remotion_props.py --latest --index 1` for Remotion.

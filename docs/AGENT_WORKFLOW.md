# Agent 工作流

适用于 Codex、Claude Code 等能读写本地项目的 Agent。

## Agent 先读哪些文件

```text
README.md
docs/OUTPUTS.md
docs/USAGE.md
config/profile.example.json
```

如果要做视频化，再读：

```text
docs/VIDEO_WORKFLOW.md
remotion/src/YokoShort.tsx
remotion/src/EditorialShort.tsx
```

## 任务卡 1：从简报挑选题

```text
请读取最新的 data/scored/*_brief.md 和对应的 *_scored.jsonl。
挑出今天最值得做成 60-90 秒短视频的一条 AI 资讯。
要求：
1. 解释为什么选它：重要性、短视频爆点、受众匹配。
2. 打开原文链接核验公司名、产品名、数字、发布时间。
3. 标出可讲、慎讲、不讲的信息。
4. 如果事实不可靠，换下一条。
5. 给出最终选题 id 前缀。
```

## 任务卡 2：生成并改写脚本

```text
请使用选题 id 前缀运行：
python -m yoko_video.m3.script --ids <id前缀>

然后读取 data/scripts/*_scripts.md，对脚本做二次编辑：
1. 保留已核验事实。
2. 改成更自然的口播短句。
3. 去掉 AI 腔、空洞排比和夸张词。
4. 输出最终口播稿、封面标题、3-5 个分镜建议、风险点。
```

## 任务卡 3：把脚本转成 Remotion props

```text
请读取最新 data/scripts/*_scripts.json 的第 1 条脚本。
运行：
python scripts/script_to_remotion_props.py --latest --index 1

然后检查 remotion/props.json 是否包含 title_caption、data_points、key_points、voiceover。
给出 Remotion 预览和渲染命令。
```

## 任务卡 4：做成信息流视频

```text
请用 Remotion 做 9:16 信息流短视频。
要求：
1. 使用 remotion/props.json。
2. 优先复用 YokoShort 或 EditorialShort。
3. 标题、数字、要点不能溢出画面。
4. 底部 12%-15% 留给平台字幕和按钮。
5. 渲染前先预览，必要时调整字号和布局。
6. 输出最终 MP4 路径和检查结果。
```

## 必须遵守的事实核验规则

- 不能把 LLM 生成内容直接当事实。
- 关键数字必须能追溯到原文、官方公告或可靠媒体。
- Reddit、论坛、HN 评论只能当线索，不能当单一事实来源。
- 标题党、爆料、传闻必须在脚本中降级表达。
- 不确定的信息宁可删掉。

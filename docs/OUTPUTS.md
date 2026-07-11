# 产物说明

## data/raw/YYYY-MM-DD.jsonl

M1 采集到的原始资讯，每行一个 JSON。

常见字段：

- `id`：条目唯一 ID
- `source`：信息源名称
- `tier`：信息源层级，如 `T1`、`T2`、`CN`、`DATA`
- `kind`：内容类型，如 `news`、`vendor`、`newsletter`、`macro-data`
- `fetched_at`：采集时间，UTC
- `published_at`：发布时间，UTC
- `title`：标题
- `url`：原文链接
- `authors`：作者列表
- `categories`：RSS 分类
- `summary`：正文摘要或页面摘录

## data/m1.db

SQLite 去重库。记录已经见过的条目，避免跨天重复处理。
这是本地产物，不建议提交。

## data/scored/YYYY-MM-DD_scored.jsonl

M2 评分结果。在 raw 条目上增加 `scores` 字段。

`scores` 常见字段：

- `is_ad`：是否广告/PR
- `category`：AI 分类
- `importance`：行业重要性，1-10
- `video_fit`：短视频适配度，1-10
- `audience_fit`：受众匹配度，1-10
- `one_liner`：一句话核心信息
- `chinese_angle`：中文短视频切入角度
- `final`：综合分

## data/scored/YYYY-MM-DD_brief.md

给人看的每日选题简报。包含：

- 原始条目数
- 评分成功数量
- 类别分布
- Top 选题候选
- 核心信息
- 中文视频角度
- 原文链接

## data/scripts/YYYY-MM-DD_scripts.md

M3 生成的短视频脚本文档。适合直接给人看或贴进剪映、腾讯智影、HeyGen。

常见部分：

- 钩子
- 关键数据
- 核心信息点
- 创作者观点
- 引流 CTA
- 口播逐字稿
- 画面建议

## data/scripts/YYYY-MM-DD_scripts.json

结构化脚本。适合给 Remotion 或 Agent 使用。

常见字段：

- `title_caption`
- `hook`
- `data_points`
- `key_points`
- `creator_take`
- `cta`
- `voiceover`
- `visual_cues`
- `duration_sec`
- `meta`

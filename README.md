# yoko-video

把最近几天的 AI 行业资讯自动汇总成“可选题简报”，再生成短视频脚本。适合 AI/科技创作者每天筛选资讯、挑选选题，并让 Codex / Claude Code 等 Agent 辅助完成脚本和视频化。

当前主链路：

```text
M1 信息采集 -> M2 选题评分 -> M3 脚本生成 -> M4 视频化
```

## 3 分钟快速开始

### 1. 安装依赖

需要 Python 3.10+。

```powershell
pip install -r requirements.txt
```

如果要使用小红书 Markdown 转图工具，再安装可选依赖：

```powershell
pip install -r requirements-optional.txt
playwright install chromium
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env`：

```powershell
Copy-Item .env.example .env
```

然后填入：

```env
DEEPSEEK_API_KEY=你的 DeepSeek API Key
NEWS_SINCE_DAYS=3
MAX_UNSCORED=120
BRIEF_TOP_N=40
SCRIPT_TOP=2
```

### 3. 配置你的账号风格

```powershell
Copy-Item config\profile.example.json config\profile.json
```

修改 `config/profile.json` 里的创作者名称、受众、CTA、语气样例。M2 选题评分和 M3 脚本生成都会读取它。

### 4. 生成今日选题简报

双击：

```text
run_news.bat
```

或命令行运行：

```powershell
python -m yoko_video.m1.collect --since-days 3
python -m yoko_video.m2.score --only-unscored --max-unscored 120 --top-n 40
```

输出：

```text
data/scored/YYYY-MM-DD_brief.md
data/scored/YYYY-MM-DD_scored.jsonl
```

### 5. 生成短视频脚本

双击：

```text
run_script.bat
```

或手动指定选题：

```powershell
python -m yoko_video.m3.script --ids <选题id前缀>
```

输出：

```text
data/scripts/YYYY-MM-DD_scripts.md
data/scripts/YYYY-MM-DD_scripts.json
```

### 6. 一键跑简报 + 脚本

```text
run_all.bat
```

## 常见使用场景

- 只想每天看 AI 资讯：运行 `run_news.bat`，打开 `data/scored/*_brief.md`。
- 想做视频：先看 brief 选题，再运行 `run_script.bat` 或 `python -m yoko_video.m3.script --ids <id>`。
- 想控制成本：调低 `.env` 里的 `MAX_UNSCORED`。
- 只看最近 2-3 天：设置 `.env` 里的 `NEWS_SINCE_DAYS=3`。
- 想接入自己的信息源：编辑 `yoko_video/m1/sources.py`。
- 想让 Agent 帮你做成片：看 `docs/AGENT_WORKFLOW.md`。

## 产物说明

详见 `docs/OUTPUTS.md`。核心文件：

- `data/raw/*.jsonl`：采集到的原始资讯。
- `data/scored/*_scored.jsonl`：加了 LLM 评分的结构化数据。
- `data/scored/*_brief.md`：适合人看的每日选题简报。
- `data/scripts/*_scripts.md`：可直接拍摄或交给视频工具的脚本。
- `data/scripts/*_scripts.json`：给 Remotion / Agent 使用的结构化脚本。

## 视频化

目前推荐两种方式：

1. 外部 SaaS：把 `data/scripts/*_scripts.md` 里的口播稿、画面建议粘到剪映、腾讯智影、HeyGen 等工具。
2. Remotion 信息流：运行 `scripts/script_to_remotion_props.py` 把脚本转成 `remotion/props.json`，再用 Remotion 预览或渲染。

详见 `docs/VIDEO_WORKFLOW.md`。

## 开源安全说明

这个仓库默认只提交示例配置和示例数据。你自己的 `.env`、`config/profile.json`、`data/`、`experiments/`、`out/` 和视频素材不应提交到公开仓库。

公开发布前请按 `docs/OPEN_SOURCE_RELEASE.md` 做一次检查。

## 给 Agent 的入口

如果你用 Codex / Claude Code，请先让 Agent 读：

- `AGENTS.md`
- `docs/AGENT_WORKFLOW.md`
- `docs/OUTPUTS.md`

推荐任务：

```text
请读取今天的 data/scored/*_brief.md，挑出最值得做短视频的一条，核验事实，然后运行 M3 生成脚本，并把脚本改到适合口播。
```

## 项目文档

- `docs/INSTALL.md`：安装说明。
- `docs/USAGE.md`：M1/M2/M3/M4 用法。
- `docs/OUTPUTS.md`：产物字段说明。
- `docs/AGENT_WORKFLOW.md`：Agent 任务卡。
- `docs/VIDEO_WORKFLOW.md`：视频化和 Remotion 桥接。
- `docs/TROUBLESHOOTING.md`：常见问题。
- `docs/OPEN_SOURCE_RELEASE.md`：开源前敏感信息检查清单。
- `docs/WECHAT_OPEN_SOURCE_ARTICLE.md`：公众号文章草稿。

## 注意

LLM 生成的选题和脚本不能直接当事实发布。做视频前必须核验原文链接、公司名、产品名、关键数字和发布时间。

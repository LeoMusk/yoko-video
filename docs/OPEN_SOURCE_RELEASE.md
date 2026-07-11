# 开源发布检查清单

这份清单用于把本项目发布到公开 Git 仓库前做最后检查。

## 不能提交的内容

- `.env`、`.env.*`：真实 API Key、Base URL、代理配置。
- `config/profile.json`：个人账号定位、产品名、CTA、风格样例。
- `data/`：本地采集的原始资讯、评分结果、脚本结果、SQLite 去重库。
- `experiments/`、`out/`：本地视频实验、截图、MP4、音频、渲染中间产物。
- `remotion/public/*`：真实新闻截图、视频素材、音频素材。
- `.claude/`、`.vscode/`：本地编辑器和 Agent 配置。

## 应该提交的内容

- `README.md`
- `.env.example`
- `requirements.txt`
- `requirements-optional.txt`
- `config/profile.example.json`
- `yoko_video/`
- `scripts/`
- `docs/`
- `examples/`
- `run_*.bat`、`run_*.ps1`
- `remotion/` 中的通用模板代码和示例 `props.json`
- `AGENTS.md`、`CLAUDE.md`
- `LICENSE`

## 发布前命令

```powershell
git status --short
git ls-files .env config/profile.json data experiments out
git log --all --oneline -- .env config/profile.json data experiments out
git grep -n -I -E "sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{20,}|xox[baprs]-|DEEPSEEK_API_KEY=[^y#[:space:]]" HEAD -- . ":!remotion/package-lock.json"
```

期望结果：

- `git ls-files ...` 不输出 `.env`、`config/profile.json`、`data/`、`experiments/`、`out/`。
- `git grep ...` 不输出真实密钥。
- `git status --short` 里没有准备误提交的本地素材和生成产物。

如果 `git log --all -- ...` 还能看到历史提交，说明这些文件曾经进入过 git 历史。普通删除只能让它们不出现在最新版本里，不能从历史里消失。

## 干净历史发布

如果仓库从未公开，且历史里只是误提交了本地数据，可以在确认后重写历史再推送。

如果仓库已经公开过，或者你不想影响原仓库，最稳妥的方式是新建一个干净公开仓库，只提交当前脱敏后的源码、示例配置和文档。

推荐判断：

- 只是想先给粉丝使用：新建干净公开仓库。
- 当前仓库已经有 star、issue 或别人 clone：不要随便改历史，先发一个删除敏感文件的提交，再评估是否需要换仓库。
- 历史里出现真实 API Key：先作废 Key，再重写历史或新建仓库。

## 推荐发布流程

不要直接运行 `git add .`。如果工作区里还有本地视频实验或一次性 Remotion 组件，容易把素材路径、截图、实验代码一起带进公开仓库。

推荐显式添加核心文件：

```powershell
git add README.md .gitignore .env.example LICENSE AGENTS.md CLAUDE.md
git add requirements.txt requirements-optional.txt config examples docs
git add yoko_video scripts run_*.bat run_*.ps1 render_remotion.bat render_remotion.ps1
git add remotion/package.json remotion/package-lock.json remotion/remotion.config.ts remotion/tsconfig.json remotion/props.json remotion/breaking-flash.json
git add remotion/src/index.ts remotion/src/YokoShort.tsx remotion/src/EditorialShort.tsx remotion/src/Opus48Launch.tsx remotion/src/BreakingFlash.tsx
git status --short
git commit -m "Prepare public release"
git push origin main
```

如果你确认要公开某个实验性视频模板，再单独检查它依赖的素材、截图、品牌名和事实来源后再添加。

如果 GitHub 仓库还是私有，在网页端进入：

```text
Settings -> General -> Danger Zone -> Change repository visibility -> Public
```

公开后建议用一个全新的目录重新拉取验证：

```powershell
git clone https://github.com/LeoMusk/yoko-video.git
cd yoko-video
pip install -r requirements.txt
Copy-Item .env.example .env
Copy-Item config\profile.example.json config\profile.json
```

填好 `DEEPSEEK_API_KEY` 后，双击 `run_news.bat` 验证。

# 公众号文章草稿：我把 AI 资讯选题助手开源了

## 标题备选

1. 我用 Codex 做了一个 AI 资讯选题助手，现在开源
2. 每天自动筛 AI 行业资讯，还能生成短视频脚本
3. 做 AI 群运营和短视频，这个小工具可以直接拿去用

## 正文

过去一段时间，我一直在用 Codex 做一个小工具：每天自动抓取最近 2-3 天的 AI 行业资讯，筛掉重复和低价值信息，再把值得关注的内容整理成选题简报。

这个项目最开始只是给我自己用的。

因为每天 AI 新闻太多了。新模型、新产品、融资、开源项目、论文、公司动态、争议事件，信息量很大，但真正值得拿来做群运营、短视频选题、朋友圈内容的，其实没有那么多。

手动刷信息很累，最大的问题不是找不到新闻，而是不知道哪条值得讲。

所以我把流程拆成了几步：

1. 自动采集最近几天的 AI 资讯
2. 用 LLM 做初步评分和分类
3. 生成一份人能快速看的选题简报
4. 对有价值的选题继续生成短视频脚本
5. 必要时再交给 Codex / Claude Code 这类 Agent 做核验、改稿和视频化

现在这个项目我整理了一版，准备开源给需要的人。

项目地址：

```text
https://github.com/LeoMusk/yoko-video
```

## 它适合谁

这个工具比较适合三类人：

第一类，是做 AI 群运营的人。每天需要在群里发一点有价值的信息，但又不想复制粘贴一堆零散新闻。

第二类，是做 AI / 科技短视频的人。你可以先让工具帮你筛选资讯，再挑一条适合口播的视频选题。

第三类，是想学习 Codex / Claude Code 工作流的人。这个项目不是一个复杂系统，但覆盖了采集、结构化、评分、脚本生成、视频化这几步，很适合拿来练 Agent 协作。

## 怎么使用

使用方式尽量做得简单。

先拉取项目：

```powershell
git clone https://github.com/LeoMusk/yoko-video.git
cd yoko-video
```

安装依赖：

```powershell
pip install -r requirements.txt
```

复制配置文件：

```powershell
Copy-Item .env.example .env
Copy-Item config\profile.example.json config\profile.json
```

然后在 `.env` 里填入你的 DeepSeek API Key。

如果你只是想每天看 AI 资讯，直接双击：

```text
run_news.bat
```

它会自动完成两件事：

1. 抓取最近几天的 AI 资讯
2. 对资讯做评分，并生成选题简报

产物会在这里：

```text
data/scored/YYYY-MM-DD_brief.md
```

这份简报里会包含：

- 今天采集了多少条资讯
- 哪些内容分数较高
- 每条资讯的核心信息
- 中文短视频角度
- 原文链接

如果你看到某条资讯很适合做短视频，可以继续双击：

```text
run_script.bat
```

或者指定某个选题：

```powershell
python -m yoko_video.m3.script --ids <选题id前缀>
```

脚本会输出到：

```text
data/scripts/YYYY-MM-DD_scripts.md
data/scripts/YYYY-MM-DD_scripts.json
```

其中 Markdown 文件适合直接人工看，JSON 文件适合交给 Agent 或 Remotion 做视频化。

## video 部分怎么用

项目里也放了一个基础的视频化链路。

如果你想用代码生成信息流短视频，可以先把脚本转成 Remotion props：

```powershell
python scripts\script_to_remotion_props.py --latest --index 1
```

然后进入 Remotion 预览：

```powershell
cd remotion
npm install
npm run studio
```

也可以让 Agent 帮你做这一步。

比如你可以对 Codex 说：

```text
读取最新的 data/scored/*_brief.md，挑出最适合做短视频的一条。
先核验原文事实，再生成脚本。
然后把脚本转成 remotion/props.json，并检查 Remotion 页面有没有文字溢出。
```

我自己的经验是，Agent 很适合做三件事：

1. 从简报里挑选真正值得讲的选题
2. 把初稿改成更自然的口播
3. 根据截图、榜单、演示视频生成短视频页面

但注意，LLM 生成的内容不能直接当事实发布。

最终发视频前，一定要核验原文链接、公司名、产品名、数字和发布时间。

## 为什么开源

这个项目不是什么很复杂的系统。

但它解决的是一个很真实的问题：信息太多，注意力太少。

尤其是做 AI 内容、AI 群运营、AI 产品的人，每天都需要跟上行业变化。但如果全部靠手动刷，会很快被信息流淹没。

我希望这个工具能提供一个起点：

- 小白可以直接双击 bat 跑起来
- 内容创作者可以快速找到选题
- 群运营可以每天生成一份可读简报
- 会用 Agent 的人可以继续扩展成自己的视频生产流

你可以把它改成自己的信息源，也可以把输出接到飞书、企微、公众号、小红书、视频号。

如果你已经在用 Codex 或 Claude Code，也可以直接让 Agent 读项目里的 `AGENTS.md`，它会知道应该先读哪些文件、跑哪些命令、产物在哪里。

项目地址：

```text
https://github.com/LeoMusk/yoko-video
```

如果你刚开始做 AI 内容，不妨先让工具帮你解决第一步：每天知道有什么值得讲。

剩下的，就是判断、表达和持续输出。

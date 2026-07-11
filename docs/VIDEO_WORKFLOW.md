# 视频化工作流

M3 会生成两份脚本：

```text
data/scripts/YYYY-MM-DD_scripts.md
data/scripts/YYYY-MM-DD_scripts.json
```

## 路线 A：外部 SaaS

适合小白和稳定生产。

1. 打开 `*_scripts.md`
2. 复制 `口播逐字稿`
3. 把 `画面建议` 交给剪映、腾讯智影、HeyGen 等工具
4. 发布前核验关键事实和数字

## 路线 B：Remotion 信息流视频

适合想用代码生成 9:16 信息流短视频的用户。

### 1. 安装 Node 依赖

```powershell
cd remotion
npm install
cd ..
```

### 2. 把 M3 脚本转成 props

最新脚本第 1 条：

```powershell
python scripts\script_to_remotion_props.py --latest --index 1
```

指定日期：

```powershell
python scripts\script_to_remotion_props.py --date 2026-06-20 --index 1
```

输出：

```text
remotion/props.json
```

### 3. 预览

```powershell
cd remotion
npm run studio
```

选择 `YokoShort` 或 `EditorialShort` composition。

也可以用根目录脚本：

```powershell
.\render_remotion.ps1 -Preview
```

### 4. 渲染 MP4

```powershell
.\render_remotion.ps1 -Index 1 -Composition YokoShort
```

输出：

```text
out/remotion/*.mp4
```

## 路线 C：让 Agent 做视频

给 Agent 的任务卡：

```text
读取 data/scripts/*_scripts.json 的第 1 条脚本。
运行 python scripts/script_to_remotion_props.py --latest --index 1。
打开 remotion/props.json，确认字段完整。
用 Remotion 预览 YokoShort 和 EditorialShort，选择更适合的一版。
如果文字溢出，调整 Remotion 模板字号、行高或 key_points 数量。
渲染 MP4，并报告输出路径。
```

## 进阶：本地视频剪辑

如果你有本地口播视频、直播片段、演示录屏，可以让 Agent 使用 `skills/agent-video-cut` 工作流做二次剪辑。这个路线适合：

- 把长视频剪成 25-45 秒短视频
- 给口播视频加信息卡片
- 用 Hyperframes 做可复现渲染

先让 Agent 读取：

```text
skills/agent-video-cut/SKILL.md
```

再提供本地视频路径和目标平台。

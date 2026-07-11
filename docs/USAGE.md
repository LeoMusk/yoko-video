# 使用方式

## 方式一：每日资讯简报

双击：

```text
run_news.bat
```

等价命令：

```powershell
python -m yoko_video.m1.collect --since-days 3
python -m yoko_video.m2.score --only-unscored --max-unscored 120 --top-n 40
```

输出：

```text
data/scored/YYYY-MM-DD_brief.md
data/scored/YYYY-MM-DD_scored.jsonl
```

## 方式二：从今日 Top 选题生成脚本

双击：

```text
run_script.bat
```

默认生成 `SCRIPT_TOP` 条脚本，配置在 `.env`。

## 方式三：指定选题生成脚本

先打开 `data/scored/YYYY-MM-DD_brief.md`，复制目标选题对应的 `id` 前缀，再运行：

```powershell
python -m yoko_video.m3.script --ids 5544e5b
```

如果要透传参数给 bat 对应的 ps1：

```powershell
.\run_script.ps1 --ids 5544e5b
```

## 方式四：一键简报 + 脚本

```text
run_all.bat
```

## 调试采集源

```powershell
python -m yoko_video.m1.collect --dry-run
python -m yoko_video.m1.collect --tier T1
python -m yoko_video.m1.collect --mode watch
python -m yoko_video.m1.collect --only openai-news deepmind-blog
```

## 控制成本

- 降低 `.env` 的 `MAX_UNSCORED`
- 调小 M2 的 `--top-n`
- 先跑 `--limit 30` 做调试

```powershell
python -m yoko_video.m2.score --limit 30 --top-n 10
```

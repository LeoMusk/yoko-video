# 常见问题

## 双击 bat 一闪而过

从 PowerShell 手动运行对应脚本：

```powershell
.\run_news.ps1
```

这样可以看到完整报错。

## 提示缺少 feedparser

```powershell
pip install -r requirements.txt
```

## 提示未配置 DEEPSEEK_API_KEY

复制 `.env.example` 为 `.env`，填入：

```env
DEEPSEEK_API_KEY=你的 key
```

## M1 有信源失败

这是正常情况。RSS 或网页源可能临时超时、403、改版。`run_news.ps1` 会继续用成功采集的数据做评分。

## 当天没有 brief

可能原因：

- 今天没有新数据
- UTC 日期和本地日期不同
- M2 API 调用失败

去 `data/scored/` 看最新的 `*_brief.md`。

## 生成的脚本不像我的风格

修改 `config/profile.json`：

- `tone_keywords`
- `opening_address`
- `cta_style`
- `style_samples`
- `banned_phrases`

建议放 3-5 段你自己满意的视频字幕作为 `style_samples`。

## 事实看起来可疑

让 Agent 打开原文链接核验。未核验的数字和结论不要进视频。

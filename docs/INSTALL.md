# 安装说明

## 环境要求

- Python 3.10+
- Windows 用户可直接使用项目根目录下的 `.bat` 文件
- M2/M3 需要 DeepSeek API Key
- Remotion 视频化需要 Node.js 18+（仅进阶视频化需要）

## 安装 Python 依赖

```powershell
pip install -r requirements.txt
```

可选工具（小红书 Markdown 转图）：

```powershell
pip install -r requirements-optional.txt
playwright install chromium
```

## 配置 .env

```powershell
Copy-Item .env.example .env
```

至少填写：

```env
DEEPSEEK_API_KEY=你的 DeepSeek API Key
```

常用参数：

```env
NEWS_SINCE_DAYS=3
MAX_UNSCORED=120
BRIEF_TOP_N=40
SCRIPT_TOP=2
```

## 配置创作者信息

```powershell
Copy-Item config\profile.example.json config\profile.json
```

修改 `creator_name`、`audience`、`product_name`、`cta_style`、`style_samples`。
如果没有 `config/profile.json`，程序会使用 `config/profile.example.json`。

## 验证安装

```powershell
python -c "import feedparser; print('ok')"
python scripts\smoke_deepseek.py
```

`smoke_deepseek.py` 会真实调用一次 DeepSeek API。

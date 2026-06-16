# 小红书 Markdown 转图片工作流

脚本：

```powershell
python scripts\md_to_xhs_images.py path\to\article.md
```

默认输出：

```text
data/xhs/<markdown文件名>/<markdown文件名>_01.png
data/xhs/<markdown文件名>/<markdown文件名>_02.png
...
data/xhs/<markdown文件名>/<markdown文件名>.html
```

## 单篇导出

```powershell
python scripts\md_to_xhs_images.py data\articles\fable.md --out data\xhs --brand 世界模型工场
```

## 批量导出

目录下所有 `.md` 会逐个导出：

```powershell
python scripts\md_to_xhs_images.py data\articles --out data\xhs --brand 世界模型工场
```

## 强制分页

默认会根据页面高度自动分页。需要手动断页时，在 Markdown 中加入：

```markdown
<!-- pagebreak -->
```

或：

```markdown
---PAGE---
```

## 当前模板

默认主题：`yoko-clean`

- 小红书 3:4 竖图，默认 `1080x1440`
- 白底、强标题、认知文章风格
- 右上角页码
- 底部品牌文字
- 支持标题、段落、列表、引用、代码块、表格、图片

可调参数：

```powershell
python scripts\md_to_xhs_images.py article.md `
  --out data\xhs `
  --brand 世界模型工场 `
  --width 1080 `
  --height 1440 `
  --scale 1
```

## 建议写作格式

```markdown
# 普通人开始用不起强AI了

第一屏先给结论和冲突。

## 这次是真强

解释核心事实。

## 但问题来了

讲代价、限制、门槛。

## 我的判断

输出可转发的认知结论。
```

如果标题断行不理想，可以直接写 HTML 换行：

```markdown
# 普通人开始用不<br>起强AI了
```

## 和 Madopic 的关系

Madopic 是交互式 Markdown 转图工具，适合手动编辑和预览；这个脚本是批处理工具，适合把已经定稿的文章批量转成小红书图片。后续可以继续把 Madopic 里的 UI 预览能力作为参考，但生产链路建议走本脚本。

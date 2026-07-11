# 配置说明

复制 `profile.example.json` 为 `profile.json`，再改成自己的账号信息。

```powershell
Copy-Item config\profile.example.json config\profile.json
```

`profile.json` 不会提交到 Git。M2 选题评分和 M3 脚本生成都会优先读取它。

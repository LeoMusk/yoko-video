"""极简 .env 加载器（避免引入 python-dotenv 依赖）。

只支持 KEY=VALUE 形式。# 开头视为注释。值两端的双引号会被剥掉。
找到第一个 .env 文件（项目根）就停止。
"""
from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: Path | None = None) -> dict[str, str]:
    """读取 .env，注入 os.environ（不覆盖已存在的）。返回新增 / 已有的 kv。"""
    if path is None:
        path = Path(".env")
    if not path.exists():
        return {}

    loaded: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # 去掉两端引号
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        loaded[key] = value
        os.environ.setdefault(key, value)
    return loaded

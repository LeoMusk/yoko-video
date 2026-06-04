"""DeepSeek API 客户端（OpenAI 兼容协议，HTTP 直连，不引入 openai SDK）。

调用示例：
    client = DeepSeekClient.from_env()
    msg = client.chat(
        model="deepseek-v4-flash",
        messages=[{"role": "user", "content": "你好"}],
        response_format={"type": "json_object"},
    )
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_TIMEOUT = 120


@dataclass
class DeepSeekClient:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    timeout: int = DEFAULT_TIMEOUT

    @classmethod
    def from_env(cls, env_var: str = "DEEPSEEK_API_KEY") -> "DeepSeekClient":
        key = os.environ.get(env_var)
        if not key:
            raise RuntimeError(
                f"{env_var} 未设置；请在 .env 或环境变量中配置后再运行"
            )
        base = os.environ.get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL)
        return cls(api_key=key, base_url=base)

    def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        response_format: dict[str, str] | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """单次 chat 调用。返回原始 response dict。失败按指数退避重试。"""
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        last_err: Exception | None = None
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = resp.read().decode("utf-8")
                    return json.loads(body)
            except urllib.error.HTTPError as e:
                err_body = ""
                try:
                    err_body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    pass
                last_err = RuntimeError(f"HTTP {e.code}: {err_body[:500]}")
                # 4xx 一般不该重试（除了 429）
                if e.code != 429 and 400 <= e.code < 500:
                    raise last_err
            except (urllib.error.URLError, TimeoutError) as e:
                last_err = RuntimeError(f"Network error: {e}")
            time.sleep(2 ** attempt)
        raise last_err or RuntimeError("Unknown error")


def extract_content(resp: dict[str, Any]) -> str:
    """从 DeepSeek/OpenAI 兼容 response 中拿 content 字符串。"""
    return resp["choices"][0]["message"]["content"]


def usage_of(resp: dict[str, Any]) -> dict[str, int]:
    """返回 {prompt_tokens, completion_tokens, total_tokens}。"""
    u = resp.get("usage") or {}
    return {
        "prompt_tokens": u.get("prompt_tokens", 0),
        "completion_tokens": u.get("completion_tokens", 0),
        "total_tokens": u.get("total_tokens", 0),
    }

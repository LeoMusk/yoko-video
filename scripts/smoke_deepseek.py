"""冒烟测试：确认 .env 加载 + DeepSeek API 调用 + model 名称有效。"""
from yoko_video.m2.env import load_dotenv
from yoko_video.m2.llm import DeepSeekClient, extract_content, usage_of

load_dotenv()
client = DeepSeekClient.from_env()

resp = client.chat(
    model="deepseek-v4-flash",
    messages=[
        {"role": "system", "content": "你是一个 JSON 输出器。"},
        {"role": "user", "content": "返回 {\"hello\": \"world\"}，仅 JSON。"},
    ],
    response_format={"type": "json_object"},
    max_tokens=50,
)
print("--- content ---")
print(extract_content(resp))
print("--- usage ---")
print(usage_of(resp))

"""
封装 Ollama streaming 调用。
使用官方 ollama Python 包，stream=True 逐 chunk yield 结构化 dict。
"""
import time
from typing import Generator
from django.conf import settings
import ollama


def stream_prompt(prompt: str, think: str | None = None) -> Generator[dict, None, None]:
    """
    向本地 Ollama 发送 prompt，逐块 yield 结构化 dict：
      {"type": "token",  "text": str, "thinking": bool}  — 文本 chunk
      {"type": "stats",  "tokens": int, "tps": float}    — 最终统计（done 时）
    thinking=True 表示模型正在推理，不写入文件。
    """
    client = ollama.Client(host=settings.OLLAMA_HOST)
    kwargs = dict(model=settings.OLLAMA_MODEL, prompt=prompt, stream=True)
    if think:
        kwargs["think"] = think

    for chunk in client.generate(**kwargs):
        done          = chunk.get("done", False)
        response_text = chunk.get("response", "") or ""
        thinking_text = chunk.get("thinking", "") or ""

        if done:
            eval_count    = chunk.get("eval_count", 0) or 0
            eval_duration = chunk.get("eval_duration", 0) or 0  # 纳秒
            tps = round(eval_count / (eval_duration / 1e9), 1) if eval_duration else 0.0
            yield {"type": "stats", "tokens": eval_count, "tps": tps}
        elif thinking_text:
            # 模型推理阶段：thinking 字段有内容，response 为空
            yield {"type": "token", "text": thinking_text, "thinking": True}
        elif response_text:
            yield {"type": "token", "text": response_text, "thinking": False}


def check_health() -> bool:
    """
    检测 Ollama 是否在线。
    尝试列出模型列表，成功返回 True，任何异常返回 False。
    """
    try:
        client = ollama.Client(host=settings.OLLAMA_HOST)
        client.list()
        return True
    except Exception:
        return False

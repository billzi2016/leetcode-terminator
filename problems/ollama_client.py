"""
封装 Ollama streaming 调用。
使用官方 ollama Python 包，stream=True 逐 chunk yield 文本。
"""
from typing import Generator
from django.conf import settings
import ollama


def stream_prompt(prompt: str) -> Generator[str, None, None]:
    """
    向本地 Ollama 发送 prompt，以 generator 形式逐块 yield 文本内容。
    调用方负责将 chunks 写入文件和推送给前端。
    """
    client = ollama.Client(host=settings.OLLAMA_HOST)
    for chunk in client.generate(
        model=settings.OLLAMA_MODEL,
        prompt=prompt,
        stream=True,
    ):
        text = chunk.get("response", "")
        if text:
            yield text


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

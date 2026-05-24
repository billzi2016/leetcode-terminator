"""
启动时将 leetcode_problems.json 加载到内存字典。
key 为 frontend_id（整数），value 为完整题目 dict。
模块级变量，整个进程生命周期只加载一次。
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def _load() -> dict[int, dict]:
    path = BASE_DIR / "leetcode_problems.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    questions = data.get("questions", [])
    return {int(q["frontend_id"]): q for q in questions}

# 进程启动时执行一次，后续所有请求直接读此字典
PROBLEMS: dict[int, dict] = _load()

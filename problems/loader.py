"""
启动时将 leetcode_problems.json 加载到内存字典，同时统计 topic/难度分布。
key 为 frontend_id（整数），value 为完整题目 dict。
模块级变量，整个进程生命周期只加载一次。
"""
import json
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load():
    path = BASE_DIR / "leetcode_problems.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    questions = data.get("questions", [])

    problems = {int(q["frontend_id"]): q for q in questions}

    diff_counter: Counter = Counter()
    topic_counter: Counter = Counter()
    for q in questions:
        diff_counter[q.get("difficulty", "")] += 1
        for t in q.get("topics", []):
            topic_counter[t] += 1

    # topics 按数量降序排列
    topic_counts = dict(topic_counter.most_common())
    difficulty_counts = dict(diff_counter)

    return problems, topic_counts, difficulty_counts


# 进程启动时执行一次，后续所有请求直接读这三个变量
PROBLEMS: dict[int, dict]
TOPIC_COUNTS: dict[str, int]
DIFFICULTY_COUNTS: dict[str, int]

PROBLEMS, TOPIC_COUNTS, DIFFICULTY_COUNTS = _load()

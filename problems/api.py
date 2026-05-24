"""
Django Ninja API 路由。
所有端点挂在 /api/ 下，streaming 端点返回 SSE（django-eventstream）。
"""
import json
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.http import StreamingHttpResponse
from ninja import NinjaAPI, Query
from ninja.pagination import paginate, PageNumberPagination

from .loader import PROBLEMS, TOPIC_COUNTS, DIFFICULTY_COUNTS
from .ollama_client import check_health, stream_prompt
from .prompts import (
    translation_prompt,
    solution_prompt,
    similar_problem_prompt,
    similar_solution_prompt,
)

api = NinjaAPI()


# ────────────────────────────────────────────────────────────
# 工具函数
# ────────────────────────────────────────────────────────────

def _build_formatted_description(problem: dict) -> str:
    """
    拼装完整题目描述。
    原始 description 字段中 "Example X:" 和 "Constraints:" 只是占位符，
    实际内容在 examples 和 constraints 字段中，需要手动拼入。
    """
    lines = problem.get("description", "").split("\n")
    # 去掉占位行（"Example 1:" / "Constraints:" 等空行头）
    main_lines = [
        l for l in lines
        if not (l.strip().startswith("Example ") and l.strip().endswith(":"))
        and l.strip() != "Constraints:"
    ]
    result = "\n".join(main_lines).strip()

    examples = problem.get("examples", [])
    if examples:
        result += "\n\n"
        for ex in examples:
            result += f"**Example {ex['example_num']}:**\n```\n{ex.get('example_text', '')}\n```\n\n"

    constraints = problem.get("constraints", [])
    if constraints:
        result += "**Constraints:**\n"
        for c in constraints:
            result += f"- `{c}`\n"

    return result.strip()


def _solution_dir(problem_id: int) -> Path:
    """返回某题的 solutions 文件夹路径，不自动创建。"""
    return Path(settings.SOLUTIONS_DIR) / str(problem_id)


def _similar_dir(problem_id: int, n: int) -> Path:
    """返回举一反三第 n 题的文件夹路径。"""
    return _solution_dir(problem_id) / "similar" / str(n)


def _read_md(path: Path) -> Optional[str]:
    """读取 Markdown 文件，不存在返回 None。"""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def _stream_to_file(prompt: str, filepath: Path, think: str | None = None):
    """
    SSE streaming 生成器：
    1. 向 Ollama 发送 prompt，逐 chunk yield SSE 格式 JSON
    2. 仅收集非推理阶段的文本，完成后写入文件
    think: None = Ollama 默认，'high' = 深度推理
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    collected = []
    for item in stream_prompt(prompt, think=think):
        if item["type"] == "token" and not item.get("thinking"):
            collected.append(item["text"])
        yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
    filepath.write_text("".join(collected), encoding="utf-8")
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


def _sse_response(generator):
    """将生成器包装成 SSE StreamingHttpResponse。"""
    response = StreamingHttpResponse(generator, content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


# ────────────────────────────────────────────────────────────
# 健康检查
# ────────────────────────────────────────────────────────────

@api.get("/health/")
def health(request):
    """检测 Ollama 是否在线。"""
    return {"status": "ok" if check_health() else "down"}


@api.get("/meta/")
def meta(request):
    """返回 topic 和难度的题目数量统计，启动时计算一次，不重复扫描。"""
    return {
        "topics": TOPIC_COUNTS,
        "difficulties": DIFFICULTY_COUNTS,
    }


# ────────────────────────────────────────────────────────────
# 题目列表 & 详情
# ────────────────────────────────────────────────────────────

@api.get("/problems/")
def list_problems(
    request,
    q: Optional[str] = Query(None, description="搜索标题或 slug"),
    difficulty: Optional[str] = Query(None, description="Easy / Medium / Hard"),
    topic: Optional[str] = Query(None, description="按 topic 筛选"),
    page: int = Query(1),
    page_size: int = Query(50),
):
    """
    返回题目列表，支持关键词搜索、难度筛选、topic 筛选。
    默认每页 50 条，按 frontend_id 排序。
    """
    items = list(PROBLEMS.values())

    if q:
        q_lower = q.lower()
        items = [
            p for p in items
            if q_lower in p.get("title", "").lower()
            or q_lower in p.get("problem_slug", "").lower()
        ]

    if difficulty:
        diff = difficulty.capitalize()
        items = [p for p in items if p.get("difficulty") == diff]

    if topic:
        items = [p for p in items if topic in p.get("topics", [])]

    items.sort(key=lambda p: int(p.get("frontend_id", 0)))

    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": [
            {
                "id": int(p["frontend_id"]),
                "title": p["title"],
                "difficulty": p.get("difficulty", ""),
                "slug": p.get("problem_slug", ""),
                "topics": p.get("topics", []),
            }
            for p in items[start:end]
        ],
    }


@api.get("/problems/{problem_id}/")
def get_problem(request, problem_id: int):
    """返回单题完整数据，附带拼装好的 formatted_description，不存在返回 404。"""
    problem = PROBLEMS.get(problem_id)
    if not problem:
        return api.create_response(request, {"detail": "Not found"}, status=404)
    return {**problem, "formatted_description": _build_formatted_description(problem)}


# ────────────────────────────────────────────────────────────
# 翻译
# ────────────────────────────────────────────────────────────

@api.get("/solutions/{problem_id}/translation/")
def get_translation(request, problem_id: int):
    """读取中文翻译缓存，不存在返回 null。"""
    content = _read_md(_solution_dir(problem_id) / "translation.md")
    return {"content": content}


@api.get("/solutions/{problem_id}/translation/stream/")
def stream_translation(request, problem_id: int, think: Optional[str] = Query(None)):
    """SSE：调用 Ollama 翻译原题，边生成边推流，完成后写入 translation.md。"""
    problem = PROBLEMS.get(problem_id)
    if not problem:
        return api.create_response(request, {"detail": "Not found"}, status=404)
    filepath = _solution_dir(problem_id) / "translation.md"
    prompt = translation_prompt(_build_formatted_description(problem))
    return _sse_response(_stream_to_file(prompt, filepath, think=think))


# ────────────────────────────────────────────────────────────
# 题解
# ────────────────────────────────────────────────────────────

@api.get("/solutions/{problem_id}/solution/")
def get_solution(request, problem_id: int):
    """读取题解缓存，不存在返回 null。"""
    content = _read_md(_solution_dir(problem_id) / "solution.md")
    return {"content": content}


@api.get("/solutions/{problem_id}/solution/stream/")
def stream_solution(request, problem_id: int, think: Optional[str] = Query(None)):
    """SSE：调用 Ollama 生成题解，边生成边推流，完成后写入 solution.md。"""
    problem = PROBLEMS.get(problem_id)
    if not problem:
        return api.create_response(request, {"detail": "Not found"}, status=404)
    filepath = _solution_dir(problem_id) / "solution.md"
    prompt = solution_prompt(problem)
    return _sse_response(_stream_to_file(prompt, filepath, think=think))


# ────────────────────────────────────────────────────────────
# 举一反三
# ────────────────────────────────────────────────────────────

@api.get("/solutions/{problem_id}/similar/")
def list_similar(request, problem_id: int):
    """返回该题已生成的举一反三序号列表，如 [1, 2, 3]。"""
    similar_base = _solution_dir(problem_id) / "similar"
    if not similar_base.exists():
        return {"items": []}
    nums = sorted(
        int(d.name) for d in similar_base.iterdir()
        if d.is_dir() and d.name.isdigit()
    )
    return {"items": nums}


@api.get("/solutions/{problem_id}/similar/{n}/problem/")
def get_similar_problem(request, problem_id: int, n: int):
    """读取第 n 道相似题目，不存在返回 null。"""
    content = _read_md(_similar_dir(problem_id, n) / "problem.md")
    return {"content": content}


@api.get("/solutions/{problem_id}/similar/{n}/problem/stream/")
def stream_similar_problem(request, problem_id: int, n: int, think: Optional[str] = Query(None)):
    """SSE：生成第 n 道相似题目，写入 similar/{n}/problem.md，同时清除旧 solution.md。"""
    problem = PROBLEMS.get(problem_id)
    if not problem:
        return api.create_response(request, {"detail": "Not found"}, status=404)
    dir_ = _similar_dir(problem_id, n)
    old_solution = dir_ / "solution.md"
    if old_solution.exists():
        old_solution.unlink()
    filepath = dir_ / "problem.md"
    prompt = similar_problem_prompt(problem)
    return _sse_response(_stream_to_file(prompt, filepath, think=think))


@api.get("/solutions/{problem_id}/similar/{n}/solution/")
def get_similar_solution(request, problem_id: int, n: int):
    """读取第 n 道相似题解，不存在返回 null。"""
    content = _read_md(_similar_dir(problem_id, n) / "solution.md")
    return {"content": content}


@api.get("/solutions/{problem_id}/similar/{n}/solution/stream/")
def stream_similar_solution(request, problem_id: int, n: int, think: Optional[str] = Query(None)):
    """SSE：生成第 n 道相似题的题解，写入 similar/{n}/solution.md。"""
    problem_text = _read_md(_similar_dir(problem_id, n) / "problem.md")
    if not problem_text:
        return api.create_response(request, {"detail": "先生成题目再生成题解"}, status=400)
    filepath = _similar_dir(problem_id, n) / "solution.md"
    prompt = similar_solution_prompt(problem_text)
    return _sse_response(_stream_to_file(prompt, filepath, think=think))

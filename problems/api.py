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

from .loader import PROBLEMS
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


def _stream_to_file(prompt: str, filepath: Path):
    """
    SSE streaming 生成器：
    1. 向 Ollama 发送 prompt，逐 chunk yield SSE 格式文本
    2. 全部完成后写入文件
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    collected = []
    for chunk in stream_prompt(prompt):
        collected.append(chunk)
        # SSE 格式：data: <内容>\n\n
        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
    # 所有 chunk 收集完毕，写入缓存文件
    filepath.write_text("".join(collected), encoding="utf-8")
    yield "data: [DONE]\n\n"


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


# ────────────────────────────────────────────────────────────
# 题目列表 & 详情
# ────────────────────────────────────────────────────────────

@api.get("/problems/")
def list_problems(
    request,
    q: Optional[str] = Query(None, description="搜索标题或 slug"),
    difficulty: Optional[str] = Query(None, description="Easy / Medium / Hard"),
    page: int = Query(1),
    page_size: int = Query(50),
):
    """
    返回题目列表，支持关键词搜索和难度筛选。
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
    """返回单题完整数据，不存在返回 404。"""
    problem = PROBLEMS.get(problem_id)
    if not problem:
        return api.create_response(request, {"detail": "Not found"}, status=404)
    return problem


# ────────────────────────────────────────────────────────────
# 翻译
# ────────────────────────────────────────────────────────────

@api.get("/solutions/{problem_id}/translation/")
def get_translation(request, problem_id: int):
    """读取中文翻译缓存，不存在返回 null。"""
    content = _read_md(_solution_dir(problem_id) / "translation.md")
    return {"content": content}


@api.get("/solutions/{problem_id}/translation/stream/")
def stream_translation(request, problem_id: int):
    """SSE：调用 Ollama 翻译原题，边生成边推流，完成后写入 translation.md。"""
    problem = PROBLEMS.get(problem_id)
    if not problem:
        return api.create_response(request, {"detail": "Not found"}, status=404)
    filepath = _solution_dir(problem_id) / "translation.md"
    prompt = translation_prompt(problem.get("description", ""))
    return _sse_response(_stream_to_file(prompt, filepath))


# ────────────────────────────────────────────────────────────
# 题解
# ────────────────────────────────────────────────────────────

@api.get("/solutions/{problem_id}/solution/")
def get_solution(request, problem_id: int):
    """读取题解缓存，不存在返回 null。"""
    content = _read_md(_solution_dir(problem_id) / "solution.md")
    return {"content": content}


@api.get("/solutions/{problem_id}/solution/stream/")
def stream_solution(request, problem_id: int):
    """SSE：调用 Ollama 生成题解，边生成边推流，完成后写入 solution.md。"""
    problem = PROBLEMS.get(problem_id)
    if not problem:
        return api.create_response(request, {"detail": "Not found"}, status=404)
    filepath = _solution_dir(problem_id) / "solution.md"
    prompt = solution_prompt(problem)
    return _sse_response(_stream_to_file(prompt, filepath))


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
def stream_similar_problem(request, problem_id: int, n: int):
    """SSE：生成第 n 道相似题目，写入 similar/{n}/problem.md，同时清除旧 solution.md。"""
    problem = PROBLEMS.get(problem_id)
    if not problem:
        return api.create_response(request, {"detail": "Not found"}, status=404)
    dir_ = _similar_dir(problem_id, n)
    # 重新出题时删除旧题解，防止题目和题解不匹配
    old_solution = dir_ / "solution.md"
    if old_solution.exists():
        old_solution.unlink()
    filepath = dir_ / "problem.md"
    prompt = similar_problem_prompt(problem)
    return _sse_response(_stream_to_file(prompt, filepath))


@api.get("/solutions/{problem_id}/similar/{n}/solution/")
def get_similar_solution(request, problem_id: int, n: int):
    """读取第 n 道相似题解，不存在返回 null。"""
    content = _read_md(_similar_dir(problem_id, n) / "solution.md")
    return {"content": content}


@api.get("/solutions/{problem_id}/similar/{n}/solution/stream/")
def stream_similar_solution(request, problem_id: int, n: int):
    """SSE：生成第 n 道相似题的题解，写入 similar/{n}/solution.md。"""
    problem_text = _read_md(_similar_dir(problem_id, n) / "problem.md")
    if not problem_text:
        return api.create_response(request, {"detail": "先生成题目再生成题解"}, status=400)
    filepath = _similar_dir(problem_id, n) / "solution.md"
    prompt = similar_solution_prompt(problem_text)
    return _sse_response(_stream_to_file(prompt, filepath))

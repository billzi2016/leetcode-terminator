"""
测试举一反三相关端点：序号管理、题目/题解生成与重置逻辑。
"""
import pytest
from unittest.mock import patch


def _fake_chunks(*texts):
    """构造 mock streaming generator，模拟 Ollama 逐块返回结构化 dict。"""
    def gen():
        for t in texts:
            yield {"type": "token", "text": t, "thinking": False}
        yield {"type": "stats", "tokens": sum(len(t) for t in texts), "tps": 10.0}
    return gen()


# ── 序号列表 ────────────────────────────────────────────────

@pytest.mark.django_db
def test_similar_list_empty_when_no_dir(client, tmp_solutions):
    """similar 目录不存在时应返回空列表，不报错。"""
    r = client.get("/api/solutions/1/similar/")
    assert r.json()["items"] == []


@pytest.mark.django_db
def test_similar_list_returns_sorted_numbers(client, tmp_solutions):
    """已存在的序号应按升序返回。"""
    for n in [3, 1, 2]:
        (tmp_solutions / "1" / "similar" / str(n)).mkdir(parents=True)
    r = client.get("/api/solutions/1/similar/")
    assert r.json()["items"] == [1, 2, 3]


# ── 读取题目 ────────────────────────────────────────────────

@pytest.mark.django_db
def test_get_similar_problem_null_when_no_file(client, tmp_solutions):
    """problem.md 不存在时返回 null。"""
    r = client.get("/api/solutions/1/similar/1/problem/")
    assert r.json()["content"] is None


@pytest.mark.django_db
def test_get_similar_problem_returns_content(client, tmp_solutions):
    """problem.md 存在时返回文件内容。"""
    d = tmp_solutions / "1" / "similar" / "1"
    d.mkdir(parents=True)
    (d / "problem.md").write_text("相似题目描述", encoding="utf-8")

    r = client.get("/api/solutions/1/similar/1/problem/")
    assert r.json()["content"] == "相似题目描述"


# ── 生成题目 ────────────────────────────────────────────────

@pytest.mark.django_db
def test_stream_similar_problem_writes_file(client, tmp_solutions):
    """生成相似题目后应写入 problem.md。"""
    with patch("problems.api.stream_prompt", return_value=_fake_chunks("新题目内容")):
        r = client.get("/api/solutions/1/similar/1/problem/stream/")
        list(r.streaming_content)

    assert (tmp_solutions / "1" / "similar" / "1" / "problem.md").exists()


@pytest.mark.django_db
def test_regen_problem_deletes_old_solution(client, tmp_solutions):
    """
    重新出题时必须删除旧的 solution.md。
    防止新题目和旧题解不匹配。
    """
    d = tmp_solutions / "1" / "similar" / "1"
    d.mkdir(parents=True)
    (d / "problem.md").write_text("旧题目", encoding="utf-8")
    (d / "solution.md").write_text("旧题解", encoding="utf-8")

    with patch("problems.api.stream_prompt", return_value=_fake_chunks("新题目")):
        r = client.get("/api/solutions/1/similar/1/problem/stream/")
        list(r.streaming_content)

    assert not (d / "solution.md").exists(), "旧 solution.md 应被删除"
    assert (d / "problem.md").read_text(encoding="utf-8") == "新题目"


# ── 生成题解 ────────────────────────────────────────────────

@pytest.mark.django_db
def test_stream_similar_solution_writes_file(client, tmp_solutions):
    """生成相似题解后应写入 solution.md。"""
    d = tmp_solutions / "1" / "similar" / "1"
    d.mkdir(parents=True)
    (d / "problem.md").write_text("题目描述", encoding="utf-8")

    with patch("problems.api.stream_prompt", return_value=_fake_chunks("题解内容")):
        r = client.get("/api/solutions/1/similar/1/solution/stream/")
        list(r.streaming_content)

    assert (d / "solution.md").exists()


@pytest.mark.django_db
def test_stream_similar_solution_400_without_problem(client, tmp_solutions):
    """problem.md 不存在时不能生成题解，应返回 400。"""
    r = client.get("/api/solutions/1/similar/1/solution/stream/")
    assert r.status_code == 400


# ── 读取题解 ────────────────────────────────────────────────

@pytest.mark.django_db
def test_get_similar_solution_null_when_no_file(client, tmp_solutions):
    """solution.md 不存在时返回 null。"""
    r = client.get("/api/solutions/1/similar/1/solution/")
    assert r.json()["content"] is None


@pytest.mark.django_db
def test_get_similar_solution_returns_content(client, tmp_solutions):
    """solution.md 存在时返回内容。"""
    d = tmp_solutions / "1" / "similar" / "1"
    d.mkdir(parents=True)
    (d / "solution.md").write_text("## 思路\n哈希表", encoding="utf-8")

    r = client.get("/api/solutions/1/similar/1/solution/")
    assert r.json()["content"] == "## 思路\n哈希表"

"""
测试翻译 & 题解的读取端点（非 streaming）。
这些端点只做文件读取，不调用 Ollama，不需要 mock。
"""
import pytest


@pytest.mark.django_db
def test_translation_null_when_no_file(client, tmp_solutions):
    """文件不存在时 content 应为 null，前端据此决定显示"开始翻译"按钮。"""
    r = client.get("/api/solutions/1/translation/")
    assert r.status_code == 200
    assert r.json()["content"] is None


@pytest.mark.django_db
def test_translation_returns_cached_content(client, tmp_solutions):
    """文件存在时应返回文件内容，不重新调用 Ollama。"""
    path = tmp_solutions / "1" / "translation.md"
    path.parent.mkdir(parents=True)
    path.write_text("## 题目描述\n两数之和", encoding="utf-8")

    r = client.get("/api/solutions/1/translation/")
    assert r.json()["content"] == "## 题目描述\n两数之和"


@pytest.mark.django_db
def test_solution_null_when_no_file(client, tmp_solutions):
    """题解文件不存在时 content 应为 null。"""
    r = client.get("/api/solutions/1/solution/")
    assert r.json()["content"] is None


@pytest.mark.django_db
def test_solution_returns_cached_content(client, tmp_solutions):
    """题解文件存在时直接返回缓存，不重新生成。"""
    path = tmp_solutions / "1" / "solution.md"
    path.parent.mkdir(parents=True)
    path.write_text("## 思路分析\n使用哈希表", encoding="utf-8")

    r = client.get("/api/solutions/1/solution/")
    assert r.json()["content"] == "## 思路分析\n使用哈希表"


@pytest.mark.django_db
def test_different_problems_isolated(client, tmp_solutions):
    """不同题目的缓存文件互不干扰。"""
    for pid in [1, 2, 3]:
        path = tmp_solutions / str(pid) / "solution.md"
        path.parent.mkdir(parents=True)
        path.write_text(f"题解 {pid}", encoding="utf-8")

    for pid in [1, 2, 3]:
        r = client.get(f"/api/solutions/{pid}/solution/")
        assert r.json()["content"] == f"题解 {pid}"

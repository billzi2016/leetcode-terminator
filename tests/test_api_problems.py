"""
测试题目列表 & 单题详情 API。
"""
import pytest


@pytest.mark.django_db
def test_list_returns_all_problems(client):
    """不加筛选时应返回全部 2913 道题。"""
    r = client.get("/api/problems/?page_size=3000")
    assert r.status_code == 200
    assert r.json()["total"] == 2913


@pytest.mark.django_db
def test_list_pagination(client):
    """默认 page_size=50，第一页应恰好 50 条。"""
    r = client.get("/api/problems/")
    data = r.json()
    assert len(data["results"]) == 50
    assert data["page"] == 1


@pytest.mark.django_db
def test_search_by_title(client):
    """q= 应能在标题中模糊匹配，不区分大小写。"""
    r = client.get("/api/problems/?q=two+sum&page_size=100")
    results = r.json()["results"]
    assert any(p["title"] == "Two Sum" for p in results)


@pytest.mark.django_db
def test_search_by_slug(client):
    """q= 同时搜索 slug 字段。"""
    r = client.get("/api/problems/?q=two-sum&page_size=100")
    results = r.json()["results"]
    assert any(p["slug"] == "two-sum" for p in results)


@pytest.mark.django_db
def test_filter_by_difficulty_easy(client):
    """difficulty=Easy 时所有结果应为 Easy。"""
    r = client.get("/api/problems/?difficulty=Easy&page_size=3000")
    results = r.json()["results"]
    assert len(results) > 0
    assert all(p["difficulty"] == "Easy" for p in results)


@pytest.mark.django_db
def test_filter_by_difficulty_hard(client):
    """difficulty=Hard 时所有结果应为 Hard。"""
    r = client.get("/api/problems/?difficulty=Hard&page_size=3000")
    results = r.json()["results"]
    assert all(p["difficulty"] == "Hard" for p in results)


@pytest.mark.django_db
def test_results_sorted_by_id(client):
    """题目列表应按 frontend_id 升序排列。"""
    r = client.get("/api/problems/?page_size=100")
    ids = [p["id"] for p in r.json()["results"]]
    assert ids == sorted(ids)


@pytest.mark.django_db
def test_single_problem_found(client):
    """id=1 应返回 Two Sum 的完整数据。"""
    r = client.get("/api/problems/1/")
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Two Sum"
    assert "description" in data


@pytest.mark.django_db
def test_single_problem_not_found(client):
    """不存在的 id 应返回 404。"""
    r = client.get("/api/problems/99999/")
    assert r.status_code == 404

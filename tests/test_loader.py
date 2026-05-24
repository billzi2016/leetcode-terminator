"""
测试 loader.py：JSON 加载到内存字典的正确性。
"""
from problems.loader import PROBLEMS


def test_problems_loaded():
    """内存字典不为空，说明 JSON 成功加载。"""
    assert len(PROBLEMS) > 0


def test_problems_total_count():
    """期望恰好 2913 道题（来源 neenza/leetcode-problems）。"""
    assert len(PROBLEMS) == 2913


def test_key_is_int():
    """字典 key 必须是整数，方便 O(1) 按 id 查找。"""
    for key in list(PROBLEMS.keys())[:10]:
        assert isinstance(key, int)


def test_problem_required_fields():
    """每道题必须包含核心字段，缺失会导致前端渲染或 Prompt 组装出错。"""
    required = {"frontend_id", "title", "difficulty", "description"}
    for pid, p in list(PROBLEMS.items())[:50]:
        missing = required - p.keys()
        assert not missing, f"题目 {pid} 缺少字段: {missing}"


def test_first_problem_is_two_sum():
    """id=1 应为 Two Sum，作为基础数据完整性验证。"""
    assert PROBLEMS[1]["title"] == "Two Sum"


def test_difficulty_values():
    """difficulty 只允许三个合法值，避免前端徽章渲染出错。"""
    allowed = {"Easy", "Medium", "Hard"}
    for p in PROBLEMS.values():
        diff = p.get("difficulty", "")
        assert diff in allowed, f"非法 difficulty 值: {diff}"

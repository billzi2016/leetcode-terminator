"""
测试底层文件操作工具函数：路径生成、文件读取。
不依赖 Django client，纯 Python 单元测试。
"""
import pytest
from pathlib import Path
from unittest.mock import patch
from problems.api import _solution_dir, _similar_dir, _read_md


@pytest.fixture(autouse=True)
def patch_solutions_dir(tmp_solutions):
    """
    自动将所有测试的 SOLUTIONS_DIR 重定向到临时目录。
    _solution_dir / _similar_dir 运行时读 settings，所以 patch settings 即可生效。
    """
    pass  # tmp_solutions fixture 已完成 patch，此处只是显式标注依赖


def test_solution_dir_contains_problem_id(tmp_solutions):
    """_solution_dir 应返回以题目 id 结尾的路径。"""
    d = _solution_dir(42)
    assert d.name == "42"
    assert d.parent == tmp_solutions


def test_similar_dir_structure(tmp_solutions):
    """_similar_dir 应返回 {id}/similar/{n} 结构。"""
    d = _similar_dir(42, 3)
    assert d.name == "3"
    assert d.parent.name == "similar"
    assert d.parent.parent.name == "42"


def test_read_md_returns_none_for_missing_file(tmp_solutions):
    """文件不存在时 _read_md 应返回 None，不抛异常。"""
    result = _read_md(tmp_solutions / "nonexistent.md")
    assert result is None


def test_read_md_returns_file_content(tmp_path):
    """文件存在时应返回完整内容，包括 Markdown 特殊字符。"""
    f = tmp_path / "test.md"
    f.write_text("## 标题\n```python\nprint('hello')\n```", encoding="utf-8")
    assert _read_md(f) == "## 标题\n```python\nprint('hello')\n```"


def test_read_md_handles_utf8(tmp_path):
    """中文和 emoji 等 UTF-8 字符应正确读取。"""
    f = tmp_path / "test.md"
    f.write_text("中文内容 ✓", encoding="utf-8")
    assert _read_md(f) == "中文内容 ✓"


def test_different_ids_get_different_dirs(tmp_solutions):
    """不同题目 id 的路径不重叠，避免文件互相覆盖。"""
    assert _solution_dir(1) != _solution_dir(2)
    assert _similar_dir(1, 1) != _similar_dir(2, 1)
    assert _similar_dir(1, 1) != _similar_dir(1, 2)

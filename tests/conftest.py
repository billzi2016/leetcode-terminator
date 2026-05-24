"""
pytest 全局 fixtures。
- tmp_solutions: 用临时目录替换 SOLUTIONS_DIR，防止测试污染真实数据
- 其余 fixtures（client、settings）由 pytest-django 内置提供
"""
import pytest


@pytest.fixture
def tmp_solutions(tmp_path, settings):
    """
    将 settings.SOLUTIONS_DIR 重定向到 pytest 的 tmp_path。
    测试结束后 pytest 自动清理，不影响项目真实 solutions/ 目录。
    """
    settings.SOLUTIONS_DIR = tmp_path
    return tmp_path

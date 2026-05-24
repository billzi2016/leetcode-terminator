"""
测试 Ollama 健康检查端点。
mock ollama.Client，覆盖在线/离线/超时三种情况。
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
def test_health_ok_when_ollama_online(client):
    """Ollama 正常响应时应返回 status=ok。"""
    with patch("problems.ollama_client.ollama.Client") as mock_cls:
        mock_cls.return_value.list.return_value = MagicMock()
        r = client.get("/api/health/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.django_db
def test_health_down_when_ollama_offline(client):
    """Ollama 连接被拒时应返回 status=down。"""
    with patch("problems.ollama_client.ollama.Client") as mock_cls:
        mock_cls.return_value.list.side_effect = ConnectionRefusedError("refused")
        r = client.get("/api/health/")
    assert r.json()["status"] == "down"


@pytest.mark.django_db
def test_health_down_on_timeout(client):
    """Ollama 超时时应返回 status=down，不抛出未处理异常。"""
    with patch("problems.ollama_client.ollama.Client") as mock_cls:
        mock_cls.return_value.list.side_effect = TimeoutError("timeout")
        r = client.get("/api/health/")
    assert r.json()["status"] == "down"


@pytest.mark.django_db
def test_health_down_on_any_exception(client):
    """任意异常都应被捕获并返回 down，保证端点永不 500。"""
    with patch("problems.ollama_client.ollama.Client") as mock_cls:
        mock_cls.return_value.list.side_effect = RuntimeError("unexpected")
        r = client.get("/api/health/")
    assert r.json()["status"] == "down"

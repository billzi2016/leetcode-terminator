"""
测试 SSE streaming 端点：翻译和题解的生成与文件写入。
mock problems.api.stream_prompt，不实际调用 Ollama。
"""
import pytest
from unittest.mock import patch


def _fake_chunks(*texts):
    """构造 mock streaming generator，模拟 Ollama 逐块返回。"""
    def gen():
        for t in texts:
            yield t
    return gen()


@pytest.mark.django_db
def test_stream_translation_writes_file(client, tmp_solutions):
    """翻译流式生成完成后，内容应写入 translation.md。"""
    with patch("problems.api.stream_prompt", return_value=_fake_chunks("## 题目描述\n", "两数之和")):
        r = client.get("/api/solutions/1/translation/stream/")
        list(r.streaming_content)  # 消费流以触发文件写入

    filepath = tmp_solutions / "1" / "translation.md"
    assert filepath.exists()
    content = filepath.read_text(encoding="utf-8")
    assert "## 题目描述" in content
    assert "两数之和" in content


@pytest.mark.django_db
def test_stream_solution_writes_file(client, tmp_solutions):
    """题解流式生成完成后，内容应写入 solution.md。"""
    with patch("problems.api.stream_prompt", return_value=_fake_chunks("## 思路分析\n", "哈希表")):
        r = client.get("/api/solutions/1/solution/stream/")
        list(r.streaming_content)

    filepath = tmp_solutions / "1" / "solution.md"
    assert filepath.exists()
    assert "哈希表" in filepath.read_text(encoding="utf-8")


@pytest.mark.django_db
def test_stream_sse_format(client, tmp_solutions):
    """SSE 响应 Content-Type 必须是 text/event-stream。"""
    with patch("problems.api.stream_prompt", return_value=_fake_chunks("内容")):
        r = client.get("/api/solutions/1/translation/stream/")
        assert "text/event-stream" in r.get("Content-Type", "")


@pytest.mark.django_db
def test_stream_done_signal(client, tmp_solutions):
    """流结束时应包含 [DONE] 信号，前端据此关闭 EventSource。"""
    with patch("problems.api.stream_prompt", return_value=_fake_chunks("内容")):
        r = client.get("/api/solutions/1/translation/stream/")
        chunks = [c.decode() for c in r.streaming_content]
    assert any("[DONE]" in c for c in chunks)


@pytest.mark.django_db
def test_stream_overwrites_existing_file(client, tmp_solutions):
    """重新生成时应覆盖已有文件，不追加。"""
    path = tmp_solutions / "1" / "solution.md"
    path.parent.mkdir(parents=True)
    path.write_text("旧内容", encoding="utf-8")

    with patch("problems.api.stream_prompt", return_value=_fake_chunks("新内容")):
        r = client.get("/api/solutions/1/solution/stream/")
        list(r.streaming_content)

    assert path.read_text(encoding="utf-8") == "新内容"


@pytest.mark.django_db
def test_stream_404_for_unknown_problem(client, tmp_solutions):
    """不存在的题目 id 应返回 404，不调用 Ollama。"""
    r = client.get("/api/solutions/99999/translation/stream/")
    assert r.status_code == 404


@pytest.mark.django_db
def test_stream_creates_parent_dirs(client, tmp_solutions):
    """文件所在目录不存在时应自动创建，不报 FileNotFoundError。"""
    with patch("problems.api.stream_prompt", return_value=_fake_chunks("内容")):
        r = client.get("/api/solutions/42/solution/stream/")
        list(r.streaming_content)

    assert (tmp_solutions / "42" / "solution.md").exists()

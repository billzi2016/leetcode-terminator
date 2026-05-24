# LeetCode Terminator

本地 LeetCode 刷题辅助工具。左侧题目列表，右侧展示英文原题、中文翻译、中文题解，并支持举一反三。由本地 Ollama `gpt-oss:120b` 驱动，所有生成结果持久化为 Markdown 文件。

## 前置条件

- Python 3.11+
- [Ollama](https://ollama.com) 已安装并在运行
- `gpt-oss:120b` 模型已拉取

```bash
ollama pull gpt-oss:120b
```

## 安装

```bash
git clone <repo>
cd leetcode-terminator

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## 启动

```bash
python manage.py runserver
```

浏览器访问 `http://localhost:8000`

## 运行测试

```bash
pytest
```

## Docker

```bash
docker build -t leetcode-terminator .

# solutions/ 挂载为 volume，容器重建不丢数据
docker run -v $(pwd)/solutions:/app/solutions -p 8000:8000 leetcode-terminator
```

## 目录结构

```
leetcode-terminator/
├── config/             Django 配置
├── problems/           主应用（API、loader、prompts、templates）
├── static/vendor/      前端静态文件（htmx、marked、highlight.js）
├── solutions/          生成的 Markdown 文件（按题号归档）
│   └── {id}/
│       ├── translation.md
│       ├── solution.md
│       └── similar/
│           └── {n}/
│               ├── problem.md
│               └── solution.md
├── tests/              pytest 测试
└── leetcode_problems.json  2913 道题数据
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama 地址，Docker 内改为 `http://host.docker.internal:11434` |
| `OLLAMA_MODEL` | `gpt-oss:120b` | 使用的模型名 |

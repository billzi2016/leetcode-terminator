# LeetCode Terminator

> LeetCode 大概率已经凉了。
>
> 这个项目从零到完整功能，AI 不到半小时生成完毕——翻译、题解、举一反三、流式输出、侧边栏筛选、Markdown 渲染、代码高亮行号、持久化缓存、Docker 部署、47 个测试全绿。保守估计是一名人类工程师一周的工作量。
>
> 代码是纯 AI 写的。

---

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
./start.sh
```

浏览器访问 `http://localhost:8000`

## 停止

```bash
# 方式一：Ctrl+C（前台运行时）

# 方式二：按端口号杀掉进程
kill $(lsof -ti:8000)

# 方式三：查找后手动确认
lsof -i:8000
kill <PID>
```

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
├── start.sh            一键启动脚本
└── leetcode_problems.json  2913 道题数据
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama 地址，Docker 内改为 `http://host.docker.internal:11434` |
| `OLLAMA_MODEL` | `gpt-oss:120b` | 使用的模型名 |

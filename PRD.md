# LeetCode Terminator — PRD

## 产品概述

本地运行的 LeetCode 刷题辅助工具。用户在左侧选择题目，右侧展示英文原题与 AI 生成的中文题解（思路 + 代码）。题解由本地 Ollama（gpt-oss-120b）生成，首次生成后持久化为 Markdown 文件，后续直接读取。

---

## 目标用户

- 本人（本地工具，非公开部署）

---

## 技术栈

| 层级 | 选型 |
|------|------|
| 后端框架 | Django |
| API 层 | Django Ninja |
| 模板 | Django Templates（仅页面壳） |
| LLM | Ollama 本地 `gpt-oss-120b`，使用官方 `ollama` Python 包 |
| 题目数据 | `leetcode_problems.json`（2913 题，已下载） |
| 题解存储 | `solutions/{id}/` 文件夹，所有内容归在题号下 |
| MD → HTML | 前端 `marked.js`（本地） |
| 代码高亮 | `highlight.js`（本地），与 marked.js 集成 |
| 无刷新交互 | HTMX（本地） |
| Streaming | `django-eventstream`（SSE），前端用标准 `EventSource` |
| 搜索过滤 | `django-filter` + Ninja 集成 |
| 前端依赖 | 无 npm，所有 JS/CSS 下载到 `static/vendor/` 本地 serve |
| 原则 | 钉死 Ollama 本地方案，不考虑 OpenRouter 等远程 API；能用套件就用 |

---

## 数据来源

- **题目 JSON**：`leetcode_problems.json`，来源 [neenza/leetcode-problems](https://github.com/neenza/leetcode-problems)
- 字段：`frontend_id`、`title`、`difficulty`、`problem_slug`、`topics`、`description`
- 总量：2913 题
- 加载方式：Django 启动时读一次，存模块级内存字典，不入数据库

---

## 数据格式策略

| 数据 | 格式 | 原因 |
|------|------|------|
| 原始题目 | JSON（内存字典） | 有结构化字段，用于搜索、筛选、传给 Ollama |
| 原题 `description` | 前端直接文本渲染 | 无需转换，plain text 即可 |
| Ollama 输出 | Markdown 文件 | LLM 对 MD 格式遵循稳定；代码块含特殊字符，JSON 转义极不可靠；streaming 下解析不完整 JSON 是噩梦 |

**结论**：不让 Ollama 返回 JSON，不把原题转成 MD。两种数据各司其职，不混用。

---

## 题解存储策略

每道题对应一个文件夹，翻译和题解分开存，各自独立生成、独立缓存。

**存储路径：**

```
solutions/{id}/
├── translation.md        # 中文题目翻译
├── solution.md           # 中文题解（思路+代码+复杂度）
└── similar/
    ├── 1/
    │   ├── problem.md    # 举一反三第 1 题
    │   └── solution.md
    └── 2/ ...
```

**交互逻辑：**

- 点击题目 → 立即显示英文原题（内存 JSON，毫秒级）
- `translation.md` 存在 → 显示中文翻译 + [重新翻译] 按钮
- `translation.md` 不存在 → 显示 [开始翻译] 按钮
- `solution.md` 存在 → 显示题解 + [重新生成] 按钮
- `solution.md` 不存在 → 显示 [生成题解] 按钮
- 所有生成均使用 Ollama streaming，token 边出边显示
- 重新生成/重新翻译：覆盖写入同一文件

---

## API 端点（Django Ninja）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/problems/` | 题目列表，支持 `q=` 关键词搜索、`difficulty=` 筛选 |
| GET | `/api/problems/{id}/` | 单题详情（标题、难度、标签、英文原题） |
| GET | `/api/solutions/{id}/translation/` | 读取中文翻译，不存在返回 `null` |
| GET | `/api/solutions/{id}/translation/stream/` | SSE：Ollama 翻译原题，写入 `translation.md` |
| GET | `/api/solutions/{id}/solution/` | 读取题解，不存在返回 `null` |
| GET | `/api/solutions/{id}/solution/stream/` | SSE：Ollama 生成题解，写入 `solution.md` |
| GET | `/api/health/` | 检测 Ollama 是否在线，返回 `{status: "ok"\|"down"}` |
| GET | `/api/solutions/{id}/similar/` | 返回已生成的序号列表，如 `[1, 2, 3]` |
| GET | `/api/solutions/{id}/similar/{n}/problem/` | 读取第 n 道相似题，不存在返回 `null` |
| GET | `/api/solutions/{id}/similar/{n}/problem/stream/` | SSE：生成第 n 道相似题，写入文件 |
| GET | `/api/solutions/{id}/similar/{n}/solution/stream/` | SSE：生成第 n 道题解，写入文件 |

---

## Ollama 健康监控

- 右上角常驻状态指示器：绿点 = 在线 / 红点 = 离线
- 前端每 15 秒轮询一次 `/api/health/`
- 后端 ping `localhost:11434`，200 = ok，超时或报错 = down
- Ollama 离线时，[生成题解] 和 [举一反三] 按钮置灰并提示"Ollama 未运行"

---

## 举一反三

基于原题让 Ollama 出相似题，再给出解法。分两次独立调用，避免单次输出过长导致格式混乱。每次点击生成一道新题，按序号累积，不覆盖历史。

**多次生成流程：**

```
用户点击 [+ 举一反三]
      │
      后端扫 solutions/similar/{id}/ 目录，取最大序号 n+1
      │
      ▼
  第一次调用：原题完整 JSON → Ollama（SSE stream）
  只输出新题目本身，写入 solutions/{id}/similar/{n}/problem.md
      │
      ▼
  用户点击 [生成解法]（题目生成完后出现）
      │
      ▼
  第二次调用：新题目文本 → Ollama（SSE stream）
  输出思路+题解+心得，写入 solutions/{id}/similar/{n}/solution.md
```

**重新生成：**

- 题目不满意：[重新出题] → 覆盖 `solutions/{id}/similar/{n}/problem.md`，同时删除对应 `solution.md`
- 题解不满意：[重新解题] → 覆盖 `solutions/{id}/similar/{n}/solution.md`
- 原题题解不满意：[重新生成] → 覆盖 `solutions/{id}/solution.md`

**UI 交互：**

```
[+ 举一反三]                    ← 每次点击生成新的一道
 #1  #2  #3  ...               ← tab 切换已有的，当前高亮
 [重新出题]  [重新解题]         ← 当前 tab 下显示
```

**存储路径：**（与题解存储策略一致，similar 嵌套在题号文件夹内）

```
solutions/{id}/
├── translation.md
├── solution.md
└── similar/
    ├── 1/
    │   ├── problem.md
    │   └── solution.md
    └── 2/ ...
```

---

## Ollama Prompt 结构

所有 Prompt 均明确要求输出 Markdown 格式，防止模型输出 plain text 或 JSON。
完整题目 JSON 对象直接传入，模型不依赖自身记忆，避免幻觉。

**原题翻译：**

```
你是专业的技术翻译，请将以下 LeetCode 题目翻译成中文，输出格式为 Markdown。
保留所有代码示例、数字、变量名，只翻译文字描述部分。

原题内容：
{description}

请严格按照以下 Markdown 格式输出，不要输出其他内容：

## 题目描述
...

## 示例
...

## 约束条件
...
```

**原题题解：**

```
你是 LeetCode 解题专家，请用中文回答，输出格式为 Markdown。

以下是题目的完整数据（JSON 格式）：
{problem_json}

请严格按照以下 Markdown 格式输出，不要输出其他内容，代码统一使用 Python：

## 题目理解
用中文复述题意，说清楚输入、输出、约束条件。

## 思路分析
分析解题思路，说明为什么选择这种方法。

## 代码实现
​```python
...
​```

## 复杂度分析
时间复杂度：...
空间复杂度：...
```

**举一反三 — 第一次调用（出题）：**

```
你是 LeetCode 出题专家，请用中文出题，输出格式为 Markdown。

以下是一道 LeetCode 题目的完整数据：
{problem_json}

请根据这道题，出一道风格相似、考察同类知识点的新题目。
严格只输出题目本身，格式如下，不要输出答案或任何提示：

## 题目描述
...

## 输入输出格式
...

## 示例
...

## 约束条件
...
```

**举一反三 — 第二次调用（解题）：**

```
你是 LeetCode 解题专家，请用中文回答，输出格式为 Markdown。

以下是一道题目：
{generated_problem}

请严格按照以下 Markdown 格式输出，不要输出其他内容，代码统一使用 Python：

## 思路分析
...

## 代码实现
​```python
...
​```

## 复杂度分析
时间复杂度：...
空间复杂度：...

## 心得
...
```

---

## 页面布局

单页应用，两栏布局，无路由跳转。

```
┌──────────┬─────────────────────────────────────────┬──────────┐
│ 搜索框   │ # 42. 接雨水  Hard | Array · DP · Stack  │ ● Ollama │
│ 难度筛选 ├─────────────────────────────────────────┴──────────┤
│──────────│ 英文原题（直接渲染 description）                    │
│ 1. 两数和│─────────────────────────────────────────────────── │
│ 2. 两数加│ 中文翻译（marked.js）                               │
│ ...      │ [开始翻译] / [重新翻译]                             │
│ 42. 接雨●│─────────────────────────────────────────────────── │
│ ...      │ 中文题解（marked.js + highlight.js）                │
│          │ [生成题解] / [重新生成]                             │
│          │─────────────────────────────────────────────────── │
│          │ 举一反三  #1  #2  #3  [+ 新增]                     │
│          │ [生成解法] / [重新出题] / [重新解题]                │
└──────────┴────────────────────────────────────────────────────┘
```

- 左栏：260px，固定，可滚动题目列表
- 右栏：flex-grow，独立滚动
- 点击左栏条目：HTMX 触发，右栏无刷新更新
- 当前选中题目高亮

---

## 目录结构

```
leetcode-terminator/
├── manage.py
├── config/
│   └── settings.py
├── problems/
│   ├── api.py                        # Ninja router
│   ├── views.py                      # 单个 view，渲染 index.html
│   ├── loader.py                     # JSON → 内存字典
│   └── templates/
│       └── index.html
├── static/
│   └── vendor/
│       ├── htmx.min.js
│       ├── marked.min.js
│       ├── highlight.min.js
│       └── highlight-github-dark.min.css
├── solutions/                        # 打开即是题号列表
│   └── {id}/
│       ├── translation.md            # 中文题目翻译
│       ├── solution.md               # 中文题解
│       └── similar/
│           ├── 1/
│           │   ├── problem.md        # 举一反三第 1 题
│           │   └── solution.md
│           └── 2/ ...
├── PRD.md
└── leetcode_problems.json
```

---

## 依赖

```
django
django-ninja
django-eventstream
django-filter
ollama
```

前端静态文件（全部下载到 `static/vendor/`，无需 npm，无需网络）：

```
static/vendor/
├── htmx.min.js
├── marked.min.js
├── highlight.min.js
└── highlight-github-dark.min.css
```

模板中用 Django `{% static %}` 引用：

```html
<link rel="stylesheet" href="{% static 'vendor/highlight-github-dark.min.css' %}">
<script src="{% static 'vendor/htmx.min.js' %}"></script>
<script src="{% static 'vendor/marked.min.js' %}"></script>
<script src="{% static 'vendor/highlight.min.js' %}"></script>
```

marked.js 配置接入 highlight.js（3 行，官方推荐方式）：

```javascript
marked.setOptions({
  highlight: (code, lang) => hljs.highlight(code, { language: lang || 'python' }).value
});
```

---

## 实施顺序

1. `startproject` + `startapp` + Ninja + django-eventstream 接入
2. `loader.py`：JSON 加载到内存
3. 下载前端静态文件到 `static/vendor/`
4. API 端点：题目列表、单题详情、health check
5. SSE streaming：翻译、题解、举一反三（共 7 个 stream 端点）
6. `index.html`：三栏右侧布局 + HTMX + marked.js + highlight.js
7. 搜索 / 难度筛选（django-filter）
8. 补全测试（pytest-django），确保每个端点和文件操作有覆盖
9. README、pyproject.toml、requirements.txt、Dockerfile

---

## 测试

使用 `pytest` + `pytest-django`，每个功能模块对应独立测试文件。所有测试均有详尽注释，说明测试目的和边界条件。

**测试文件结构：**

```
tests/
├── conftest.py                  # pytest fixtures：Django client、临时 solutions 目录、mock 题目数据
├── test_loader.py               # JSON 加载：字段完整性、内存字典结构、2913 题数量
├── test_api_problems.py         # 题目列表：分页、q= 搜索、difficulty= 筛选；单题详情：存在/不存在
├── test_api_solutions.py        # 翻译/题解读取：有缓存返回内容、无缓存返回 null
├── test_api_health.py           # Ollama 在线返回 ok、模拟离线返回 down
├── test_api_stream.py           # SSE stream：mock ollama 包，验证 chunk 推送、文件写入、覆盖逻辑
├── test_api_similar.py          # 举一反三：序号列表、新增自增、题目/题解读取、重新出题删除 solution
└── test_file_ops.py             # 文件操作：路径生成、并发写入安全、重新生成覆盖
```

**覆盖要点：**

| 功能 | 测试场景 |
|------|---------|
| JSON 加载 | 正常加载、字段缺失降级、重复 id 处理 |
| 题目列表 | 无筛选返回全部、q= 匹配标题/slug、difficulty= 大小写兼容、组合筛选 |
| 单题详情 | 存在返回完整 JSON、不存在返回 404 |
| 翻译/题解读取 | 文件存在返回内容、文件不存在返回 null |
| SSE stream | mock ollama streaming，验证每个 chunk 推送到响应、完成后文件写入正确 |
| 重新生成 | 覆盖已有文件内容更新 |
| 举一反三新增 | 首次创建 `1/`、第二次创建 `2/`，序号自动递增 |
| 重新出题 | 覆盖 `problem.md`，`solution.md` 同时删除 |
| Health check | mock `ollama.Client`，分别测试在线/离线/超时 |

**注释规范：**

- 每个函数顶部写明：做什么、为什么这样做、边界条件
- 非显而易见的逻辑必须有行内注释
- 测试函数命名格式：`test_<功能>_<场景>`，如 `test_similar_regenerate_deletes_solution`

---

## 项目文件

### README.md

包含：项目简介、前置条件（Ollama 已安装并运行 gpt-oss-120b）、安装步骤、启动命令、目录说明。

### pyproject.toml

```toml
[project]
name = "leetcode-terminator"
version = "0.1.0"
requires-python = ">=3.11"

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
python_files = ["tests/test_*.py"]

[tool.ruff]
line-length = 100
```

### requirements.txt

```
django
django-ninja
django-eventstream
django-filter
ollama
pytest
pytest-django
ruff
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ollama 运行在宿主机，容器内用 host.docker.internal 访问
ENV OLLAMA_HOST=http://host.docker.internal:11434

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

> **注意**：`solutions/` 目录建议挂载为 volume，避免容器重建丢失已生成的 MD 文件：
> `docker run -v $(pwd)/solutions:/app/solutions -p 8000:8000 leetcode-terminator`

---

## 暂不做

- 用户账号 / 进度追踪
- 多语言切换
- 公开部署
- 预生成所有题解
- 代码执行 / 判题

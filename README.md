# LeetCode Terminator

> LeetCode 大概率已经凉了。
>
> 这个项目从零到完整功能，AI 不到半小时生成完毕——翻译、题解、举一反三、流式输出、侧边栏筛选、Markdown 渲染、代码高亮行号、持久化缓存、Docker 部署、47 个测试全绿。保守估计是一名人类工程师一周的工作量。
>
> 代码是纯 AI 写的。

---

## 这意味着什么

软件工程的考核重心正在位移。

以前面试考你能不能手写二叉树、背出快排、默写 DP 转移方程。这些能力在 AI 面前不值一提——10 秒钟，任何算法题都有完整题解、复杂度分析、多语言实现。**代码能力会往后放，但不会消失。** 你仍然需要读懂代码、判断对错、知道为什么这样写。

真正会被放大的能力是：

- **系统思维**：你能不能把一个模糊的需求拆成可执行的模块？
- **架构判断**：选什么框架、怎么分层、数据往哪里流？
- **全栈视野**：前端怎么交互、后端怎么设计 API、部署怎么跑起来？
- **驾驭 AI 的能力**：你能不能让 AI 做正确的事，而不是让 AI 带着你跑偏？

本质上，**你要知道自己在做什么**。AI 是工具，不是大脑。你不理解系统，AI 生成的代码就是一堆无法维护的垃圾。

你真的懂，写出来的东西地基是稳的。你不懂，写出来地基就是毁的——而且你看不出来它毁在哪里。

LeetCode 和做项目，这两件事的能力重叠很少。LeetCode 考的是算法直觉和数学推导，大多数刷题高手从来没搭过一个完整的系统。真正的项目需要你做出一系列判断：存储用文件还是数据库、API 怎么分层、前端交互如何设计、LLM 的输出怎么结构化——这些判断没有标准答案，考的是你对整个系统的理解深度。

在这个项目里，AI 是执行层，人是架构师。代码是 AI 写的，但每一个关键决策——存储方式、框架选型、交互逻辑、Prompt 策略——都是人做的。换一个对 Django、LLM、前端没有真实感知的人来，即使用同一个 AI，项目也不会长成这样。能刷出 LeetCode hard 的人，不一定能做出一个完整的项目；能做出完整项目的人，才真正理解软件是怎么运转的。

你真的懂，写出来的东西地基是稳的。你不懂，写出来地基就是毁的——而且你看不出来它毁在哪里。能刷出 LeetCode hard 的人，不一定能做出一个完整的项目；能做出完整项目的人，才真正理解软件是怎么运转的。

---

## SDD：Spec-Driven Development

本项目采用 **SDD（规格驱动开发）** 模式。

流程是：**先写 Spec，代码从 Spec 里长出来。**

```
需求 → PRD（产品规格文档）→ 技术设计 → AI 生成代码 → 测试验证
```

项目里的 [`PRD.md`](./PRD.md) 就是这个 Spec。它定义了：

- 页面布局和交互逻辑
- API 端点和数据格式
- 文件存储结构
- Prompt 模板的设计原则
- 测试覆盖范围

AI 没有凭空发明任何东西，每一个模块都能在 Spec 里找到对应的描述。Spec 写得越清楚，AI 生成的代码就越准确，返工就越少。

**SDD 的核心价值不是省时间，而是把"你到底要什么"这件事逼清楚。** 很多项目烂掉不是因为代码写得差，而是需求从来没想清楚过。

---

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Django 6 + Django Ninja (REST API) |
| AI 接入 | Ollama Python SDK（本地，无需联网） |
| 前端 | 原生 JS + HTMX + marked.js + highlight.js |
| 数据 | 2913 道 LeetCode 题目 JSON，启动时加载进内存 |
| 持久化 | Markdown 文件，按题号归档 |
| 测试 | pytest + pytest-django，47 个测试 |
| 部署 | Docker |

---

## 数据来源

- **题目 JSON**：`leetcode_problems.json`，来源 [neenza/leetcode-problems](https://github.com/neenza/leetcode-problems)

---

## 前置条件

- Python 3.11+
- [Ollama](https://ollama.com) 已安装并在运行
- `gpt-oss:120b` 模型已拉取

```bash
ollama pull gpt-oss:120b
```

## 安装

```bash
git clone https://github.com/billzi2016/leetcode-terminator
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
├── PRD.md              产品规格文档（Spec）
├── start.sh            一键启动脚本
└── leetcode_problems.json  2913 道题数据
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama 地址，Docker 内改为 `http://host.docker.internal:11434` |
| `OLLAMA_MODEL` | `gpt-oss:120b` | 使用的模型名 |

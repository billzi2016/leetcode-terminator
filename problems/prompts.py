"""
所有 Ollama Prompt 模板集中在此文件。
修改提示词只需改这里，不用动业务逻辑。
"""
import json


def translation_prompt(description: str) -> str:
    """原题中文翻译：只翻译文字，保留代码示例和变量名。"""
    return f"""你是专业的技术翻译，请将以下 LeetCode 题目翻译成中文，输出格式为 Markdown。
保留所有代码示例、数字、变量名，只翻译文字描述部分。

原题内容：
{description}

请严格按照以下 Markdown 格式输出，不要输出其他内容：

## 题目描述

## 示例

## 约束条件
"""


def solution_prompt(problem: dict) -> str:
    """原题中文题解：先给最直觉暴力解，再给最优雅解，符合学习递进规律。"""
    return f"""你是 LeetCode 解题专家，请用中文回答，输出格式为 Markdown。

以下是题目的完整数据（JSON 格式）：
{json.dumps(problem, ensure_ascii=False, indent=2)}

请严格按照以下 Markdown 格式输出，不要输出其他内容，代码统一使用 Python：

## 解法一：暴力 / 最直觉解
说明这种解法的思路，适合第一反应时想到。

```python
```

**复杂度**
- 时间复杂度：
- 空间复杂度：

---

## 解法二：最优解
说明为什么这种解法更优，优化了哪里。

```python
```

**复杂度**
- 时间复杂度：
- 空间复杂度：

---

## 对比小结
一句话说清楚两种解法的取舍。
"""


def similar_problem_prompt(problem: dict) -> str:
    """举一反三出题：基于原题 JSON 生成新题目，只输出题目本身。"""
    return f"""你是 LeetCode 出题专家，请用中文出题，输出格式为 Markdown。

以下是一道 LeetCode 题目的完整数据：
{json.dumps(problem, ensure_ascii=False, indent=2)}

请根据这道题，出一道风格相似、考察同类知识点的新题目。
严格只输出题目本身，不要输出答案或任何提示，格式如下：

## 题目描述

## 输入输出格式

## 示例

## 约束条件
"""


def similar_solution_prompt(generated_problem: str) -> str:
    """举一反三解题：基于生成的新题目给出思路、题解、心得。"""
    return f"""你是 LeetCode 解题专家，请用中文回答，输出格式为 Markdown。

以下是一道题目：
{generated_problem}

请严格按照以下 Markdown 格式输出，不要输出其他内容，代码统一使用 Python：

## 思路分析

## 代码实现

```python
```

## 复杂度分析
时间复杂度：
空间复杂度：

## 心得
"""

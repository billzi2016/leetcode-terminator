## 题目描述

你的汽车从位置 0 开始，速度为 +1，位于无限数轴上。你的汽车可以行驶到负数位置。你的汽车会根据指令序列自动行驶，指令包括 **'A'**（加速）和 **'R'**（调头）：例如，在指令 `"AAR"` 之后，汽车的位置依次为 `0 --> 1 --> 3 --> 3`，速度依次为 `1 --> 2 --> 4 --> -1`。给定目标位置 `target`，返回到达该位置的最短指令序列的长度。

## 示例

**示例 1：**
``` 
Input: target = 3
Output: 2
Explanation: 
The shortest instruction sequence is "AA".
Your position goes from 0 --> 1 --> 3.
```

**示例 2：**
``` 
Input: target = 6
Output: 5
Explanation: 
The shortest instruction sequence is "AAARA".
Your position goes from 0 --> 1 --> 3 --> 7 --> 7 --> 6.
```

## 约束条件

- `1 <= target <= 104`
## 题目描述

给定一个整数 `x`，如果 `x` 是回文数则返回 `true`，否则返回 `false`。

## 示例

**示例 1:**  
```
Input: x = 121
Output: true
Explanation: 121 reads as 121 from left to right and from right to left.
```

**示例 2:**  
```
Input: x = -121
Output: false
Explanation: From left to right, it reads -121. From right to left, it becomes 121-. Therefore it is not a palindrome.
```

**示例 3:**  
```
Input: x = 10
Output: false
Explanation: Reads 01 from right to left. Therefore it is not a palindrome.
```

## 约束条件

- `-231 <= x <= 231 - 1`
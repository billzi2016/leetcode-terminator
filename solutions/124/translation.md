## 题目描述

在二叉树中，一条路径是由一系列节点构成，使得序列中每一对相邻节点之间都有一条边相连。每个节点在序列中至多出现一次。需要注意的是，路径不一定要经过根节点。  
路径的路径和（path sum）指的是路径上所有节点值的总和。  
给定二叉树的根节点 `root`，返回任意非空路径的最大路径和。

## 示例

**示例 1：**
```
Input: root = [1,2,3]
Output: 6
Explanation: The optimal path is 2 -> 1 -> 3 with a path sum of 2 + 1 + 3 = 6.
```

**示例 2：**
```
Input: root = [-10,9,20,null,null,15,7]
Output: 42
Explanation: The optimal path is 15 -> 20 -> 7 with a path sum of 15 + 20 + 7 = 42.
```

## 约束条件

- `The number of nodes in the tree is in the range [1, 3 * 104].`
- `-1000 <= Node.val <= 1000`
## 题目描述

给定两个已排序的数组 `nums1` 和 `nums2`，它们的大小分别为 `m` 和 `n`，返回这两个排序数组的中位数。整体运行时间复杂度要求为 `O(log (m+n))`。

## 示例

**示例 1：**
``` 
Input: nums1 = [1,3], nums2 = [2]
Output: 2.00000
Explanation: merged array = [1,2,3] and median is 2.
```

**示例 2：**
``` 
Input: nums1 = [1,2], nums2 = [3,4]
Output: 2.50000
Explanation: merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.
```

## 约束条件
- `nums1.length == m`
- `nums2.length == n`
- `0 <= m <= 1000`
- `0 <= n <= 1000`
- `1 <= m + n <= 2000`
- `-106 <= nums1[i], nums2[i] <= 106`
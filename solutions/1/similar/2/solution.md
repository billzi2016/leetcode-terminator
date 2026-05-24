## 思路分析

我们需要在数组 `nums` 中找到唯一的一对下标 `(i, j)`，使得  

```
nums[j] - nums[i] = k   且 i != j
```

只要遍历一次数组并利用哈希表（字典）记录已经出现过的元素值及其下标，就可以在 **O(1)** 的时间内判断当前元素是否能与之前的某个元素构成所需的差值。

具体步骤：

1. 创建空字典 `pos`，键为数组中的值，值为该值第一次出现的下标。
2. 从左到右遍历数组 `nums`，设当前下标为 `idx`，当前值为 `val`。
3. 要满足 `nums[j] - nums[i] = k`，有两种可能  
   - `val` 充当 `nums[j]`：此时我们需要在之前出现过的 `val - k`（即 `nums[i] = val - k`）。  
   - `val` 充当 `nums[i]`：此时我们需要在之前出现过的 `val + k`（即 `nums[j] = val + k`）。  
   检查这两种情况是否在字典 `pos` 中存在即可。
4. 一旦找到匹配的下标，直接输出这对下标（顺序不限），结束程序。
5. 若当前值尚未加入字典，则把 `val : idx` 加入 `pos`，继续遍历。

因为题目保证恰好只有唯一的一组满足条件的下标，以上过程一定能够在遍历结束前找到答案。

## 代码实现

```python
import sys

def main() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    n = int(next(it))
    nums = [int(next(it)) for _ in range(n)]
    k = int(next(it))

    # 哈希表：值 -> 第一次出现的下标
    pos = {}

    for idx, val in enumerate(nums):
        # 情形 1：当前值作为 nums[j]
        need_i = val - k          # nums[i] = val - k
        if need_i in pos:
            print(pos[need_i], idx)
            return

        # 情形 2：当前值作为 nums[i]
        need_j = val + k          # nums[j] = val + k
        if need_j in pos:
            print(idx, pos[need_j])
            return

        # 记录当前值（只记录第一次出现，满足唯一解的前提）
        if val not in pos:
            pos[val] = idx

if __name__ == "__main__":
    main()
```

## 复杂度分析

- **时间复杂度**：`O(n)`，只遍历一次数组，每次查找/插入哈希表均摊为 `O(1)`。
- **空间复杂度**：`O(n)`，最坏情况下哈希表要存储所有不同的数组元素。

## 心得

- 利用哈希表可以把 “在数组中找差值为 `k` 的两个数” 这类问题从 `O(n²)` 降到 `O(n)`，是非常常用且高效的技巧。
- 题目保证唯一解，使得我们不必担心出现多种匹配导致的歧义，只要第一条满足条件的即为答案。
- 在实现时注意两种可能的角色（`nums[i]` 与 `nums[j]`），只检查一种会漏掉 `k` 为负数或正数的情况。这里统一检查两种即可。
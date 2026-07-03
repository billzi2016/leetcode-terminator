## 思路分析

二进制回文的本质是 **从最高位到最低位的序列** 与 **从最低位到最高位的序列** 完全相同。  
设整数 `x` 的二进制位数为 `L`（`x = 0` 时 `L = 1`），则第 `i` 位（0 为最低位）可以通过

```
bit_i = (x >> i) & 1
```

得到。我们只需要把最高位 `L‑1` 与最低位 `0`、次高位 `L‑2` 与次低位 `1` …… 两两比较，若全部相等则二进制是回文。

实现步骤：

1. **特殊情况**：`x == 0` 直接返回 `true`（二进制为 `0`）。
2. 计算二进制位数 `L`  
   `L = x.bit_length()`（Python 内置），若 `x == 0` 则 `L = 1`。
3. 设指针 `left = L‑1`、`right = 0`，循环条件为 `left > right`。  
   - 取出 `left`、`right` 两位的值并比较。  
   - 若不相等，返回 `false`。  
   - 否则 `left -= 1`、`right += 1` 继续比较。
4. 循环结束后未发现不相等的位，说明是回文，返回 `true`。

该算法只使用了常数级的变量，循环次数为二进制位数的一半，时间复杂度 `O(log x)`，空间复杂度 `O(1)`。

---

## 代码实现

```python
import sys

def is_binary_palindrome(x: int) -> bool:
    """判断整数 x 的二进制表示（不含前导零）是否为回文"""
    if x == 0:
        return True

    # 二进制位数，等价于 floor(log2(x)) + 1
    L = x.bit_length()   # Python 的内置函数，返回非零整数的位数

    left = L - 1   # 最高位索引
    right = 0      # 最低位索引

    while left > right:
        left_bit = (x >> left) & 1
        right_bit = (x >> right) & 1
        if left_bit != right_bit:
            return False
        left -= 1
        right += 1

    return True


def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    x = int(data)
    print('true' if is_binary_palindrome(x) else 'false')


if __name__ == "__main__":
    main()
```

---

## 复杂度分析

- **时间复杂度**：`O(log x)`  
  循环次数至多为二进制位数的一半，二进制位数为 `⌊log₂ x⌋ + 1`，因此整体是 `O(log x)`。

- **空间复杂度**：`O(1)`  
  只使用了若干整数变量，与输入规模无关。

---

## 心得

本题的关键在于 **不使用额外的字符串或数组**，而是直接通过位运算读取指定位置的比特。  
Python 的 `int.bit_length()` 能快速得到二进制位数，避免了手动循环除以 2 的过程，使代码更简洁。  
在实际面试或竞赛中，掌握这种「双指针 + 位运算」的思路可以帮助我们在 **O(log n)** 时间、**O(1)** 空间内解决类似的二进制回文或对称性问题。
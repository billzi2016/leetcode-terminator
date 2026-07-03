## 思路分析

要判断一个非负整数 `x` 的二进制表示（不含前导零）是否是回文，核心在于 **逐位比较** 两端的比特。

1. **特殊情况**  
   - `x == 0` 时，二进制为 `"0"`，显然是回文，直接返回 `true`。

2. **获取二进制位数**  
   - `x.bit_length()` 能在 O(1) 时间得到二进制位数（不含前导零），记为 `L`。  
   - 当 `x > 0` 时，最高有效位的下标是 `L‑1`，最低位下标是 `0`。  
   - 对于 `x == 0`，我们已在第一步处理。

3. **双指针比较**  
   - 设左指针 `left = L‑1`（最高位），右指针 `right = 0`（最低位）。  
   - 当 `left > right` 时，取出对应的比特：  
     ```python
     left_bit  = (x >> left) & 1
     right_bit = (x >> right) & 1
     ```
   - 若两位不相等，则二进制不是回文，返回 `false`。  
   - 否则指针向中间收敛：`left -= 1`，`right += 1`。  
   - 循环结束后未发现不相等的情况，说明是回文，返回 `true`。

整个过程只使用位运算，没有把整数转成字符串，满足题目要求。

---

## 代码实现

```python
import sys

def is_binary_palindrome(x: int) -> bool:
    """判断整数 x 的二进制表示（不含前导零）是否为回文"""
    if x == 0:
        # 0 的二进制为 "0"
        return True

    # 二进制位数（最高位下标 + 1）
    L = x.bit_length()          # 等价于 floor(log2(x)) + 1
    left = L - 1                 # 最高位下标
    right = 0                    # 最低位下标

    while left > right:
        left_bit = (x >> left) & 1
        right_bit = (x >> right) & 1
        if left_bit != right_bit:
            return False
        left -= 1
        right += 1

    return True


def main() -> None:
    data = sys.stdin.read().strip()
    if not data:
        return
    x = int(data)
    ans = is_binary_palindrome(x)
    # 按题目要求输出小写 true/false
    print("true" if ans else "false")


if __name__ == "__main__":
    main()
```

---

## 复杂度分析

- **时间复杂度**：`O(L)`，其中 `L = x.bit_length()`，即二进制位数，最多为 31（因为 `x ≤ 2³¹‑1`），等价于 `O(log x)`。
- **空间复杂度**：`O(1)`，只使用了若干整数变量。

---

## 心得

1. **位长度的获取**  
   - 使用 `int.bit_length()` 是最简洁且符合“不要转成字符串”要求的方式，内部实现本质上是位运算/数值计算。

2. **双指针思路的迁移**  
   - 回文判断在字符串中常用双指针，同理在二进制位上也完全适用，只是把字符比较换成位比较。

3. **边界处理**  
   - `0` 是唯一的“全 0”情况，需要单独处理，否则 `bit_length()` 会返回 `0`，导致左指针为 `-1`，循环逻辑出错。

4. **提前结束**  
   - 与字符回文一样，一旦发现不匹配即可立刻返回 `false`，避免不必要的遍历，提升常数因子。

通过上述思路即可在 O(log x) 时间、O(1) 空间内完成二进制回文判断，代码简洁易懂且符合题目限制。
## 题目描述  

给定一个整数数组 `nums` 和一个整数 `target`，返回两个数的下标，使得它们的和等于 `target`。  
可以假设每个输入恰好只有一个解，并且同一个元素不能被使用两次。  
答案的下标顺序可以任意。

## 示例  

**示例 1：**
``` 
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
```

**示例 2：**
``` 
Input: nums = [3,2,4], target = 6
Output: [1,2]
```

**示例 3：**
``` 
Input: nums = [3,3], target = 6
Output: [0,1]
```

## 约束条件  

- `2 <= nums.length <= 10^4`  
- `-10^9 <= nums[i] <= 10^9`  
- `-10^9 <= target <= 10^9`  
- `Only one valid answer exists.`   (仅存在唯一有效答案)
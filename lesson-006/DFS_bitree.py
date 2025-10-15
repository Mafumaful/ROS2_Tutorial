from typing import Optional, List
from collections import deque

# 构建二叉树

class TreeNode:
    def __init__(self, val=0, left: Optional["TreeNode"]=None, right: Optional["TreeNode"]=None):
        self.val = val
        self.left = left
        self.right = right

    def printval(self):
        print(self.val)

def build_tree(level: List[Optional[int]]) -> Optional[TreeNode]:
    """
    由层序数组构建二叉树。数组元素为 int 或 None。
    例如：[1,2,3,None,4] 表示：
            1
           / \
          2   3
           \
            4
    """
    if not level:
        return None
    nodes = [None if v is None else TreeNode(v) for v in level]
    n = len(nodes)
    for i in range(n):
        if nodes[i] is None:
            continue
        li, ri = 2*i + 1, 2*i + 2
        if li < n:
            nodes[i].left = nodes[li]
        if ri < n:
            nodes[i].right = nodes[ri]
    return nodes[0]

def level_order(root: Optional[TreeNode]) -> List[Optional[int]]:
    """
    将二叉树序列化为层序数组（尾部多余的 None 会被去掉），便于断言。
    """
    if not root:
        return []
    q = deque([root])
    ans: List[Optional[int]] = []
    while q:
        node = q.popleft()
        if node is None:
            ans.append(None)
            continue
        ans.append(node.val)
        q.append(node.left)
        q.append(node.right)
    while ans and ans[-1] is None:  # 去掉尾部多余 None
        ans.pop()
    return ans

class Solution:
    def sufficientSubset(self, root: Optional[TreeNode], limit: int) -> Optional[TreeNode]:
        def dfs(node:Optional[TreeNode], pre_sum: int) -> Optional[TreeNode]:
            if not node:
                return None
            cur = pre_sum + node.val
            # 叶子结点直接判断
            if node.left is None and node.right is None:
                return node if cur >=limit else None
            # 内部节点处理
            node.left = dfs(node.left, cur)
            node.right = dfs(node.right, cur)
            if node.left is None and node.right is None:
                return None
            return node
        return dfs(root, 0)

# ---------- 测试集 ----------
def run_tests():
    sol = Solution()

    # 1. 题面示例
    root = build_tree([1,2,3,4,-99,-99,7,8,9,-99,-99,12,13,-99,14])
    ss = level_order(sol.sufficientSubset(root, 10))
    assert level_order(sol.sufficientSubset(root, 10)) == \
           [1,2,3,4,None,None,7,8,9,None,None,None,None,None,14]

    # 2. 题面示例 2
    root = build_tree([5,-6,6])
    assert level_order(sol.sufficientSubset(root, -1)) == [5, None, 6]

    # 3. 整棵树被删空
    root = build_tree([1, -2, -3])
    assert level_order(sol.sufficientSubset(root, 5)) == []

    # 4. 单节点保留
    root = build_tree([3])
    assert level_order(sol.sufficientSubset(root, 3)) == [3]

    # 5. 单节点删除
    root = build_tree([2])
    assert level_order(sol.sufficientSubset(root, 3)) == []

    # 6. 左链
    root = build_tree([1,2,None,3,None,4,None])
    assert level_order(sol.sufficientSubset(root, 7)) == [1,2,None,3,None,4]

    # 7. 含负数与剪空子树
    root = build_tree([1,-1,2,-2,None,-3,4])
    assert level_order(sol.sufficientSubset(root, 6)) == [1,None,2,None,4]

    # 8. 大 limit
    root = build_tree([10,5,5,1,1,1,1])
    assert level_order(sol.sufficientSubset(root, 100)) == []

    print("All test cases passed ✅")

def main():
    run_tests()
    # 额外演示
    arr = [1,2,3,4,-99,-99,7,8,9,-99,-99,12,13,-99,14]
    root = build_tree(arr)
    sol = Solution()
    pruned = sol.sufficientSubset(root, 10)
    print("Demo input:", arr, "limit=10")
    print("Pruned level order:", level_order(pruned))

if __name__ == "__main__":
    main()
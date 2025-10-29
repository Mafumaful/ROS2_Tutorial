"""
第1课: A*路径规划算法

这个文件实现了经典的A*算法，用于在网格地图上寻找最优路径。

核心概念:
1. f(n) = g(n) + h(n)
   - g(n): 从起点到当前节点的实际代价
   - h(n): 从当前节点到终点的启发式估计代价
   - f(n): 总评估代价

2. Open List: 待扩展的节点列表（优先队列）
3. Closed Set: 已访问过的节点集合
4. 启发式函数: 用欧几里得距离或曼哈顿距离估计剩余代价

作者: Path Planning Course Team
日期: 2024
"""

import heapq
import math
import numpy as np
from typing import List, Tuple, Optional, Set, Dict
from dataclasses import dataclass, field


@dataclass(order=True)
class AStarNode:
    """
    A*算法的节点类
    
    使用@dataclass装饰器简化代码，自动生成__init__, __repr__等方法
    order=True 使得节点可以按f值排序（用于优先队列）
    
    属性:
        f: 总评估代价 f(n) = g(n) + h(n)
        pos: 节点位置坐标 (x, y)
        g: 从起点到当前节点的实际代价
        h: 从当前节点到终点的启发式估计代价
        parent: 父节点（用于路径回溯）
    """
    f: float  # 排序字段，必须放在第一位
    pos: Tuple[int, int] = field(compare=False)  # 不参与比较
    g: float = field(compare=False)
    h: float = field(compare=False)
    parent: Optional['AStarNode'] = field(default=None, compare=False)


class AStar:
    """
    A*路径规划算法类
    
    这个类实现了完整的A*算法，包括:
    - 启发式函数计算
    - 邻居节点扩展
    - 路径搜索主循环
    - 路径回溯
    
    使用方法:
        >>> planner = AStar(grid, start=(0,0), goal=(9,9))
        >>> path = planner.plan()
        >>> if path:
        ...     print(f"找到路径！长度: {len(path)}")
    """
    
    def __init__(
        self, 
        grid: np.ndarray, 
        start: Tuple[int, int], 
        goal: Tuple[int, int],
        heuristic_weight: float = 1.0
    ):
        """
        初始化A*规划器
        
        Args:
            grid: 2D numpy数组，0表示空闲，1表示障碍物
            start: 起点坐标 (x, y)
            goal: 终点坐标 (x, y)
            heuristic_weight: 启发式函数权重，>1会加快搜索但可能不是最优
        """
        self.grid = grid
        self.start = start
        self.goal = goal
        self.heuristic_weight = heuristic_weight
        
        # 获取地图尺寸
        self.height, self.width = grid.shape
        
        # 统计信息
        self.nodes_expanded = 0  # 扩展的节点数
        self.nodes_visited = 0   # 访问的节点数
        
        print(f"[A*] 初始化完成")
        print(f"  地图大小: {self.width} × {self.height}")
        print(f"  起点: {start}, 终点: {goal}")
        print(f"  启发式权重: {heuristic_weight}")
    
    def heuristic(self, pos: Tuple[int, int]) -> float:
        """
        计算启发式代价 h(n)
        
        使用欧几里得距离（直线距离）作为启发式函数。
        这是一个"可采纳的"启发式函数，因为它永不高估实际代价。
        
        Args:
            pos: 当前位置 (x, y)
        
        Returns:
            从当前位置到目标的估计距离
        
        注意:
            - 欧几里得距离适用于可以斜向移动的情况
            - 如果只能上下左右移动，曼哈顿距离更合适
            - 可采纳性保证找到最优路径
        """
        dx = pos[0] - self.goal[0]
        dy = pos[1] - self.goal[1]
        return math.sqrt(dx*dx + dy*dy) * self.heuristic_weight
    
    def is_valid(self, pos: Tuple[int, int]) -> bool:
        """
        检查位置是否有效
        
        一个有效的位置需要满足:
        1. 在地图范围内
        2. 不是障碍物
        
        Args:
            pos: 要检查的位置 (x, y)
        
        Returns:
            True if 位置有效, False otherwise
        """
        x, y = pos
        
        # 边界检查
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # 障碍物检查
        if self.grid[y, x] == 1:
            return False
        
        return True
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[Tuple[int, int], float]]:
        """
        获取当前位置的所有有效邻居节点
        
        支持8连通移动:
        ↖ ↑ ↗
        ← ● →
        ↙ ↓ ↘
        
        Args:
            pos: 当前位置 (x, y)
        
        Returns:
            邻居列表，每个元素是 ((nx, ny), cost) 的元组
            - (nx, ny): 邻居坐标
            - cost: 移动到该邻居的代价
        
        注意:
            - 直线移动代价为1.0
            - 对角移动代价为√2 ≈ 1.414（更长的距离）
        """
        x, y = pos
        neighbors = []
        
        # 8个方向的增量: (dx, dy)
        # 顺序: 上、右、下、左、右上、右下、左下、左上
        directions = [
            (-1, -1), (0, -1), (1, -1),  # 上排
            (-1,  0),          (1,  0),  # 中排（跳过中心点）
            (-1,  1), (0,  1), (1,  1),  # 下排
        ]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # 检查新位置是否有效
            if self.is_valid((nx, ny)):
                # 计算移动代价
                # 直线移动: cost = 1.0
                # 对角移动: cost = √2
                cost = math.sqrt(dx*dx + dy*dy)
                neighbors.append(((nx, ny), cost))
        
        return neighbors
    
    def reconstruct_path(self, node: AStarNode) -> List[Tuple[int, int]]:
        """
        从终点节点回溯到起点，重建完整路径
        
        通过parent指针向上回溯，直到到达起点（parent为None）
        
        Args:
            node: 终点节点
        
        Returns:
            从起点到终点的路径，是一个坐标列表 [(x1,y1), (x2,y2), ...]
        """
        path = []
        current = node
        
        # 向上回溯
        while current is not None:
            path.append(current.pos)
            current = current.parent
        
        # 反转路径（因为是从终点回溯到起点的）
        path.reverse()
        
        return path
    
    def plan(self, verbose: bool = True) -> Optional[List[Tuple[int, int]]]:
        """
        执行A*路径规划
        
        这是算法的主要函数，实现了A*搜索的核心逻辑:
        1. 初始化Open List和Closed Set
        2. 循环取出f值最小的节点
        3. 检查是否到达目标
        4. 扩展邻居节点
        5. 更新节点代价
        
        Args:
            verbose: 是否打印详细信息
        
        Returns:
            如果找到路径，返回坐标列表 [(x1,y1), (x2,y2), ...]
            如果没找到路径，返回 None
        
        算法复杂度:
            时间: O(b^d) 其中b是分支因子，d是深度
            空间: O(b^d)
        """
        if verbose:
            print("\n[A*] 开始路径规划...")
        
        # 重置统计信息
        self.nodes_expanded = 0
        self.nodes_visited = 0
        
        # ===== 1. 初始化 =====
        # Open List: 优先队列，存储待扩展的节点
        # Python的heapq是最小堆，会按照节点的f值排序
        open_list = []
        
        # 用于打破f值相同时的平局（FIFO顺序）
        counter = 0
        
        # Closed Set: 已访问节点的集合
        # 使用set数据结构，查找速度O(1)
        closed_set: Set[Tuple[int, int]] = set()
        
        # g_score: 存储到达每个节点的最佳g值
        # 用于判断是否找到了更好的路径
        g_score: Dict[Tuple[int, int], float] = {}
        
        # 创建起点节点
        start_node = AStarNode(
            pos=self.start,
            g=0,
            h=self.heuristic(self.start),
            f=self.heuristic(self.start),  # f = g + h = 0 + h
            parent=None
        )
        
        # 将起点加入Open List
        # heapq需要的格式: (priority, counter, item)
        heapq.heappush(open_list, (start_node.f, counter, start_node))
        counter += 1
        g_score[self.start] = 0
        
        if verbose:
            print(f"  起点 f={start_node.f:.2f} (g=0, h={start_node.h:.2f})")
        
        # ===== 2. 主搜索循环 =====
        while open_list:
            # a. 取出f值最小的节点
            _, _, current = heapq.heappop(open_list)
            current_pos = current.pos
            self.nodes_visited += 1
            
            # b. 检查是否到达目标
            if current_pos == self.goal:
                path = self.reconstruct_path(current)
                
                if verbose:
                    print(f"\n[A*] ✓ 找到路径！")
                    print(f"  路径长度: {len(path)}")
                    print(f"  路径代价: {current.g:.2f}")
                    print(f"  扩展节点: {self.nodes_expanded}")
                    print(f"  访问节点: {self.nodes_visited}")
                
                return path
            
            # c. 如果已经访问过，跳过
            if current_pos in closed_set:
                continue
            
            # d. 标记为已访问
            closed_set.add(current_pos)
            self.nodes_expanded += 1
            
            # e. 扩展邻居节点
            for neighbor_pos, move_cost in self.get_neighbors(current_pos):
                # 如果邻居已经访问过，跳过
                if neighbor_pos in closed_set:
                    continue
                
                # 计算到达邻居的新g值
                tentative_g = current.g + move_cost
                
                # 如果找到了更好的路径（或第一次访问这个节点）
                if neighbor_pos not in g_score or tentative_g < g_score[neighbor_pos]:
                    # 更新最佳g值
                    g_score[neighbor_pos] = tentative_g
                    
                    # 计算启发式代价
                    h = self.heuristic(neighbor_pos)
                    f = tentative_g + h
                    
                    # 创建新节点
                    neighbor_node = AStarNode(
                        pos=neighbor_pos,
                        g=tentative_g,
                        h=h,
                        f=f,
                        parent=current
                    )
                    
                    # 加入Open List
                    heapq.heappush(open_list, (f, counter, neighbor_node))
                    counter += 1
        
        # ===== 3. 搜索失败 =====
        if verbose:
            print(f"\n[A*] ✗ 未找到路径")
            print(f"  扩展节点: {self.nodes_expanded}")
            print(f"  访问节点: {self.nodes_visited}")
        
        return None


# ===== 辅助函数 =====

def create_grid_map(
    width: int, 
    height: int, 
    obstacles: List[Tuple[int, int, int, int]] = None
) -> np.ndarray:
    """
    创建网格地图
    
    Args:
        width: 地图宽度
        height: 地图高度
        obstacles: 障碍物列表，每个障碍物是 (x_min, y_min, x_max, y_max)
    
    Returns:
        2D numpy数组，0表示空闲，1表示障碍物
    
    示例:
        >>> grid = create_grid_map(10, 10, obstacles=[(3, 3, 5, 5)])
        >>> print(grid[3:6, 3:6])  # 打印障碍物区域
    """
    grid = np.zeros((height, width), dtype=np.uint8)
    
    if obstacles:
        for x_min, y_min, x_max, y_max in obstacles:
            # 确保坐标在范围内
            x_min = max(0, min(x_min, width-1))
            y_min = max(0, min(y_min, height-1))
            x_max = max(0, min(x_max, width-1))
            y_max = max(0, min(y_max, height-1))
            
            # 标记障碍物
            grid[y_min:y_max+1, x_min:x_max+1] = 1
    
    return grid


# ===== 测试代码 =====

if __name__ == "__main__":
    print("="*50)
    print("A*算法测试")
    print("="*50)
    
    # 创建10x10的测试地图
    # 添加一个L形障碍物
    obstacles = [(3, 3, 5, 5)]
    grid = create_grid_map(10, 10, obstacles)
    
    print("\n地图:")
    print("  □ = 空闲, ■ = 障碍物, S = 起点, G = 终点")
    print()
    
    # 打印地图
    start = (1, 1)
    goal = (8, 8)
    
    for y in range(10):
        for x in range(10):
            if (x, y) == start:
                print("S ", end="")
            elif (x, y) == goal:
                print("G ", end="")
            elif grid[y, x] == 1:
                print("■ ", end="")
            else:
                print("□ ", end="")
        print()
    
    # 执行A*规划
    planner = AStar(grid, start, goal)
    path = planner.plan()
    
    if path:
        print("\n规划的路径:")
        print("  ● = 路径")
        print()
        
        # 打印带路径的地图
        path_set = set(path)
        for y in range(10):
            for x in range(10):
                if (x, y) == start:
                    print("S ", end="")
                elif (x, y) == goal:
                    print("G ", end="")
                elif (x, y) in path_set:
                    print("● ", end="")
                elif grid[y, x] == 1:
                    print("■ ", end="")
                else:
                    print("□ ", end="")
            print()
        
        print(f"\n路径坐标: {path[:5]}...{path[-3:]}")
    else:
        print("\n无法找到路径！")
    
    print("\n" + "="*50)


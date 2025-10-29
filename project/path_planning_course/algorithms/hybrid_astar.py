"""
第2课: Hybrid A*路径规划算法

Hybrid A*是A*算法的扩展，考虑车辆运动学约束。

关键区别:
1. 状态空间: (x, y, θ) vs 传统A*的(x, y)
2. 扩展方式: 运动原语 vs 8方向移动
3. 路径特点: 可直接执行的平滑路径 vs 锯齿状路径

运动原语 (Motion Primitives):
- 预定义的一组控制输入
- 模拟车辆真实运动
- 考虑转弯半径等约束

作者: Path Planning Course Team
"""

import numpy as np
import math
import heapq
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass, field
import sys
sys.path.append('..')
from vehicle.bicycle_model import BicycleModel


@dataclass
class MotionPrimitive:
    """
    运动原语类
    
    定义一个基本的运动指令：给定转向角，行驶一定距离
    
    属性:
        steer: 转向角 (rad)
        distance: 行驶距离 (m)
        direction: 方向 (+1前进, -1后退)
    """
    steer: float
    distance: float
    direction: int = 1
    
    def __str__(self) -> str:
        dir_str = "前进" if self.direction > 0 else "后退"
        return f"MP(δ={np.rad2deg(self.steer):.1f}°, d={self.distance:.1f}m, {dir_str})"


@dataclass(order=True)
class HybridAStarNode:
    """
    Hybrid A*节点
    
    与传统A*的区别:
    - 状态包含角度: (x, y, θ) vs (x, y)
    - 需要离散化索引以避免重复搜索
    - 存储轨迹而非单个位置
    """
    f: float
    state: Tuple[float, float, float, float] = field(compare=False)  # (x, y, θ, v)
    g: float = field(compare=False)
    h: float = field(compare=False)
    parent: Optional['HybridAStarNode'] = field(default=None, compare=False)
    primitive: Optional[MotionPrimitive] = field(default=None, compare=False)
    trajectory: Optional[np.ndarray] = field(default=None, compare=False)


class HybridAStar:
    """
    Hybrid A*路径规划器
    
    核心改进:
    1. 3D状态空间 (x, y, θ)
    2. 运动原语扩展
    3. 车辆运动学约束
    4. 连续状态 + 离散索引
    
    使用方法:
        >>> vehicle = BicycleModel(L=2.7)
        >>> planner = HybridAStar(vehicle, obstacles)
        >>> path = planner.plan(start, goal)
    """
    
    def __init__(
        self,
        vehicle_model: BicycleModel,
        grid: np.ndarray,
        xy_resolution: float = 0.5,
        yaw_resolution: float = np.deg2rad(15),
        use_reverse: bool = False
    ):
        """
        初始化Hybrid A*规划器
        
        Args:
            vehicle_model: 车辆运动学模型
            grid: 2D占据网格，0=空闲，1=障碍物
            xy_resolution: 位置离散化分辨率 (m)
            yaw_resolution: 角度离散化分辨率 (rad)
            use_reverse: 是否使用后退运动原语
        """
        self.vehicle = vehicle_model
        self.grid = grid
        self.xy_res = xy_resolution
        self.yaw_res = yaw_resolution
        self.use_reverse = use_reverse
        
        self.height, self.width = grid.shape
        self.n_yaw = int(2 * np.pi / yaw_resolution)  # 角度bins数量
        
        # 创建运动原语集
        self.motion_primitives = self._create_motion_primitives()
        
        # 统计信息
        self.nodes_expanded = 0
        self.nodes_visited = 0
        
        print(f"[Hybrid A*] 初始化完成")
        print(f"  地图大小: {self.width} × {self.height}")
        print(f"  位置分辨率: {xy_resolution} m")
        print(f"  角度分辨率: {np.rad2deg(yaw_resolution):.1f}° ({self.n_yaw}个bins)")
        print(f"  运动原语数量: {len(self.motion_primitives)}")
        if use_reverse:
            print(f"  支持后退运动")
    
    def _create_motion_primitives(self) -> List[MotionPrimitive]:
        """
        创建运动原语集
        
        Returns:
            运动原语列表
        
        设计原则:
        - 覆盖不同转向角（左转、直行、右转）
        - 步长适中（通常0.5-2.0m）
        - 可选后退原语（泊车场景）
        """
        primitives = []
        
        # 转向角候选（相对于最大转向角）
        steer_angles = [
            -self.vehicle.delta_max,          # 最大左转
            -self.vehicle.delta_max * 0.5,    # 小幅左转
            0.0,                              # 直行
            self.vehicle.delta_max * 0.5,     # 小幅右转
            self.vehicle.delta_max,           # 最大右转
        ]
        
        # 行驶距离
        distance = 1.0  # 1米
        
        # 前进原语
        for steer in steer_angles:
            primitives.append(MotionPrimitive(steer, distance, direction=1))
        
        # 后退原语（可选）
        if self.use_reverse:
            for steer in steer_angles:
                primitives.append(MotionPrimitive(steer, distance, direction=-1))
        
        return primitives
    
    def calc_index(self, state: Tuple[float, float, float, float]) -> Tuple[int, int, int]:
        """
        计算状态的离散索引
        
        Args:
            state: (x, y, θ, v)
        
        Returns:
            (ix, iy, iyaw): 离散索引
        
        目的:
            避免重复搜索相近的状态
        
        示例:
            state1 = (2.3, 1.8, 32°) → index = (5, 4, 2)
            state2 = (2.4, 1.9, 31°) → index = (5, 4, 2)  # 相同索引
        """
        x, y, theta, v = state
        
        ix = round(x / self.xy_res)
        iy = round(y / self.xy_res)
        iyaw = round(theta / self.yaw_res) % self.n_yaw
        
        return (ix, iy, iyaw)
    
    def heuristic(self, state: Tuple[float, float, float, float]) -> float:
        """
        启发式函数
        
        使用欧几里得距离 + 角度差异惩罚
        
        Args:
            state: (x, y, θ, v)
        
        Returns:
            估计代价
        """
        x, y, theta, v = state
        gx, gy, gtheta, gv = self.goal
        
        # 位置距离
        pos_dist = math.sqrt((x - gx)**2 + (y - gy)**2)
        
        # 角度差异（归一化到[0, π]）
        angle_diff = abs(self.normalize_angle(theta - gtheta))
        
        # 组合代价
        return pos_dist + 0.5 * angle_diff
    
    def normalize_angle(self, angle: float) -> float:
        """归一化角度到[-π, π]"""
        return np.arctan2(np.sin(angle), np.cos(angle))
    
    def is_collision(self, state: Tuple[float, float, float, float]) -> bool:
        """
        碰撞检测
        
        简化版本：只检查车辆中心点
        实际应用中应检查车辆footprint
        
        Args:
            state: (x, y, θ, v)
        
        Returns:
            True if 碰撞, False otherwise
        """
        x, y, theta, v = state
        
        # 转换到网格坐标
        ix = int(x)
        iy = int(y)
        
        # 边界检查
        if not (0 <= ix < self.width and 0 <= iy < self.height):
            return True
        
        # 障碍物检查
        if self.grid[iy, ix] == 1:
            return True
        
        return False
    
    def simulate_primitive(
        self,
        state: np.ndarray,
        primitive: MotionPrimitive,
        num_steps: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        模拟运动原语的执行
        
        Args:
            state: 初始状态 [x, y, θ, v]
            primitive: 运动原语
            num_steps: 离散化步数
        
        Returns:
            (final_state, trajectory):
                - final_state: 最终状态
                - trajectory: 轨迹，形状(num_steps+1, 4)
        """
        dt = primitive.distance / (num_steps * 2.0)  # 时间步长
        
        # 设置速度（前进或后退）
        target_v = 2.0 * primitive.direction
        
        trajectory = [state.copy()]
        current_state = state.copy()
        current_state[3] = target_v  # 设置速度
        
        for _ in range(num_steps):
            # 控制输入: [转向角, 加速度]
            control = np.array([primitive.steer, 0.0])
            
            # 仿真一步
            current_state = self.vehicle.step(current_state, control, dt)
            trajectory.append(current_state.copy())
        
        return current_state, np.array(trajectory)
    
    def expand_node(self, node: HybridAStarNode) -> List[HybridAStarNode]:
        """
        扩展节点，生成后继节点
        
        Args:
            node: 当前节点
        
        Returns:
            后继节点列表
        """
        successors = []
        current_state = np.array(node.state)
        
        for primitive in self.motion_primitives:
            # 模拟运动原语
            new_state, trajectory = self.simulate_primitive(current_state, primitive)
            
            # 碰撞检测
            collision = False
            for traj_state in trajectory:
                if self.is_collision(tuple(traj_state)):
                    collision = True
                    break
            
            if collision:
                continue
            
            # 计算代价
            # 使用轨迹长度作为代价
            step_cost = primitive.distance
            
            # 后退代价更高（鼓励前进）
            if primitive.direction < 0:
                step_cost *= 1.5
            
            # 创建后继节点
            new_g = node.g + step_cost
            new_h = self.heuristic(tuple(new_state))
            new_f = new_g + new_h
            
            successor = HybridAStarNode(
                f=new_f,
                state=tuple(new_state),
                g=new_g,
                h=new_h,
                parent=node,
                primitive=primitive,
                trajectory=trajectory
            )
            
            successors.append(successor)
        
        return successors
    
    def near_goal(
        self,
        state: Tuple[float, float, float, float],
        pos_tol: float = 1.0,
        angle_tol: float = np.deg2rad(15)
    ) -> bool:
        """
        判断是否接近目标
        
        Args:
            state: 当前状态
            pos_tol: 位置容差 (m)
            angle_tol: 角度容差 (rad)
        
        Returns:
            True if 接近目标
        """
        x, y, theta, v = state
        gx, gy, gtheta, gv = self.goal
        
        pos_ok = math.sqrt((x - gx)**2 + (y - gy)**2) < pos_tol
        angle_ok = abs(self.normalize_angle(theta - gtheta)) < angle_tol
        
        return pos_ok and angle_ok
    
    def extract_path(self, node: HybridAStarNode) -> List[np.ndarray]:
        """
        提取路径（包含完整轨迹）
        
        Args:
            node: 终点节点
        
        Returns:
            路径列表，每个元素是一段轨迹
        """
        path_segments = []
        current = node
        
        while current.parent is not None:
            if current.trajectory is not None:
                # 反转轨迹（因为是从终点回溯）
                path_segments.append(current.trajectory[::-1])
            current = current.parent
        
        # 反转整个路径
        path_segments.reverse()
        
        # 合并所有轨迹段
        if path_segments:
            full_path = np.vstack(path_segments)
        else:
            full_path = np.array([node.state])
        
        return full_path
    
    def plan(
        self,
        start: Tuple[float, float, float, float],
        goal: Tuple[float, float, float, float],
        verbose: bool = True
    ) -> Optional[np.ndarray]:
        """
        Hybrid A*路径规划主函数
        
        Args:
            start: 起点状态 (x, y, θ, v)
            goal: 终点状态 (x, y, θ, v)
            verbose: 是否打印详细信息
        
        Returns:
            路径数组 (N, 4) 或 None
        """
        self.goal = goal
        self.nodes_expanded = 0
        self.nodes_visited = 0
        
        if verbose:
            print(f"\n[Hybrid A*] 开始规划...")
            print(f"  起点: ({start[0]:.1f}, {start[1]:.1f}, {np.rad2deg(start[2]):.1f}°)")
            print(f"  终点: ({goal[0]:.1f}, {goal[1]:.1f}, {np.rad2deg(goal[2]):.1f}°)")
        
        # 检查起点和终点
        if self.is_collision(start):
            print("[Hybrid A*] 错误: 起点在障碍物中！")
            return None
        if self.is_collision(goal):
            print("[Hybrid A*] 错误: 终点在障碍物中！")
            return None
        
        # 初始化
        open_list = []
        closed_dict: Dict[Tuple[int, int, int], HybridAStarNode] = {}
        counter = 0
        
        # 起点节点
        start_node = HybridAStarNode(
            f=self.heuristic(start),
            state=start,
            g=0,
            h=self.heuristic(start),
            parent=None
        )
        
        heapq.heappush(open_list, (start_node.f, counter, start_node))
        counter += 1
        
        # 主搜索循环
        while open_list:
            _, _, current = heapq.heappop(open_list)
            self.nodes_visited += 1
            
            # 到达目标
            if self.near_goal(current.state):
                path = self.extract_path(current)
                
                if verbose:
                    print(f"\n[Hybrid A*] ✓ 找到路径！")
                    print(f"  路径点数: {len(path)}")
                    print(f"  路径代价: {current.g:.2f}")
                    print(f"  扩展节点: {self.nodes_expanded}")
                    print(f"  访问节点: {self.nodes_visited}")
                
                return path
            
            # 计算索引
            index = self.calc_index(current.state)
            
            # 检查是否已访问过
            if index in closed_dict:
                if current.g >= closed_dict[index].g:
                    continue
            
            # 加入closed set
            closed_dict[index] = current
            self.nodes_expanded += 1
            
            # 打印进度
            if verbose and self.nodes_expanded % 50 == 0:
                print(f"  已扩展 {self.nodes_expanded} 个节点...", end='\r')
            
            # 扩展后继节点
            successors = self.expand_node(current)
            
            for succ in successors:
                succ_index = self.calc_index(succ.state)
                
                # 检查是否找到更好的路径
                if succ_index not in closed_dict or succ.g < closed_dict[succ_index].g:
                    heapq.heappush(open_list, (succ.f, counter, succ))
                    counter += 1
        
        # 未找到路径
        if verbose:
            print(f"\n[Hybrid A*] ✗ 未找到路径")
            print(f"  扩展节点: {self.nodes_expanded}")
            print(f"  访问节点: {self.nodes_visited}")
        
        return None


# ===== 测试代码 =====

if __name__ == "__main__":
    print("="*60)
    print("Hybrid A*算法测试")
    print("="*60)
    
    # 创建车辆模型
    vehicle = BicycleModel(L=2.7)
    
    # 创建简单地图
    grid = np.zeros((20, 20))
    # 添加障碍物
    grid[8:12, 8:12] = 1
    
    # 创建规划器
    planner = HybridAStar(vehicle, grid, xy_resolution=1.0, yaw_resolution=np.deg2rad(30))
    
    # 定义起点和终点
    start = (2.0, 2.0, 0.0, 0.0)  # (x, y, θ, v)
    goal = (18.0, 18.0, np.pi/4, 0.0)
    
    # 规划
    path = planner.plan(start, goal)
    
    if path is not None:
        print(f"\n成功规划路径！")
        print(f"路径前5个点:")
        for i in range(min(5, len(path))):
            x, y, theta, v = path[i]
            print(f"  {i}: ({x:.2f}, {y:.2f}, {np.rad2deg(theta):.1f}°)")
        
        # 简单可视化
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # 绘制网格
        ax.imshow(grid, origin='lower', cmap='binary', alpha=0.3)
        
        # 绘制路径
        ax.plot(path[:, 0], path[:, 1], 'b-', linewidth=2, label='Hybrid A*路径')
        ax.scatter(start[0], start[1], c='green', s=200, marker='o', label='起点', zorder=5)
        ax.scatter(goal[0], goal[1], c='red', s=200, marker='*', label='终点', zorder=5)
        
        # 绘制车辆姿态
        step = len(path) // 10
        for i in range(0, len(path), step):
            x, y, theta, v = path[i]
            dx = np.cos(theta) * 1.0
            dy = np.sin(theta) * 1.0
            ax.arrow(x, y, dx, dy, head_width=0.5, head_length=0.3, fc='red', ec='red', alpha=0.6)
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_title('Hybrid A* 路径规划结果')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        plt.savefig('hybrid_astar_test.png', dpi=150, bbox_inches='tight')
        print("\n已保存图片: hybrid_astar_test.png")
        plt.show()
    
    print("\n" + "="*60)


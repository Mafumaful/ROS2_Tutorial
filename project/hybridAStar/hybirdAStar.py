# Hybrid A*路径规划算法完整实现 - 自动泊车系统智能路径规划
import numpy as np
import heapq
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, PillowWriter
from collections import defaultdict
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import math
import random

@dataclass
class VehicleState:
    """
    车辆状态数据结构
    
    包含车辆的位置、姿态和运动状态
    """
    x: float          # X坐标 (米)
    y: float          # Y坐标 (米)
    theta: float      # 航向角 (弧度)
    gear: int         # 挡位: 1(前进), -1(后退)
    cost: float       # 到达此状态的代价
    parent: Optional['VehicleState'] = None  # 父状态
    action: Optional[str] = None  # 到达此状态的动作

@dataclass
class VehicleParams:
    """
    车辆参数配置
    
    定义车辆的物理约束和运动特性
    """
    wheelbase: float = 2.8        # 轴距 (米)
    max_steer: float = 0.6        # 最大转向角 (弧度)
    min_radius: float = 5.0       # 最小转弯半径 (米)
    step_size: float = 0.5        # 步长 (米)
    width: float = 1.8             # 车宽 (米)
    length: float = 4.5           # 车长 (米)

class HybridAStar:
    """
    Hybrid A*路径规划算法 - 用于自动泊车系统的智能路径规划
    
    功能说明：
    1. 结合A*搜索的全局最优性和连续空间路径的平滑性
    2. 考虑车辆的运动学约束
    3. 生成符合车辆物理特性的可行路径
    4. 优化路径的平滑性和效率
    """
    
    def __init__(self, grid_map, vehicle_params: VehicleParams):
        """
        初始化Hybrid A*算法
        
        Args:
            grid_map: 栅格地图，0表示可通行，1表示障碍物
            vehicle_params: 车辆参数
        """
        self.grid_map = grid_map
        self.vehicle_params = vehicle_params
        self.height, self.width = grid_map.shape
        
        # 搜索方向：直行、左转、右转
        self.directions = [0, vehicle_params.max_steer, -vehicle_params.max_steer]
        
        # 代价权重
        self.weights = {
            'distance': 1.0,      # 距离代价
            'curvature': 2.0,     # 曲率代价
            'gear_change': 5.0,   # 换挡代价
            'direction_change': 3.0,  # 方向切换代价
            'obstacle': 10.0      # 障碍物代价
        }
    
    def heuristic(self, state: VehicleState, goal: Tuple[float, float, float]) -> float:
        """
        启发式函数：计算从当前状态到目标的估计代价
        
        Args:
            state: 当前车辆状态
            goal: 目标状态 (x, y, theta)
            
        Returns:
            heuristic_cost: 启发式代价
        """
        # 欧几里得距离
        dx = state.x - goal[0]
        dy = state.y - goal[1]
        distance_cost = math.sqrt(dx*dx + dy*dy)
        
        # 角度差代价
        angle_diff = abs(state.theta - goal[2])
        angle_cost = min(angle_diff, 2*math.pi - angle_diff)
        
        return distance_cost + 0.5 * angle_cost
    
    def get_neighbors(self, state: VehicleState) -> List[Tuple[VehicleState, float]]:
        """
        获取当前状态的邻居状态
        
        Args:
            state: 当前车辆状态
            
        Returns:
            neighbors: 邻居状态和转移代价的列表
        """
        neighbors = []
        
        for direction in self.directions:
            # 计算新状态
            new_state = self._apply_motion_model(state, direction)
            
            if new_state is not None and not self._is_collision(new_state):
                # 计算转移代价
                cost = self._calculate_transition_cost(state, new_state)
                neighbors.append((new_state, cost))
        
        return neighbors
    
    def _apply_motion_model(self, state: VehicleState, steer_angle: float) -> Optional[VehicleState]:
        """
        应用运动模型，计算新状态
        
        Args:
            state: 当前状态
            steer_angle: 转向角
            
        Returns:
            new_state: 新状态或None（如果无效）
        """
        # 自行车模型
        x = state.x
        y = state.y
        theta = state.theta
        
        # 计算新位置
        new_x = x + self.vehicle_params.step_size * math.cos(theta)
        new_y = y + self.vehicle_params.step_size * math.sin(theta)
        new_theta = theta + self.vehicle_params.step_size * math.tan(steer_angle) / self.vehicle_params.wheelbase
        
        # 角度归一化
        new_theta = self._normalize_angle(new_theta)
        
        # 检查是否在边界内
        if not self._is_in_bounds(new_x, new_y):
            return None
        
        # 创建新状态
        new_state = VehicleState(
            x=new_x,
            y=new_y,
            theta=new_theta,
            gear=state.gear,
            cost=state.cost,
            parent=state,
            action=self._get_action_name(steer_angle)
        )
        
        return new_state
    
    def _is_collision(self, state: VehicleState) -> bool:
        """
        检查车辆是否与障碍物碰撞
        
        Args:
            state: 车辆状态
            
        Returns:
            is_collision: 是否碰撞
        """
        # 计算车辆四个角点的世界坐标
        corners = self._get_vehicle_corners(state)
        
        # 检查每个角点是否在障碍物内
        for corner in corners:
            grid_x, grid_y = self._world_to_grid(corner[0], corner[1])
            
            if (0 <= grid_x < self.width and 0 <= grid_y < self.height):
                if self.grid_map[grid_y, grid_x] == 1:  # 障碍物
                    return True
        
        return False
    
    def _get_vehicle_corners(self, state: VehicleState) -> List[Tuple[float, float]]:
        """
        计算车辆四个角点的世界坐标
        
        Args:
            state: 车辆状态
            
        Returns:
            corners: 四个角点坐标
        """
        # 车辆中心到角点的相对坐标
        half_length = self.vehicle_params.length / 2
        half_width = self.vehicle_params.width / 2
        
        # 车辆局部坐标系下的角点
        local_corners = [
            (-half_length, -half_width),  # 后左
            (-half_length, half_width),   # 后右
            (half_length, half_width),    # 前右
            (half_length, -half_width)   # 前左
        ]
        
        # 转换到世界坐标系
        world_corners = []
        cos_theta = math.cos(state.theta)
        sin_theta = math.sin(state.theta)
        
        for local_x, local_y in local_corners:
            world_x = state.x + local_x * cos_theta - local_y * sin_theta
            world_y = state.y + local_x * sin_theta + local_y * cos_theta
            world_corners.append((world_x, world_y))
        
        return world_corners
    
    def _calculate_transition_cost(self, from_state: VehicleState, to_state: VehicleState) -> float:
        """
        计算状态转移代价
        
        Args:
            from_state: 起始状态
            to_state: 目标状态
            
        Returns:
            cost: 转移代价
        """
        cost = 0.0
        
        # 距离代价
        distance = math.sqrt((to_state.x - from_state.x)**2 + (to_state.y - from_state.y)**2)
        cost += self.weights['distance'] * distance
        
        # 曲率代价
        curvature = abs(to_state.theta - from_state.theta)
        cost += self.weights['curvature'] * curvature
        
        # 换挡代价
        if from_state.gear != to_state.gear:
            cost += self.weights['gear_change']
        
        # 方向切换代价
        if from_state.action != to_state.action:
            cost += self.weights['direction_change']
        
        # 障碍物代价（距离障碍物的惩罚）
        obstacle_cost = self._get_obstacle_penalty(to_state)
        cost += self.weights['obstacle'] * obstacle_cost
        
        return cost
    
    def _get_obstacle_penalty(self, state: VehicleState) -> float:
        """
        计算障碍物惩罚代价
        
        Args:
            state: 车辆状态
            
        Returns:
            penalty: 障碍物惩罚
        """
        # 计算车辆周围的安全距离
        safety_distance = 1.0  # 安全距离 (米)
        
        # 检查车辆周围的安全区域
        corners = self._get_vehicle_corners(state)
        
        min_distance = float('inf')
        for corner in corners:
            grid_x, grid_y = self._world_to_grid(corner[0], corner[1])
            
            # 检查周围区域
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    check_x = grid_x + dx
                    check_y = grid_y + dy
                    
                    if (0 <= check_x < self.width and 0 <= check_y < self.height):
                        if self.grid_map[check_y, check_x] == 1:
                            distance = math.sqrt(dx*dx + dy*dy)
                            min_distance = min(min_distance, distance)
        
        if min_distance < safety_distance:
            return 1.0 / (min_distance + 0.1)
        
        return 0.0
    
    def search(self, start: Tuple[float, float, float], 
               goal: Tuple[float, float, float]) -> Optional[List[VehicleState]]:
        """
        执行Hybrid A*搜索
        
        Args:
            start: 起始状态 (x, y, theta)
            goal: 目标状态 (x, y, theta)
            
        Returns:
            path: 路径状态列表或None
        """
        # 初始化起始状态
        start_state = VehicleState(
            x=start[0], y=start[1], theta=start[2],
            gear=1, cost=0.0
        )
        
        # 开放列表和关闭列表
        counter = 0  # 用于heap的tie-breaking
        open_list = [(0, counter, start_state)]
        closed_set = set()
        g_score = defaultdict(lambda: float('inf'))
        start_key = self._discretize_state(start_state)
        g_score[start_key] = 0

        max_iterations = 50000  # 最大迭代次数
        iteration = 0

        while open_list and iteration < max_iterations:
            iteration += 1

            # 取出代价最小的状态
            current_f, _, current_state = heapq.heappop(open_list)

            # 检查是否到达目标
            if self._is_goal_reached(current_state, goal):
                print(f"找到路径! 迭代次数: {iteration}")
                return self._reconstruct_path(current_state)

            # 添加到关闭列表
            state_key = self._discretize_state(current_state)
            if state_key in closed_set:
                continue
            closed_set.add(state_key)
            
            # 扩展邻居状态
            neighbors = self.get_neighbors(current_state)

            # 调试输出
            if iteration % 1000 == 0:
                print(f"迭代 {iteration}: 当前位置({current_state.x:.1f}, {current_state.y:.1f}, {current_state.theta:.2f}), "
                      f"邻居数: {len(neighbors)}, Open列表大小: {len(open_list)}")

            for neighbor_state, transition_cost in neighbors:
                neighbor_key = self._discretize_state(neighbor_state)

                if neighbor_key in closed_set:
                    continue

                # 计算新的g分数
                tentative_g = g_score[state_key] + transition_cost

                if tentative_g < g_score[neighbor_key]:
                    neighbor_state.parent = current_state
                    neighbor_state.cost = tentative_g
                    g_score[neighbor_key] = tentative_g

                    # 计算f分数
                    f_score = tentative_g + self.heuristic(neighbor_state, goal)
                    counter += 1
                    heapq.heappush(open_list, (f_score, counter, neighbor_state))

        if iteration >= max_iterations:
            print(f"达到最大迭代次数 {max_iterations}，搜索终止")

        return None  # 未找到路径
    
    def _is_goal_reached(self, state: VehicleState, goal: Tuple[float, float, float]) -> bool:
        """
        检查是否到达目标

        Args:
            state: 当前状态
            goal: 目标状态

        Returns:
            is_reached: 是否到达目标
        """
        # 位置容差
        position_tolerance = 2.0  # 米（增加容差）
        angle_tolerance = 0.5     # 弧度（增加容差）
        
        dx = abs(state.x - goal[0])
        dy = abs(state.y - goal[1])
        dtheta = abs(self._normalize_angle(state.theta - goal[2]))
        
        return (dx < position_tolerance and 
                dy < position_tolerance and 
                dtheta < angle_tolerance)
    
    def _reconstruct_path(self, goal_state: VehicleState) -> List[VehicleState]:
        """
        重构路径
        
        Args:
            goal_state: 目标状态
            
        Returns:
            path: 路径状态列表
        """
        path = []
        current = goal_state
        
        while current is not None:
            path.append(current)
            current = current.parent
        
        path.reverse()
        return path
    
    def _world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """
        世界坐标转栅格坐标
        
        Args:
            x, y: 世界坐标
            
        Returns:
            grid_x, grid_y: 栅格坐标
        """
        grid_x = int(x)
        grid_y = int(y)
        return grid_x, grid_y
    
    def _is_in_bounds(self, x: float, y: float) -> bool:
        """
        检查坐标是否在边界内
        
        Args:
            x, y: 坐标
            
        Returns:
            in_bounds: 是否在边界内
        """
        return 0 <= x < self.width and 0 <= y < self.height
    
    def _normalize_angle(self, angle: float) -> float:
        """
        角度归一化到[-π, π]
        
        Args:
            angle: 角度
            
        Returns:
            normalized_angle: 归一化后的角度
        """
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
    
    def _get_action_name(self, steer_angle: float) -> str:
        """
        获取动作名称

        Args:
            steer_angle: 转向角

        Returns:
            action_name: 动作名称
        """
        if abs(steer_angle) < 0.1:
            return "直行"
        elif steer_angle > 0:
            return "左转"
        else:
            return "右转"

    def _discretize_state(self, state: VehicleState) -> Tuple[int, int, int]:
        """
        离散化状态用于去重

        Args:
            state: 车辆状态

        Returns:
            discretized_state: 离散化的状态键
        """
        # 位置离散化精度
        xy_resolution = 0.5
        # 角度离散化精度（将360度分成72份，每份5度）
        theta_resolution = math.pi / 36  # 5度

        disc_x = int(round(state.x / xy_resolution))
        disc_y = int(round(state.y / xy_resolution))
        disc_theta = int(round(state.theta / theta_resolution))

        return (disc_x, disc_y, disc_theta)

class PathVisualizer:
    """
    路径可视化器
    """
    
    def __init__(self, grid_map):
        """
        初始化可视化器
        
        Args:
            grid_map: 栅格地图
        """
        self.grid_map = grid_map
        self.height, self.width = grid_map.shape
    
    def visualize_path(self, path: List[VehicleState],
                     start: Tuple[float, float, float],
                     goal: Tuple[float, float, float],
                     vehicle_params: VehicleParams,
                     save_file: Optional[str] = None):
        """
        可视化路径规划结果

        Args:
            path: 路径状态列表
            start: 起始位置
            goal: 目标位置
            vehicle_params: 车辆参数
            save_file: 保存文件路径（可选）
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

        # 绘制地图 (反转颜色：白色背景，黑色障碍物)
        ax.imshow(self.grid_map, cmap='gray_r', origin='lower')
        
        # 绘制起始和目标位置
        ax.plot(start[0], start[1], 'go', markersize=10, label='Start Position')
        ax.plot(goal[0], goal[1], 'ro', markersize=10, label='Goal Position')

        if path:
            # 绘制路径
            path_x = [state.x for state in path]
            path_y = [state.y for state in path]
            ax.plot(path_x, path_y, 'b-', linewidth=2, label='Planned Path')
            
            # 绘制车辆轨迹
            for i, state in enumerate(path[::5]):  # 每5个点绘制一次
                self._draw_vehicle(ax, state, vehicle_params, alpha=0.3)
            
            # 绘制起点和终点的车辆
            self._draw_vehicle(ax, path[0], vehicle_params, color='green')
            self._draw_vehicle(ax, path[-1], vehicle_params, color='red')
        
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.set_title('Hybrid A* Path Planning Result')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_file:
            plt.savefig(save_file, dpi=150, bbox_inches='tight')
            print(f"Path visualization saved to: {save_file}")
            plt.close()
        else:
            plt.show()
    
    def _draw_vehicle(self, ax, state: VehicleState, vehicle_params: VehicleParams, 
                     color='blue', alpha=1.0):
        """
        绘制车辆
        
        Args:
            ax: matplotlib轴对象
            state: 车辆状态
            vehicle_params: 车辆参数
            color: 颜色
            alpha: 透明度
        """
        # 计算车辆四个角点
        half_length = vehicle_params.length / 2
        half_width = vehicle_params.width / 2
        
        # 车辆局部坐标系下的角点
        local_corners = [
            (-half_length, -half_width),
            (-half_length, half_width),
            (half_length, half_width),
            (half_length, -half_width)
        ]
        
        # 转换到世界坐标系
        cos_theta = math.cos(state.theta)
        sin_theta = math.sin(state.theta)
        
        world_corners = []
        for local_x, local_y in local_corners:
            world_x = state.x + local_x * cos_theta - local_y * sin_theta
            world_y = state.y + local_x * sin_theta + local_y * cos_theta
            world_corners.append([world_x, world_y])
        
        # 绘制车辆
        vehicle_polygon = patches.Polygon(world_corners, closed=True, 
                                        facecolor=color, alpha=alpha, edgecolor='black')
        ax.add_patch(vehicle_polygon)
        
        # 绘制车辆方向
        front_x = state.x + half_length * cos_theta
        front_y = state.y + half_length * sin_theta
        ax.plot([state.x, front_x], [state.y, front_y], 'k-', linewidth=2)

    def create_animation(self, path: List[VehicleState],
                        start: Tuple[float, float, float],
                        goal: Tuple[float, float, float],
                        vehicle_params: VehicleParams,
                        save_file: str = 'path_animation.gif'):
        """
        创建路径规划的动画GIF

        Args:
            path: 路径状态列表
            start: 起始位置
            goal: 目标位置
            vehicle_params: 车辆参数
            save_file: 保存文件路径
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

        def init():
            ax.clear()
            ax.imshow(self.grid_map, cmap='gray_r', origin='lower')
            ax.plot(start[0], start[1], 'go', markersize=10, label='Start Position')
            ax.plot(goal[0], goal[1], 'ro', markersize=10, label='Goal Position')
            ax.set_xlim(0, self.width)
            ax.set_ylim(0, self.height)
            ax.set_xlabel('X (meters)')
            ax.set_ylabel('Y (meters)')
            ax.set_title('Hybrid A* Path Planning Animation')
            ax.legend()
            ax.grid(True, alpha=0.3)
            return []

        def update(frame):
            # 清除之前的车辆和路径
            ax.clear()
            ax.imshow(self.grid_map, cmap='gray_r', origin='lower')
            ax.plot(start[0], start[1], 'go', markersize=10, label='Start Position')
            ax.plot(goal[0], goal[1], 'ro', markersize=10, label='Goal Position')

            # 绘制已走过的路径
            if frame > 0:
                path_x = [state.x for state in path[:frame+1]]
                path_y = [state.y for state in path[:frame+1]]
                ax.plot(path_x, path_y, 'b-', linewidth=2, alpha=0.6, label='Planned Path')

            # 绘制当前车辆位置
            if frame < len(path):
                current_state = path[frame]
                self._draw_vehicle(ax, current_state, vehicle_params, color='cyan', alpha=0.8)

                # 显示进度信息
                progress = (frame + 1) / len(path) * 100
                ax.text(self.width * 0.02, self.height * 0.98,
                       f'Progress: {progress:.1f}% ({frame+1}/{len(path)})',
                       fontsize=12, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                       verticalalignment='top')

            ax.set_xlim(0, self.width)
            ax.set_ylim(0, self.height)
            ax.set_xlabel('X (meters)')
            ax.set_ylabel('Y (meters)')
            ax.set_title('Hybrid A* Path Planning Animation')
            ax.legend()
            ax.grid(True, alpha=0.3)
            return []

        # 创建动画
        frames = len(path)
        anim = FuncAnimation(fig, update, init_func=init, frames=frames,
                           interval=100, blit=False, repeat=True)

        # 保存为GIF
        writer = PillowWriter(fps=10)
        anim.save(save_file, writer=writer)
        plt.close()
        print(f"Animation saved to: {save_file}")

# 使用示例和演示
def generate_random_position(grid_map: np.ndarray, vehicle_params: VehicleParams,
                            margin: float = 5.0) -> Tuple[float, float, float]:
    """
    生成一个随机的有效位置（不在障碍物中）

    Args:
        grid_map: 栅格地图
        vehicle_params: 车辆参数
        margin: 距离边界和障碍物的最小距离

    Returns:
        position: (x, y, theta) 随机位置和方向
    """
    height, width = grid_map.shape
    max_attempts = 1000

    for _ in range(max_attempts):
        # 生成随机位置
        x = random.uniform(margin, width - margin)
        y = random.uniform(margin, height - margin)
        theta = random.uniform(-math.pi, math.pi)

        # 创建临时状态来检查碰撞
        temp_state = VehicleState(x=x, y=y, theta=theta, gear=1, cost=0.0)

        # 检查车辆是否与障碍物碰撞
        corners = get_vehicle_corners(temp_state, vehicle_params)
        collision = False

        for corner in corners:
            grid_x, grid_y = int(corner[0]), int(corner[1])
            if 0 <= grid_x < width and 0 <= grid_y < height:
                if grid_map[grid_y, grid_x] == 1:
                    collision = True
                    break

        if not collision:
            return (x, y, theta)

    # 如果无法找到有效位置，返回默认位置
    print("Warning: Could not find random position, using default")
    return (margin, margin, 0.0)

def get_vehicle_corners(state: VehicleState, vehicle_params: VehicleParams) -> List[Tuple[float, float]]:
    """
    计算车辆四个角点的世界坐标（辅助函数）

    Args:
        state: 车辆状态
        vehicle_params: 车辆参数

    Returns:
        corners: 四个角点坐标
    """
    half_length = vehicle_params.length / 2
    half_width = vehicle_params.width / 2

    local_corners = [
        (-half_length, -half_width),
        (-half_length, half_width),
        (half_length, half_width),
        (half_length, -half_width)
    ]

    world_corners = []
    cos_theta = math.cos(state.theta)
    sin_theta = math.sin(state.theta)

    for local_x, local_y in local_corners:
        world_x = state.x + local_x * cos_theta - local_y * sin_theta
        world_y = state.y + local_x * sin_theta + local_y * cos_theta
        world_corners.append((world_x, world_y))

    return world_corners

def demo_hybrid_astar():
    """
    Hybrid A*算法演示函数
    """
    print("=== Hybrid A* 路径规划演示 ===")

    # 创建地图
    map_size = (50, 50)
    grid_map = np.zeros(map_size)

    # 添加多个障碍物，创建一个需要绕行的场景
    grid_map[10:40, 24:26] = 1  # 中央垂直墙壁（留有缺口）
    grid_map[15:20, 15:20] = 1  # 左侧障碍物
    grid_map[30:35, 35:40] = 1  # 右侧障碍物
    grid_map[5:10, 30:35] = 1   # 上方障碍物

    # 车辆参数
    vehicle_params = VehicleParams()

    # 创建Hybrid A*算法
    planner = HybridAStar(grid_map, vehicle_params)

    # 生成随机起点和终点
    print("生成随机起点和终点...")
    # 设置随机种子以确保可重复性（可注释以获得真正随机的结果）
    random.seed(42)
    start = generate_random_position(grid_map, vehicle_params, margin=5.0)
    goal = generate_random_position(grid_map, vehicle_params, margin=5.0)
    
    print(f"起始位置: {start}")
    print(f"目标位置: {goal}")
    
    # 执行路径规划
    print("开始路径规划...")
    path = planner.search(start, goal)
    
    if path:
        print(f"路径规划成功！路径长度: {len(path)} 个状态")
        print(f"总代价: {path[-1].cost:.2f}")
        
        # 分析路径特征
        gear_changes = 0
        direction_changes = 0
        
        for i in range(1, len(path)):
            if path[i].gear != path[i-1].gear:
                gear_changes += 1
            if path[i].action != path[i-1].action:
                direction_changes += 1
        
        print(f"换挡次数: {gear_changes}")
        print(f"方向切换次数: {direction_changes}")

        # 可视化结果
        visualizer = PathVisualizer(grid_map)

        # 保存静态图
        print("\n生成静态路径图...")
        visualizer.visualize_path(path, start, goal, vehicle_params, save_file='path_result.png')

        # 创建动画GIF
        print("\n生成动画GIF（这可能需要一些时间）...")
        visualizer.create_animation(path, start, goal, vehicle_params, save_file='path_animation.gif')
        
    else:
        print("路径规划失败！无法找到可行路径")

# 运行演示
if __name__ == "__main__":
    demo_hybrid_astar()
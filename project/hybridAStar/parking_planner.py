# 自动泊车路径规划系统 - 基于Hybrid A*算法
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
    """
    wheelbase: float = 2.8        # 轴距 (米)
    max_steer: float = 0.6        # 最大转向角 (弧度)
    min_radius: float = 5.0       # 最小转弯半径 (米)
    step_size: float = 0.5        # 步长 (米)
    width: float = 1.8            # 车宽 (米)
    length: float = 4.5           # 车长 (米)

class ParkingPlanner:
    """
    自动泊车路径规划器 - 支持前进和倒车
    """

    def __init__(self, grid_map, vehicle_params: VehicleParams, enable_reverse: bool = True):
        """
        初始化泊车规划器

        Args:
            grid_map: 栅格地图
            vehicle_params: 车辆参数
            enable_reverse: 是否启用倒车
        """
        self.grid_map = grid_map
        self.vehicle_params = vehicle_params
        self.height, self.width = grid_map.shape
        self.enable_reverse = enable_reverse

        # 搜索方向：直行、左转、右转
        self.directions = [0, vehicle_params.max_steer, -vehicle_params.max_steer]

        # 挡位选项
        self.gears = [1, -1] if enable_reverse else [1]

        # 代价权重
        self.weights = {
            'distance': 1.0,
            'curvature': 2.0,
            'gear_change': 10.0,      # 换挡代价更高
            'direction_change': 3.0,
            'obstacle': 10.0,
            'reverse_penalty': 1.5     # 倒车惩罚
        }

    def heuristic(self, state: VehicleState, goal: Tuple[float, float, float]) -> float:
        """启发式函数"""
        dx = state.x - goal[0]
        dy = state.y - goal[1]
        distance_cost = math.sqrt(dx*dx + dy*dy)

        angle_diff = abs(state.theta - goal[2])
        angle_cost = min(angle_diff, 2*math.pi - angle_diff)

        return distance_cost + 0.5 * angle_cost

    def get_neighbors(self, state: VehicleState) -> List[Tuple[VehicleState, float]]:
        """获取邻居状态（包括前进和倒车）"""
        neighbors = []

        for gear in self.gears:
            for direction in self.directions:
                new_state = self._apply_motion_model(state, direction, gear)

                if new_state is not None and not self._is_collision(new_state):
                    cost = self._calculate_transition_cost(state, new_state)
                    neighbors.append((new_state, cost))

        return neighbors

    def _apply_motion_model(self, state: VehicleState, steer_angle: float, gear: int) -> Optional[VehicleState]:
        """应用运动模型"""
        x = state.x
        y = state.y
        theta = state.theta

        # 计算新位置（倒车时方向相反）
        step = self.vehicle_params.step_size * gear
        new_x = x + step * math.cos(theta)
        new_y = y + step * math.sin(theta)
        new_theta = theta + step * math.tan(steer_angle) / self.vehicle_params.wheelbase

        # 角度归一化
        new_theta = self._normalize_angle(new_theta)

        # 检查边界
        if not self._is_in_bounds(new_x, new_y):
            return None

        # 创建新状态
        new_state = VehicleState(
            x=new_x,
            y=new_y,
            theta=new_theta,
            gear=gear,
            cost=state.cost,
            parent=state,
            action=self._get_action_name(steer_angle, gear)
        )

        return new_state

    def _is_collision(self, state: VehicleState) -> bool:
        """检查碰撞"""
        corners = self._get_vehicle_corners(state)

        for corner in corners:
            grid_x, grid_y = self._world_to_grid(corner[0], corner[1])

            if (0 <= grid_x < self.width and 0 <= grid_y < self.height):
                if self.grid_map[grid_y, grid_x] == 1:
                    return True

        return False

    def _get_vehicle_corners(self, state: VehicleState) -> List[Tuple[float, float]]:
        """计算车辆四个角点"""
        half_length = self.vehicle_params.length / 2
        half_width = self.vehicle_params.width / 2

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

    def _calculate_transition_cost(self, from_state: VehicleState, to_state: VehicleState) -> float:
        """计算状态转移代价"""
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

        # 倒车惩罚
        if to_state.gear == -1:
            cost += self.weights['reverse_penalty'] * distance

        # 方向切换代价
        if from_state.action != to_state.action:
            cost += self.weights['direction_change']

        # 障碍物代价
        obstacle_cost = self._get_obstacle_penalty(to_state)
        cost += self.weights['obstacle'] * obstacle_cost

        return cost

    def _get_obstacle_penalty(self, state: VehicleState) -> float:
        """计算障碍物惩罚"""
        safety_distance = 1.0
        corners = self._get_vehicle_corners(state)

        min_distance = float('inf')
        for corner in corners:
            grid_x, grid_y = self._world_to_grid(corner[0], corner[1])

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
        """执行路径搜索"""
        start_state = VehicleState(
            x=start[0], y=start[1], theta=start[2],
            gear=1, cost=0.0
        )

        counter = 0
        open_list = [(0, counter, start_state)]
        closed_set = set()
        g_score = defaultdict(lambda: float('inf'))
        start_key = self._discretize_state(start_state)
        g_score[start_key] = 0

        max_iterations = 50000
        iteration = 0

        while open_list and iteration < max_iterations:
            iteration += 1

            current_f, _, current_state = heapq.heappop(open_list)

            if self._is_goal_reached(current_state, goal):
                print(f"找到路径! 迭代次数: {iteration}")
                return self._reconstruct_path(current_state)

            state_key = self._discretize_state(current_state)
            if state_key in closed_set:
                continue
            closed_set.add(state_key)

            # 调试输出
            if iteration % 5000 == 0:
                print(f"迭代 {iteration}: 当前位置({current_state.x:.1f}, {current_state.y:.1f}, {current_state.theta:.2f}), "
                      f"挡位: {'前进' if current_state.gear == 1 else '倒车'}")

            neighbors = self.get_neighbors(current_state)

            for neighbor_state, transition_cost in neighbors:
                neighbor_key = self._discretize_state(neighbor_state)

                if neighbor_key in closed_set:
                    continue

                tentative_g = g_score[state_key] + transition_cost

                if tentative_g < g_score[neighbor_key]:
                    neighbor_state.parent = current_state
                    neighbor_state.cost = tentative_g
                    g_score[neighbor_key] = tentative_g

                    f_score = tentative_g + self.heuristic(neighbor_state, goal)
                    counter += 1
                    heapq.heappush(open_list, (f_score, counter, neighbor_state))

        if iteration >= max_iterations:
            print(f"达到最大迭代次数 {max_iterations}，搜索终止")

        return None

    def _is_goal_reached(self, state: VehicleState, goal: Tuple[float, float, float]) -> bool:
        """检查是否到达目标"""
        position_tolerance = 1.5  # 增加位置容差
        angle_tolerance = 0.5     # 增加角度容差

        dx = abs(state.x - goal[0])
        dy = abs(state.y - goal[1])
        dtheta = abs(self._normalize_angle(state.theta - goal[2]))

        return (dx < position_tolerance and
                dy < position_tolerance and
                dtheta < angle_tolerance)

    def _reconstruct_path(self, goal_state: VehicleState) -> List[VehicleState]:
        """重构路径"""
        path = []
        current = goal_state

        while current is not None:
            path.append(current)
            current = current.parent

        path.reverse()
        return path

    def _discretize_state(self, state: VehicleState) -> Tuple[int, int, int, int]:
        """离散化状态（包括挡位）"""
        xy_resolution = 0.5
        theta_resolution = math.pi / 36

        disc_x = int(round(state.x / xy_resolution))
        disc_y = int(round(state.y / xy_resolution))
        disc_theta = int(round(state.theta / theta_resolution))

        return (disc_x, disc_y, disc_theta, state.gear)

    def _world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """世界坐标转栅格坐标"""
        return int(x), int(y)

    def _is_in_bounds(self, x: float, y: float) -> bool:
        """检查边界"""
        return 0 <= x < self.width and 0 <= y < self.height

    def _normalize_angle(self, angle: float) -> float:
        """角度归一化"""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def _get_action_name(self, steer_angle: float, gear: int) -> str:
        """获取动作名称"""
        gear_name = "Forward" if gear == 1 else "Reverse"

        if abs(steer_angle) < 0.1:
            return f"{gear_name}-Straight"
        elif steer_angle > 0:
            return f"{gear_name}-Left"
        else:
            return f"{gear_name}-Right"

class ParkingVisualizer:
    """
    停车场景可视化器
    """

    def __init__(self, grid_map):
        self.grid_map = grid_map
        self.height, self.width = grid_map.shape

    def visualize_path(self, path: List[VehicleState],
                     start: Tuple[float, float, float],
                     goal: Tuple[float, float, float],
                     vehicle_params: VehicleParams,
                     parking_spot: Tuple[float, float, float, float] = None,
                     save_file: Optional[str] = None):
        """可视化停车路径"""
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))

        # 绘制地图
        ax.imshow(self.grid_map, cmap='gray_r', origin='lower')

        # 绘制停车位（如果提供）
        if parking_spot:
            spot_x, spot_y, spot_w, spot_h = parking_spot
            spot_rect = patches.Rectangle((spot_x, spot_y), spot_w, spot_h,
                                         linewidth=3, edgecolor='orange',
                                         facecolor='yellow', alpha=0.3,
                                         label='Parking Spot')
            ax.add_patch(spot_rect)

        # 绘制起点和终点
        ax.plot(start[0], start[1], 'go', markersize=12, label='Start Position')
        ax.plot(goal[0], goal[1], 'ro', markersize=12, label='Goal Position')

        if path:
            # 绘制路径
            path_x = [state.x for state in path]
            path_y = [state.y for state in path]
            ax.plot(path_x, path_y, 'b-', linewidth=2, label='Planned Path', alpha=0.6)

            # 绘制车辆轨迹（区分前进和倒车）
            for i in range(0, len(path), 5):
                state = path[i]
                color = 'lightblue' if state.gear == 1 else 'lightcoral'
                self._draw_vehicle(ax, state, vehicle_params, color=color, alpha=0.3)

            # 绘制起点和终点的车辆
            self._draw_vehicle(ax, path[0], vehicle_params, color='green', alpha=0.8)
            self._draw_vehicle(ax, path[-1], vehicle_params, color='red', alpha=0.8)

        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_xlabel('X (meters)', fontsize=12)
        ax.set_ylabel('Y (meters)', fontsize=12)
        ax.set_title('Automatic Parking - Hybrid A* Path Planning', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_file:
            plt.savefig(save_file, dpi=150, bbox_inches='tight')
            print(f"Parking path visualization saved to: {save_file}")
            plt.close()
        else:
            plt.show()

    def _draw_vehicle(self, ax, state: VehicleState, vehicle_params: VehicleParams,
                     color='blue', alpha=1.0):
        """绘制车辆"""
        half_length = vehicle_params.length / 2
        half_width = vehicle_params.width / 2

        local_corners = [
            (-half_length, -half_width),
            (-half_length, half_width),
            (half_length, half_width),
            (half_length, -half_width)
        ]

        cos_theta = math.cos(state.theta)
        sin_theta = math.sin(state.theta)

        world_corners = []
        for local_x, local_y in local_corners:
            world_x = state.x + local_x * cos_theta - local_y * sin_theta
            world_y = state.y + local_x * sin_theta + local_y * cos_theta
            world_corners.append([world_x, world_y])

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
                        parking_spot: Tuple[float, float, float, float] = None,
                        save_file: str = 'parking_animation.gif'):
        """创建停车动画"""
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))

        def init():
            ax.clear()
            ax.imshow(self.grid_map, cmap='gray_r', origin='lower')

            if parking_spot:
                spot_x, spot_y, spot_w, spot_h = parking_spot
                spot_rect = patches.Rectangle((spot_x, spot_y), spot_w, spot_h,
                                             linewidth=3, edgecolor='orange',
                                             facecolor='yellow', alpha=0.3)
                ax.add_patch(spot_rect)

            ax.plot(start[0], start[1], 'go', markersize=12, label='Start')
            ax.plot(goal[0], goal[1], 'ro', markersize=12, label='Goal')
            ax.set_xlim(0, self.width)
            ax.set_ylim(0, self.height)
            ax.set_xlabel('X (meters)')
            ax.set_ylabel('Y (meters)')
            ax.set_title('Automatic Parking Animation')
            ax.legend()
            ax.grid(True, alpha=0.3)
            return []

        def update(frame):
            ax.clear()
            ax.imshow(self.grid_map, cmap='gray_r', origin='lower')

            if parking_spot:
                spot_x, spot_y, spot_w, spot_h = parking_spot
                spot_rect = patches.Rectangle((spot_x, spot_y), spot_w, spot_h,
                                             linewidth=3, edgecolor='orange',
                                             facecolor='yellow', alpha=0.3)
                ax.add_patch(spot_rect)

            ax.plot(start[0], start[1], 'go', markersize=12, label='Start')
            ax.plot(goal[0], goal[1], 'ro', markersize=12, label='Goal')

            # 绘制已走过的路径
            if frame > 0:
                path_x = [state.x for state in path[:frame+1]]
                path_y = [state.y for state in path[:frame+1]]
                ax.plot(path_x, path_y, 'b-', linewidth=2, alpha=0.6)

            # 绘制当前车辆
            if frame < len(path):
                current_state = path[frame]
                color = 'cyan' if current_state.gear == 1 else 'orange'
                self._draw_vehicle(ax, current_state, vehicle_params, color=color, alpha=0.8)

                # 显示信息
                progress = (frame + 1) / len(path) * 100
                gear_text = 'Forward' if current_state.gear == 1 else 'Reverse'
                ax.text(self.width * 0.02, self.height * 0.98,
                       f'Progress: {progress:.1f}% ({frame+1}/{len(path)})\nGear: {gear_text}',
                       fontsize=12, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                       verticalalignment='top')

            ax.set_xlim(0, self.width)
            ax.set_ylim(0, self.height)
            ax.set_xlabel('X (meters)')
            ax.set_ylabel('Y (meters)')
            ax.set_title('Automatic Parking Animation')
            ax.legend()
            ax.grid(True, alpha=0.3)
            return []

        frames = len(path)
        anim = FuncAnimation(fig, update, init_func=init, frames=frames,
                           interval=100, blit=False, repeat=True)

        writer = PillowWriter(fps=10)
        anim.save(save_file, writer=writer)
        plt.close()
        print(f"Parking animation saved to: {save_file}")

def create_parking_scenario():
    """
    创建停车场景
    """
    print("=== 自动泊车路径规划演示 ===\n")

    # 创建停车场地图 (40x50米) - 简化场景
    map_size = (40, 50)
    grid_map = np.zeros(map_size)

    # 添加停车场边界
    grid_map[:, 0:2] = 1       # 左边界
    grid_map[:, 48:50] = 1     # 右边界
    grid_map[0:2, :] = 1       # 下边界
    grid_map[38:40, :] = 1     # 上边界

    # 停车位分隔线（开放式停车位，只有线标记）
    grid_map[25:26, 6:12] = 1    # 停车位底部标记线
    grid_map[25:33, 6:7] = 1     # 停车位左侧标记线

    # 其他已停车辆（障碍物）- 远离停车位区域
    grid_map[8:14, 35:41] = 1    # 右侧一辆车
    grid_map[20:26, 35:41] = 1   # 右侧另一辆车

    # 车辆参数
    vehicle_params = VehicleParams()

    # 创建停车规划器（启用倒车）
    planner = ParkingPlanner(grid_map, vehicle_params, enable_reverse=True)

    # 设置起点和目标停车位
    # 起点：停车场车道上，准备泊车
    start = (20.0, 10.0, math.pi/2)  # 在停车位下方，面向上

    # 目标：停车位内
    goal = (9.0, 29.0, math.pi/2)  # 停车位中心，面向上

    # 停车位位置 (x, y, width, height) - 合理尺寸
    # 宽度约6米，长度约8米（含缓冲区）
    parking_spot = (7, 26, 6, 8)

    print(f"起始位置: ({start[0]:.1f}, {start[1]:.1f}, {start[2]:.2f})")
    print(f"目标停车位: ({goal[0]:.1f}, {goal[1]:.1f}, {goal[2]:.2f})")
    print(f"启用倒车: 是\n")

    # 执行路径规划
    print("开始路径规划...")
    path = planner.search(start, goal)

    if path:
        print(f"\n✓ 路径规划成功！")
        print(f"路径长度: {len(path)} 个状态")
        print(f"总代价: {path[-1].cost:.2f}")

        # 分析路径特征
        forward_count = sum(1 for state in path if state.gear == 1)
        reverse_count = sum(1 for state in path if state.gear == -1)
        gear_changes = sum(1 for i in range(1, len(path)) if path[i].gear != path[i-1].gear)

        print(f"前进步数: {forward_count}")
        print(f"倒车步数: {reverse_count}")
        print(f"换挡次数: {gear_changes}")

        # 可视化
        visualizer = ParkingVisualizer(grid_map)

        print("\n生成静态停车路径图...")
        visualizer.visualize_path(path, start, goal, vehicle_params,
                                 parking_spot=parking_spot,
                                 save_file='parking_result.png')

        print("\n生成停车动画GIF（这可能需要一些时间）...")
        visualizer.create_animation(path, start, goal, vehicle_params,
                                   parking_spot=parking_spot,
                                   save_file='parking_animation.gif')

        print("\n✓ 所有可视化文件已生成！")
    else:
        print("\n✗ 路径规划失败！无法找到可行路径")

if __name__ == "__main__":
    create_parking_scenario()

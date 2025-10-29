"""
第3课: Pure Pursuit路径跟踪控制器

Pure Pursuit是一种基于几何的路径跟踪算法。

核心思想:
- 在路径上选择一个"预瞄点"(Lookahead Point)
- 计算转向角使车辆朝向该点
- 随着车辆前进，预瞄点动态更新

关键参数:
- Ld (Lookahead Distance): 预瞄距离
  * 小 → 跟踪精确但易震荡
  * 大 → 运动平稳但跟踪误差大
  * 通常设为: Ld = k·v + Ld_min

转向控制公式:
    α = atan2(Δy, Δx) - θ         # 车头指向预瞄点的角度
    δ = atan(2L·sin(α) / Ld)      # 转向角

作者: Path Planning Course Team
"""

import numpy as np
import math
from typing import List, Tuple, Optional
import sys
sys.path.append('..')
from vehicle.bicycle_model import BicycleModel


class PurePursuitController:
    """
    Pure Pursuit路径跟踪控制器
    
    几何控制方法，适合:
    - 平滑路径
    - 中低速场景
    - 计算资源受限的系统
    
    使用方法:
        >>> controller = PurePursuitController(wheelbase=2.7, k=1.0, ld_min=2.0)
        >>> state = [x, y, θ, v]
        >>> steer = controller.control(state, ref_path)
    """
    
    def __init__(
        self,
        wheelbase: float = 2.7,
        k_lookahead: float = 1.0,
        ld_min: float = 2.0,
        max_steer: float = np.deg2rad(35)
    ):
        """
        初始化Pure Pursuit控制器
        
        Args:
            wheelbase: 车辆轴距 (m)
            k_lookahead: 预瞄距离系数 (无量纲)
            ld_min: 最小预瞄距离 (m)
            max_steer: 最大转向角 (rad)
        
        预瞄距离计算:
            Ld = k·v + Ld_min
            
            - k越大，预瞄距离随速度增加越快
            - Ld_min保证低速时也有足够预瞄
        """
        self.L = wheelbase
        self.k = k_lookahead
        self.ld_min = ld_min
        self.max_steer = max_steer
        
        # 统计信息
        self.lateral_errors = []  # 横向误差历史
        self.control_history = []  # 控制历史
        
        print(f"[Pure Pursuit] 初始化完成")
        print(f"  轴距 L = {wheelbase:.2f} m")
        print(f"  预瞄系数 k = {k_lookahead:.2f}")
        print(f"  最小预瞄距离 = {ld_min:.2f} m")
        print(f"  最大转向角 = {np.rad2deg(max_steer):.1f}°")
    
    def calc_lookahead_distance(self, velocity: float) -> float:
        """
        根据速度计算预瞄距离
        
        Args:
            velocity: 当前速度 (m/s)
        
        Returns:
            预瞄距离 (m)
        
        设计原则:
            - 高速时需要更长预瞄距离（提前规划）
            - 低速时缩短预瞄距离（精确跟踪）
            - 保证最小预瞄距离（避免过于敏感）
        """
        return self.k * abs(velocity) + self.ld_min
    
    def find_nearest_point(
        self,
        vehicle_pos: np.ndarray,
        path: np.ndarray
    ) -> int:
        """
        在路径上找到距离车辆最近的点
        
        Args:
            vehicle_pos: 车辆位置 (x, y)
            path: 路径数组，形状(N, 2)或(N, 4)
        
        Returns:
            最近点的索引
        
        注意:
            这是个O(N)算法，大规模路径可用KD树优化
        """
        # 提取路径的xy坐标
        if path.shape[1] >= 2:
            path_xy = path[:, :2]
        else:
            raise ValueError("路径至少需要包含x, y坐标")
        
        # 计算距离
        distances = np.linalg.norm(path_xy - vehicle_pos, axis=1)
        
        # 返回最小距离的索引
        return np.argmin(distances)
    
    def find_lookahead_point(
        self,
        vehicle_pos: np.ndarray,
        path: np.ndarray,
        lookahead_dist: float,
        start_idx: int = 0
    ) -> Optional[Tuple[np.ndarray, int]]:
        """
        在路径上找到预瞄点
        
        预瞄点定义:
            从车辆当前位置开始，沿路径向前找到距离≥Ld的第一个点
        
        Args:
            vehicle_pos: 车辆位置 (x, y)
            path: 路径数组，形状(N, 2)或(N, 4)
            lookahead_dist: 预瞄距离
            start_idx: 起始搜索索引（通常是最近点）
        
        Returns:
            (lookahead_point, index) 或 None
            - lookahead_point: 预瞄点坐标 (x, y)
            - index: 预瞄点在路径中的索引
        
        特殊情况:
            - 如果整条路径都在预瞄距离内 → 返回路径终点
            - 如果路径为空 → 返回None
        """
        if len(path) == 0:
            return None
        
        # 提取路径xy
        path_xy = path[:, :2]
        
        # 从start_idx开始向前搜索
        for i in range(start_idx, len(path)):
            dist = np.linalg.norm(path_xy[i] - vehicle_pos)
            
            if dist >= lookahead_dist:
                return path_xy[i], i
        
        # 没找到 → 返回路径终点
        return path_xy[-1], len(path) - 1
    
    def calc_lateral_error(
        self,
        vehicle_pos: np.ndarray,
        path: np.ndarray
    ) -> float:
        """
        计算横向误差（车辆到路径的垂直距离）
        
        Args:
            vehicle_pos: 车辆位置 (x, y)
            path: 路径数组
        
        Returns:
            横向误差 (m)
        
        简化版本:
            使用车辆到最近路径点的距离
            
        完整版本应该:
            计算车辆到路径线段的垂直距离
        """
        if len(path) == 0:
            return 0.0
        
        path_xy = path[:, :2]
        distances = np.linalg.norm(path_xy - vehicle_pos, axis=1)
        return np.min(distances)
    
    def control(
        self,
        vehicle_state: np.ndarray,
        ref_path: np.ndarray
    ) -> float:
        """
        Pure Pursuit控制主函数
        
        Args:
            vehicle_state: 车辆状态 [x, y, θ, v]
            ref_path: 参考路径，形状(N, 2)或(N, 4)
        
        Returns:
            steer: 转向角 (rad)
        
        算法步骤:
        1. 根据速度计算预瞄距离 Ld
        2. 找到路径上距离车辆≥Ld的预瞄点
        3. 计算车头指向预瞄点的角度 α
        4. 应用Pure Pursuit公式: δ = atan(2L·sin(α)/Ld)
        5. 限制转向角在物理约束内
        """
        # 解包状态
        x, y, theta, v = vehicle_state
        vehicle_pos = np.array([x, y])
        
        # 检查路径
        if len(ref_path) == 0:
            print("[Pure Pursuit] 警告: 路径为空")
            return 0.0
        
        # 步骤1: 计算预瞄距离
        ld = self.calc_lookahead_distance(v)
        
        # 步骤2: 找到最近点（起始搜索位置）
        nearest_idx = self.find_nearest_point(vehicle_pos, ref_path)
        
        # 步骤3: 找到预瞄点
        result = self.find_lookahead_point(vehicle_pos, ref_path, ld, nearest_idx)
        
        if result is None:
            print("[Pure Pursuit] 警告: 未找到预瞄点")
            return 0.0
        
        lookahead_point, lookahead_idx = result
        
        # 步骤4: 计算车辆到预瞄点的向量
        dx = lookahead_point[0] - x
        dy = lookahead_point[1] - y
        
        # 转换到车辆坐标系
        # 全局坐标系 (x_g, y_g) → 车辆坐标系 (x_v, y_v)
        # 旋转矩阵: R(-θ)
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        
        local_x = dx * cos_theta + dy * sin_theta
        local_y = -dx * sin_theta + dy * cos_theta
        
        # 步骤5: 计算角度α（车头指向预瞄点的相对角度）
        alpha = np.arctan2(local_y, local_x)
        
        # 步骤6: Pure Pursuit公式
        # δ = atan(2L·sin(α) / Ld)
        steer = np.arctan2(2 * self.L * np.sin(alpha), ld)
        
        # 步骤7: 限制转向角
        steer = np.clip(steer, -self.max_steer, self.max_steer)
        
        # 记录统计信息
        lateral_error = self.calc_lateral_error(vehicle_pos, ref_path)
        self.lateral_errors.append(lateral_error)
        self.control_history.append(steer)
        
        return steer
    
    def get_statistics(self) -> dict:
        """
        获取控制统计信息
        
        Returns:
            包含统计指标的字典
        """
        if not self.lateral_errors:
            return {}
        
        return {
            'mean_lateral_error': np.mean(self.lateral_errors),
            'max_lateral_error': np.max(self.lateral_errors),
            'std_lateral_error': np.std(self.lateral_errors),
            'mean_steer': np.mean(np.abs(self.control_history)),
            'max_steer': np.max(np.abs(self.control_history)),
        }
    
    def reset_statistics(self):
        """重置统计信息"""
        self.lateral_errors = []
        self.control_history = []


class PathFollowingSimulator:
    """
    路径跟踪仿真器
    
    组合控制器和车辆模型，进行闭环仿真
    """
    
    def __init__(
        self,
        controller: PurePursuitController,
        vehicle_model: BicycleModel,
        dt: float = 0.1
    ):
        """
        初始化仿真器
        
        Args:
            controller: Pure Pursuit控制器
            vehicle_model: 车辆模型
            dt: 仿真时间步长 (s)
        """
        self.controller = controller
        self.vehicle = vehicle_model
        self.dt = dt
    
    def simulate(
        self,
        initial_state: np.ndarray,
        ref_path: np.ndarray,
        max_steps: int = 1000,
        goal_tolerance: float = 0.5
    ) -> Tuple[np.ndarray, dict]:
        """
        执行路径跟踪仿真
        
        Args:
            initial_state: 初始状态 [x, y, θ, v]
            ref_path: 参考路径
            max_steps: 最大仿真步数
            goal_tolerance: 到达终点的容差 (m)
        
        Returns:
            (trajectory, info):
                - trajectory: 轨迹数组 (N, 4)
                - info: 仿真信息字典
        """
        state = initial_state.copy()
        trajectory = [state.copy()]
        
        goal = ref_path[-1, :2]  # 路径终点
        
        for step in range(max_steps):
            # 计算控制
            steer = self.controller.control(state, ref_path)
            
            # 执行控制（假设速度控制为匀速）
            control = np.array([steer, 0.0])  # [转向角, 加速度]
            state = self.vehicle.step(state, control, self.dt)
            
            # 记录轨迹
            trajectory.append(state.copy())
            
            # 检查是否到达终点
            dist_to_goal = np.linalg.norm(state[:2] - goal)
            if dist_to_goal < goal_tolerance:
                break
        
        # 收集统计信息
        info = {
            'steps': len(trajectory),
            'reached_goal': dist_to_goal < goal_tolerance,
            'final_dist_to_goal': dist_to_goal,
            **self.controller.get_statistics()
        }
        
        return np.array(trajectory), info


# ===== 测试代码 =====

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    print("="*60)
    print("Pure Pursuit控制器测试")
    print("="*60)
    
    # 创建车辆模型
    vehicle = BicycleModel(L=2.7)
    
    # 创建控制器
    controller = PurePursuitController(
        wheelbase=2.7,
        k_lookahead=1.0,
        ld_min=3.0
    )
    
    # 创建仿真器
    simulator = PathFollowingSimulator(controller, vehicle, dt=0.1)
    
    # 创建参考路径（圆形）
    print("\n创建圆形参考路径...")
    t = np.linspace(0, 2*np.pi, 100)
    radius = 10.0
    ref_path = np.column_stack([
        radius * np.cos(t),
        radius * np.sin(t),
    ])
    
    # 初始状态（在圆上但有横向偏差）
    initial_state = np.array([radius + 2.0, 0, 0, 3.0])  # [x, y, θ, v=3m/s]
    
    # 执行仿真
    print("\n执行仿真...")
    trajectory, info = simulator.simulate(initial_state, ref_path, max_steps=500)
    
    # 打印统计信息
    print(f"\n仿真结果:")
    print(f"  仿真步数: {info['steps']}")
    print(f"  到达终点: {'是' if info['reached_goal'] else '否'}")
    print(f"  最终距离: {info['final_dist_to_goal']:.2f} m")
    print(f"  平均横向误差: {info['mean_lateral_error']:.3f} m")
    print(f"  最大横向误差: {info['max_lateral_error']:.3f} m")
    print(f"  平均转向角: {np.rad2deg(info['mean_steer']):.2f}°")
    print(f"  最大转向角: {np.rad2deg(info['max_steer']):.2f}°")
    
    # 可视化
    print("\n生成可视化...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # 子图1: 轨迹对比
    ax1 = axes[0, 0]
    ax1.plot(ref_path[:, 0], ref_path[:, 1], 'b--', linewidth=2, label='参考路径', alpha=0.7)
    ax1.plot(trajectory[:, 0], trajectory[:, 1], 'r-', linewidth=2, label='实际轨迹')
    ax1.scatter(initial_state[0], initial_state[1], c='green', s=150, marker='o', label='起点', zorder=5)
    ax1.scatter(ref_path[-1, 0], ref_path[-1, 1], c='red', s=150, marker='*', label='终点', zorder=5)
    
    # 绘制车辆姿态
    step = len(trajectory) // 15
    for i in range(0, len(trajectory), step):
        x, y, theta, v = trajectory[i]
        dx = np.cos(theta) * 1.5
        dy = np.sin(theta) * 1.5
        ax1.arrow(x, y, dx, dy, head_width=0.6, head_length=0.4, fc='blue', ec='blue', alpha=0.5)
    
    ax1.set_xlabel('X (m)', fontsize=12)
    ax1.set_ylabel('Y (m)', fontsize=12)
    ax1.set_title('路径跟踪结果', fontsize=14)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    
    # 子图2: 横向误差
    ax2 = axes[0, 1]
    time = np.arange(len(controller.lateral_errors)) * 0.1
    ax2.plot(time, controller.lateral_errors, 'b-', linewidth=2)
    ax2.axhline(y=np.mean(controller.lateral_errors), color='r', linestyle='--', 
                label=f'平均: {np.mean(controller.lateral_errors):.3f}m')
    ax2.set_xlabel('时间 (s)', fontsize=12)
    ax2.set_ylabel('横向误差 (m)', fontsize=12)
    ax2.set_title('横向误差变化', fontsize=14)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 子图3: 转向角
    ax3 = axes[1, 0]
    time = np.arange(len(controller.control_history)) * 0.1
    ax3.plot(time, np.rad2deg(controller.control_history), 'g-', linewidth=2)
    ax3.axhline(y=np.rad2deg(controller.max_steer), color='r', linestyle='--', label='最大转向角')
    ax3.axhline(y=-np.rad2deg(controller.max_steer), color='r', linestyle='--')
    ax3.set_xlabel('时间 (s)', fontsize=12)
    ax3.set_ylabel('转向角 (°)', fontsize=12)
    ax3.set_title('转向控制', fontsize=14)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # 子图4: 速度
    ax4 = axes[1, 1]
    time = np.arange(len(trajectory)) * 0.1
    ax4.plot(time, trajectory[:, 3], 'm-', linewidth=2)
    ax4.set_xlabel('时间 (s)', fontsize=12)
    ax4.set_ylabel('速度 (m/s)', fontsize=12)
    ax4.set_title('速度曲线', fontsize=14)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('pure_pursuit_test.png', dpi=150, bbox_inches='tight')
    print("  已保存图片: pure_pursuit_test.png")
    plt.show()
    
    print("\n" + "="*60)


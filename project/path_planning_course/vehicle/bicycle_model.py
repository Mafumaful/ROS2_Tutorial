"""
第2课: 车辆运动学模型

这个文件实现了自行车运动学模型(Bicycle Kinematic Model)，
用于模拟车辆的运动行为。

核心概念:
1. 自行车模型: 将四轮车简化为前后两个轮子
2. 状态变量: [x, y, θ, v]
   - (x, y): 车辆位置
   - θ: 航向角（车头朝向）
   - v: 速度
3. 控制输入: [δ, a]
   - δ: 前轮转向角
   - a: 加速度

运动学方程:
    ẋ = v·cos(θ)
    ẏ = v·sin(θ)
    θ̇ = v·tan(δ)/L
    v̇ = a

作者: Path Planning Course Team
"""

import numpy as np
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class VehicleState:
    """
    车辆状态类
    
    属性:
        x: X坐标 (m)
        y: Y坐标 (m)
        theta: 航向角 (rad)
        v: 速度 (m/s)
    """
    x: float
    y: float
    theta: float
    v: float
    
    def to_array(self) -> np.ndarray:
        """转换为numpy数组"""
        return np.array([self.x, self.y, self.theta, self.v])
    
    @staticmethod
    def from_array(arr: np.ndarray) -> 'VehicleState':
        """从numpy数组创建"""
        return VehicleState(x=arr[0], y=arr[1], theta=arr[2], v=arr[3])
    
    def __str__(self) -> str:
        return f"VehicleState(x={self.x:.2f}, y={self.y:.2f}, θ={np.rad2deg(self.theta):.1f}°, v={self.v:.2f})"


class BicycleModel:
    """
    自行车运动学模型
    
    这个类实现了车辆的运动学模拟，包括:
    - 状态更新（前向仿真）
    - 物理约束检查
    - 最小转弯半径计算
    
    使用方法:
        >>> vehicle = BicycleModel(L=2.7)
        >>> state = np.array([0, 0, 0, 2.0])  # [x, y, θ, v]
        >>> control = [np.deg2rad(10), 0.5]   # [δ, a]
        >>> new_state = vehicle.step(state, control, dt=0.1)
    """
    
    def __init__(
        self,
        L: float = 2.7,
        delta_max: float = np.deg2rad(35),
        v_max: float = 5.0,
        a_max: float = 2.0
    ):
        """
        初始化车辆模型
        
        Args:
            L: 轴距(前后轮距离) (m)，典型值: 2.7m
            delta_max: 最大转向角 (rad)，典型值: 35°
            v_max: 最大速度 (m/s)，典型值: 5 m/s
            a_max: 最大加速度 (m/s²)，典型值: 2 m/s²
        
        注意:
            - 轿车轴距通常在2.5-3.0m
            - 卡车轴距可达4-6m
            - 转向角越大，转弯半径越小
        """
        self.L = L
        self.delta_max = delta_max
        self.v_max = v_max
        self.a_max = a_max
        
        # 计算最小转弯半径
        self.R_min = self.calc_min_turning_radius()
        
        print(f"[车辆模型] 初始化完成")
        print(f"  轴距 L = {L:.2f} m")
        print(f"  最大转向角 = {np.rad2deg(delta_max):.1f}°")
        print(f"  最大速度 = {v_max:.2f} m/s")
        print(f"  最小转弯半径 = {self.R_min:.2f} m")
    
    def calc_min_turning_radius(self) -> float:
        """
        计算最小转弯半径
        
        公式: R_min = L / tan(δ_max)
        
        Returns:
            最小转弯半径 (m)
        
        物理意义:
            - 转弯半径越小，车辆机动性越好
            - 受轴距和最大转向角限制
            - 泊车等场景需要较小的转弯半径
        """
        if abs(self.delta_max) < 1e-6:
            return float('inf')
        return self.L / np.tan(self.delta_max)
    
    def normalize_angle(self, angle: float) -> float:
        """
        将角度归一化到 [-π, π] 范围
        
        Args:
            angle: 任意角度 (rad)
        
        Returns:
            归一化后的角度 (rad)
        
        为什么需要归一化:
            - 避免角度累积超出范围
            - 保持数值稳定性
            - 便于角度比较和显示
        """
        return np.arctan2(np.sin(angle), np.cos(angle))
    
    def step(
        self, 
        state: np.ndarray, 
        control: np.ndarray, 
        dt: float = 0.1
    ) -> np.ndarray:
        """
        执行一步仿真，更新车辆状态
        
        使用欧拉法进行离散化积分:
            x[k+1] = x[k] + ẋ·Δt
        
        Args:
            state: 当前状态 [x, y, θ, v]
            control: 控制输入 [δ, a]
            dt: 时间步长 (s)，典型值: 0.1s (10Hz)
        
        Returns:
            new_state: 新状态 [x', y', θ', v']
        
        运动学方程:
            ẋ = v·cos(θ)          # X方向速度分量
            ẏ = v·sin(θ)          # Y方向速度分量
            θ̇ = v·tan(δ)/L        # 角速度
            v̇ = a                 # 加速度
        
        注意:
            - 使用欧拉法时，dt不宜过大（建议≤0.1s）
            - 控制输入会被限制在物理约束范围内
            - 速度为负值时，车辆后退
        """
        # 解包状态和控制
        x, y, theta, v = state
        delta, a = control
        
        # ===== 1. 约束控制输入 =====
        # 限制转向角在 [-δ_max, δ_max] 范围内
        delta = np.clip(delta, -self.delta_max, self.delta_max)
        
        # 限制加速度在 [-a_max, a_max] 范围内
        a = np.clip(a, -self.a_max, self.a_max)
        
        # ===== 2. 应用运动学方程 =====
        # 计算速度分量
        x_dot = v * np.cos(theta)  # X方向速度
        y_dot = v * np.sin(theta)  # Y方向速度
        
        # 计算角速度
        # 注意: tan(δ) 在 δ接近±90°时会发散，但物理约束保证 |δ| ≤ 35°
        theta_dot = v * np.tan(delta) / self.L
        
        # 计算加速度（直接等于控制输入）
        v_dot = a
        
        # ===== 3. 数值积分（欧拉法）=====
        x_new = x + x_dot * dt
        y_new = y + y_dot * dt
        theta_new = theta + theta_dot * dt
        v_new = v + v_dot * dt
        
        # ===== 4. 约束状态 =====
        # 限制速度在 [0, v_max] 范围内（不允许负速度，即倒车）
        # 如果需要支持倒车，可以改为 [-v_max, v_max]
        v_new = np.clip(v_new, 0, self.v_max)
        
        # 归一化角度到 [-π, π]
        theta_new = self.normalize_angle(theta_new)
        
        return np.array([x_new, y_new, theta_new, v_new])
    
    def step_with_reverse(
        self, 
        state: np.ndarray, 
        control: np.ndarray, 
        dt: float = 0.1,
        direction: int = 1
    ) -> np.ndarray:
        """
        支持前进/后退的仿真步骤
        
        Args:
            state: 当前状态 [x, y, θ, v]
            control: 控制输入 [δ, a]
            dt: 时间步长 (s)
            direction: +1表示前进, -1表示后退
        
        Returns:
            new_state: 新状态 [x', y', θ', v']
        
        用途:
            - 泊车场景需要后退
            - 狭窄空间的机动
        """
        # 调整速度方向
        state_copy = state.copy()
        state_copy[3] *= direction  # v → ±v
        
        # 执行正常step
        new_state = self.step(state_copy, control, dt)
        
        # 恢复速度符号
        new_state[3] = abs(new_state[3])
        
        return new_state
    
    def simulate_trajectory(
        self,
        initial_state: np.ndarray,
        controls: List[np.ndarray],
        dt: float = 0.1
    ) -> np.ndarray:
        """
        模拟整条轨迹
        
        Args:
            initial_state: 初始状态 [x, y, θ, v]
            controls: 控制序列 [(δ₁, a₁), (δ₂, a₂), ...]
            dt: 时间步长 (s)
        
        Returns:
            trajectory: 轨迹数组，形状为 (N+1, 4)
                       第一行是初始状态，后续是每一步的状态
        
        示例:
            >>> controls = [
            ...     [np.deg2rad(10), 0.5],  # 右转，加速
            ...     [np.deg2rad(10), 0.0],  # 右转，匀速
            ...     [0, -0.5],              # 直行，减速
            ... ]
            >>> traj = vehicle.simulate_trajectory(init_state, controls)
        """
        trajectory = [initial_state.copy()]
        state = initial_state.copy()
        
        for control in controls:
            state = self.step(state, control, dt)
            trajectory.append(state.copy())
        
        return np.array(trajectory)
    
    def calc_turning_radius(self, delta: float) -> float:
        """
        计算给定转向角下的转弯半径
        
        Args:
            delta: 转向角 (rad)
        
        Returns:
            转弯半径 (m)
        
        公式: R = L / tan(δ)
        
        特殊情况:
            - δ = 0: R = ∞ (直线行驶)
            - δ = ±δ_max: R = R_min (最小转弯半径)
        """
        if abs(delta) < 1e-6:
            return float('inf')
        return abs(self.L / np.tan(delta))


# ===== 可视化辅助函数 =====

def plot_vehicle(
    ax,
    state: np.ndarray,
    L: float = 2.7,
    width: float = 1.5,
    color: str = 'blue'
):
    """
    在matplotlib图上绘制车辆
    
    Args:
        ax: matplotlib坐标轴
        state: 车辆状态 [x, y, θ, v]
        L: 轴距 (m)
        width: 车辆宽度 (m)
        color: 颜色
    
    绘制内容:
        - 车身矩形
        - 车头三角形（指示方向）
        - 前后轮位置
    """
    x, y, theta, v = state
    
    # 车身尺寸
    length = L * 1.2  # 车身长度略大于轴距
    
    # 计算车身四个角点（车辆坐标系）
    corners = np.array([
        [-length/2, -width/2],  # 左后
        [length/2, -width/2],   # 右后
        [length/2, width/2],    # 右前
        [-length/2, width/2],   # 左前
        [-length/2, -width/2],  # 闭合
    ])
    
    # 旋转并平移到世界坐标系
    c, s = np.cos(theta), np.sin(theta)
    rotation = np.array([[c, -s], [s, c]])
    corners_world = corners @ rotation.T + np.array([x, y])
    
    # 绘制车身
    ax.plot(corners_world[:, 0], corners_world[:, 1], color=color, linewidth=2)
    ax.fill(corners_world[:, 0], corners_world[:, 1], color=color, alpha=0.3)
    
    # 绘制车头方向（三角形）
    triangle = np.array([
        [length/2, 0],
        [length/4, width/4],
        [length/4, -width/4],
    ])
    triangle_world = triangle @ rotation.T + np.array([x, y])
    ax.fill(triangle_world[:, 0], triangle_world[:, 1], color='red', alpha=0.8)


# ===== 测试代码 =====

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    print("="*60)
    print("车辆运动学模型测试")
    print("="*60)
    
    # 创建车辆模型
    vehicle = BicycleModel(L=2.7)
    
    print("\n测试1: 直线行驶")
    print("-" * 40)
    state = np.array([0, 0, 0, 2.0])  # 初速度2 m/s
    control = [0, 0]  # 不转向，不加速
    
    trajectory = []
    for i in range(50):
        trajectory.append(state.copy())
        state = vehicle.step(state, control, dt=0.1)
        if i % 10 == 0:
            print(f"  t={i*0.1:.1f}s: {VehicleState.from_array(state)}")
    
    trajectory = np.array(trajectory)
    
    print("\n测试2: 圆周运动（右转）")
    print("-" * 40)
    state = np.array([0, 0, 0, 2.0])
    control = [np.deg2rad(20), 0]  # 右转20°
    
    trajectory_circle = []
    for i in range(100):
        trajectory_circle.append(state.copy())
        state = vehicle.step(state, control, dt=0.1)
        if i % 20 == 0:
            print(f"  t={i*0.1:.1f}s: {VehicleState.from_array(state)}")
    
    trajectory_circle = np.array(trajectory_circle)
    
    # 计算实际转弯半径
    R_actual = vehicle.calc_turning_radius(np.deg2rad(20))
    print(f"\n  理论转弯半径: {R_actual:.2f} m")
    
    print("\n测试3: 可视化")
    print("-" * 40)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 子图1: 直线运动
    ax1 = axes[0]
    ax1.plot(trajectory[:, 0], trajectory[:, 1], 'b-', linewidth=2, label='轨迹')
    ax1.scatter(trajectory[0, 0], trajectory[0, 1], c='green', s=100, label='起点', zorder=5)
    ax1.scatter(trajectory[-1, 0], trajectory[-1, 1], c='red', s=100, label='终点', zorder=5)
    
    # 绘制几个车辆姿态
    for i in [0, 15, 30, 45]:
        plot_vehicle(ax1, trajectory[i], L=2.7, color='blue')
    
    ax1.set_xlabel('X (m)', fontsize=12)
    ax1.set_ylabel('Y (m)', fontsize=12)
    ax1.set_title('测试1: 直线行驶', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    
    # 子图2: 圆周运动
    ax2 = axes[1]
    ax2.plot(trajectory_circle[:, 0], trajectory_circle[:, 1], 'b-', linewidth=2, label='轨迹')
    ax2.scatter(trajectory_circle[0, 0], trajectory_circle[0, 1], c='green', s=100, label='起点', zorder=5)
    
    # 绘制几个车辆姿态
    for i in [0, 25, 50, 75]:
        plot_vehicle(ax2, trajectory_circle[i], L=2.7, color='blue')
    
    # 绘制理论圆心
    cx, cy = 0, -R_actual
    circle = plt.Circle((cx, cy), R_actual, fill=False, color='red', linestyle='--', label=f'理论圆 (R={R_actual:.1f}m)')
    ax2.add_patch(circle)
    
    ax2.set_xlabel('X (m)', fontsize=12)
    ax2.set_ylabel('Y (m)', fontsize=12)
    ax2.set_title('测试2: 圆周运动 (δ=20°)', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.axis('equal')
    
    plt.tight_layout()
    plt.savefig('vehicle_model_test.png', dpi=150, bbox_inches='tight')
    print("  已保存图片: vehicle_model_test.png")
    plt.show()
    
    print("\n" + "="*60)


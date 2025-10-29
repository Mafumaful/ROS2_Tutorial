"""
第4课: 模型预测控制(MPC)路径跟踪控制器

MPC是基于优化的先进控制方法。

核心思想:
1. 预测: 使用车辆模型预测未来N步的状态
2. 优化: 求解最小化跟踪误差和控制代价的优化问题
3. 执行: 只执行第一步控制
4. 重复: 滚动时域,不断重新优化

优势:
- 可以处理多约束（速度、加速度、转向角等）
- 可以同时优化多个目标
- 预测未来，提前规划
- 鲁棒性强

优化问题:
    min  Σ ||x[k] - x_ref[k]||²_Q + ||u[k]||²_R
    s.t. x[k+1] = f(x[k], u[k])
         u_min ≤ u[k] ≤ u_max
         x_min ≤ x[k] ≤ x_max

作者: Path Planning Course Team
"""

import numpy as np
import cvxpy as cp
from typing import Tuple, Optional
import sys
sys.path.append('..')
from vehicle.bicycle_model import BicycleModel


class MPCController:
    """
    模型预测控制器
    
    实现线性时变MPC (Linear Time-Varying MPC)
    
    特点:
    - 在参考轨迹附近线性化
    - 使用凸优化求解(CVXPY)
    - 支持状态和控制约束
    
    使用方法:
        >>> controller = MPCController(wheelbase=2.7, horizon=10)
        >>> ref_traj = ...  # (N, 4) 参考轨迹
        >>> control = controller.control(current_state, ref_traj)
    """
    
    def __init__(
        self,
        wheelbase: float = 2.7,
        dt: float = 0.1,
        horizon: int = 10,
        Q: Optional[np.ndarray] = None,
        R: Optional[np.ndarray] = None,
        Qf: Optional[np.ndarray] = None
    ):
        """
        初始化MPC控制器
        
        Args:
            wheelbase: 车辆轴距 (m)
            dt: 离散时间步长 (s)
            horizon: 预测时域长度（预测多少步）
            Q: 状态跟踪权重矩阵 (4×4)
            R: 控制代价权重矩阵 (2×2)
            Qf: 终端状态权重矩阵 (4×4)
        
        权重矩阵设计原则:
            Q: 对角矩阵，[q_x, q_y, q_θ, q_v]
                - q_x, q_y: 位置跟踪权重（通常1.0-10.0）
                - q_θ: 航向跟踪权重（通常0.5-2.0）
                - q_v: 速度跟踪权重（通常0.1-1.0）
            
            R: 对角矩阵，[r_δ, r_a]
                - r_δ: 转向角代价（通常0.01-0.1）
                - r_a: 加速度代价（通常0.01-0.1）
            
            Qf: 终端权重，通常是Q的放大（例如10×Q）
        """
        self.L = wheelbase
        self.dt = dt
        self.N = horizon
        
        # 默认权重矩阵
        if Q is None:
            Q = np.diag([1.0, 1.0, 0.5, 0.1])  # [x, y, θ, v]
        if R is None:
            R = np.diag([0.1, 0.1])            # [δ, a]
        if Qf is None:
            Qf = 10 * Q                        # 终端权重
        
        self.Q = Q
        self.R = R
        self.Qf = Qf
        
        # 物理约束
        self.max_steer = np.deg2rad(35)  # 最大转向角
        self.max_accel = 2.0             # 最大加速度
        self.max_speed = 5.0             # 最大速度
        self.min_speed = 0.0             # 最小速度（不支持倒车）
        
        # 车辆模型（用于线性化）
        self.vehicle = BicycleModel(L=wheelbase)
        
        # 统计信息
        self.solve_times = []
        
        print(f"[MPC] 初始化完成")
        print(f"  轴距 L = {wheelbase:.2f} m")
        print(f"  时间步长 dt = {dt:.2f} s")
        print(f"  预测时域 N = {horizon}")
        print(f"  状态权重 Q = diag({np.diag(Q)})")
        print(f"  控制权重 R = diag({np.diag(R)})")
    
    def linearize(
        self,
        x_ref: np.ndarray,
        u_ref: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        在参考点附近线性化动力学模型
        
        非线性模型:
            x[k+1] = f(x[k], u[k])
        
        线性化:
            x[k+1] ≈ f(x̄, ū) + A(x[k] - x̄) + B(u[k] - ū)
            
        其中:
            A = ∂f/∂x |_(x̄, ū)  # 状态雅可比矩阵
            B = ∂f/∂u |_(x̄, ū)  # 控制雅可比矩阵
        
        Args:
            x_ref: 参考状态 [x, y, θ, v]
            u_ref: 参考控制 [δ, a]
        
        Returns:
            (A, B): 线性化系统矩阵
        
        数学推导:
            对于车辆模型:
                ẋ = v·cos(θ)
                ẏ = v·sin(θ)
                θ̇ = v·tan(δ)/L
                v̇ = a
            
            离散化后求偏导数得到A和B
        """
        x, y, theta, v = x_ref
        delta, a = u_ref
        
        # 状态雅可比矩阵 A = ∂f/∂x
        # 4×4 矩阵
        A = np.array([
            [1, 0, -v*np.sin(theta)*self.dt, np.cos(theta)*self.dt],
            [0, 1,  v*np.cos(theta)*self.dt, np.sin(theta)*self.dt],
            [0, 0, 1, np.tan(delta)/self.L*self.dt],
            [0, 0, 0, 1]
        ])
        
        # 控制雅可比矩阵 B = ∂f/∂u
        # 4×2 矩阵
        B = np.array([
            [0, 0],
            [0, 0],
            [v/(self.L*np.cos(delta)**2)*self.dt, 0],
            [0, self.dt]
        ])
        
        return A, B
    
    def predict_reference(
        self,
        x0: np.ndarray,
        u_ref: np.ndarray
    ) -> np.ndarray:
        """
        使用参考控制预测未来状态
        
        用于生成线性化的参考轨迹
        
        Args:
            x0: 初始状态 [x, y, θ, v]
            u_ref: 参考控制序列 (N, 2)
        
        Returns:
            x_ref: 参考状态序列 (N+1, 4)
        """
        x_ref = np.zeros((self.N+1, 4))
        x_ref[0] = x0
        
        for k in range(self.N):
            # 使用车辆模型仿真
            x_ref[k+1] = self.vehicle.step(x_ref[k], u_ref[k], self.dt)
        
        return x_ref
    
    def solve_mpc(
        self,
        x0: np.ndarray,
        x_ref_seq: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        求解MPC优化问题
        
        优化问题:
            min  Σ[k=0 to N-1] { ||x[k]-x_ref[k]||²_Q + ||u[k]||²_R }
            u    + ||x[N]-x_ref[N]||²_Qf
            
            s.t. x[k+1] = A[k]·x[k] + B[k]·u[k] + c[k]  (线性化动力学)
                 u_min ≤ u[k] ≤ u_max                    (控制约束)
                 x_min ≤ x[k] ≤ x_max                    (状态约束)
        
        Args:
            x0: 当前状态 [x, y, θ, v]
            x_ref_seq: 参考轨迹 (N+1, 4)
        
        Returns:
            u_opt: 最优控制序列 (N, 2) 或 None(求解失败)
        
        求解器:
            使用CVXPY + OSQP求解二次规划(QP)问题
        """
        import time
        start_time = time.time()
        
        # 决策变量
        x = cp.Variable((self.N+1, 4))  # 状态序列
        u = cp.Variable((self.N, 2))    # 控制序列
        
        # 目标函数
        cost = 0
        
        # 阶段代价
        for k in range(self.N):
            # 状态跟踪误差
            dx = x[k] - x_ref_seq[k]
            cost += cp.quad_form(dx, self.Q)
            
            # 控制代价
            cost += cp.quad_form(u[k], self.R)
        
        # 终端代价
        dx_final = x[self.N] - x_ref_seq[self.N]
        cost += cp.quad_form(dx_final, self.Qf)
        
        # 约束条件
        constraints = []
        
        # 初始条件
        constraints.append(x[0] == x0)
        
        # 动力学约束（线性化）
        u_ref = np.zeros((self.N, 2))  # 参考控制（简化为0）
        x_pred = self.predict_reference(x0, u_ref)
        
        for k in range(self.N):
            # 线性化
            A, B = self.linearize(x_pred[k], u_ref[k])
            
            # 线性化动力学: x[k+1] = x_pred[k+1] + A(x[k] - x_pred[k]) + B(u[k] - u_ref[k])
            constraints.append(
                x[k+1] == x_pred[k+1] + A @ (x[k] - x_pred[k]) + B @ (u[k] - u_ref[k])
            )
        
        # 控制约束
        for k in range(self.N):
            constraints.append(u[k, 0] <= self.max_steer)   # δ ≤ δ_max
            constraints.append(u[k, 0] >= -self.max_steer)  # δ ≥ -δ_max
            constraints.append(u[k, 1] <= self.max_accel)   # a ≤ a_max
            constraints.append(u[k, 1] >= -self.max_accel)  # a ≥ -a_max
        
        # 状态约束
        for k in range(self.N+1):
            constraints.append(x[k, 3] <= self.max_speed)  # v ≤ v_max
            constraints.append(x[k, 3] >= self.min_speed)  # v ≥ 0
        
        # 构建并求解优化问题
        problem = cp.Problem(cp.Minimize(cost), constraints)
        
        try:
            problem.solve(solver=cp.OSQP, verbose=False, warm_start=True)
            
            if problem.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
                solve_time = time.time() - start_time
                self.solve_times.append(solve_time)
                return u.value
            else:
                print(f"[MPC] 优化失败: {problem.status}")
                return None
                
        except Exception as e:
            print(f"[MPC] 求解异常: {e}")
            return None
    
    def control(
        self,
        vehicle_state: np.ndarray,
        ref_trajectory: np.ndarray
    ) -> np.ndarray:
        """
        MPC控制主函数
        
        Args:
            vehicle_state: 当前状态 [x, y, θ, v]
            ref_trajectory: 参考轨迹 (M, 4)，M ≥ N+1
        
        Returns:
            control: 控制输入 [δ, a]
        
        工作流程:
        1. 检查参考轨迹长度
        2. 提取预测时域内的参考轨迹
        3. 求解MPC优化问题
        4. 返回第一个控制输入
        """
        # 确保参考轨迹足够长
        if len(ref_trajectory) < self.N+1:
            # 如果不够，用最后一个点填充
            last_point = ref_trajectory[-1]
            padding = np.tile(last_point, (self.N+1-len(ref_trajectory), 1))
            ref_trajectory = np.vstack([ref_trajectory, padding])
        
        # 提取前N+1个点
        x_ref_seq = ref_trajectory[:self.N+1]
        
        # 求解MPC
        u_opt = self.solve_mpc(vehicle_state, x_ref_seq)
        
        if u_opt is None:
            # 求解失败，返回零控制
            print("[MPC] 警告: 返回零控制")
            return np.array([0.0, 0.0])
        
        # 返回第一个控制（滚动时域原理）
        return u_opt[0]
    
    def get_statistics(self) -> dict:
        """获取求解统计信息"""
        if not self.solve_times:
            return {}
        
        return {
            'mean_solve_time': np.mean(self.solve_times),
            'max_solve_time': np.max(self.solve_times),
            'total_solves': len(self.solve_times),
        }


# ===== 测试代码 =====

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    print("="*60)
    print("MPC控制器测试")
    print("="*60)
    
    # 创建车辆模型
    vehicle = BicycleModel(L=2.7)
    
    # 创建MPC控制器
    controller = MPCController(
        wheelbase=2.7,
        dt=0.1,
        horizon=10,
        Q=np.diag([1.0, 1.0, 0.5, 0.1]),
        R=np.diag([0.1, 0.1]),
    )
    
    # 创建参考轨迹（直线 + 圆弧）
    print("\n创建参考轨迹...")
    
    # 直线段
    straight = np.column_stack([
        np.linspace(0, 10, 50),
        np.zeros(50),
        np.zeros(50),
        2.0 * np.ones(50)
    ])
    
    # 圆弧段
    t = np.linspace(0, np.pi/2, 50)
    radius = 5.0
    arc = np.column_stack([
        10 + radius * np.sin(t),
        radius * (1 - np.cos(t)),
        t,
        2.0 * np.ones(50)
    ])
    
    ref_traj = np.vstack([straight, arc])
    
    # 初始状态（有偏差）
    initial_state = np.array([0.0, 2.0, 0.1, 2.0])  # [x, y, θ, v]
    
    # 仿真
    print("\n执行仿真...")
    state = initial_state.copy()
    trajectory = [state.copy()]
    controls = []
    
    max_steps = len(ref_traj) - controller.N - 1
    
    for step in range(max_steps):
        # MPC控制
        control = controller.control(state, ref_traj[step:])
        
        # 执行控制
        state = vehicle.step(state, control, dt=0.1)
        
        # 记录
        trajectory.append(state.copy())
        controls.append(control)
        
        # 打印进度
        if step % 20 == 0:
            print(f"  步骤 {step}/{max_steps}...", end='\r')
    
    trajectory = np.array(trajectory)
    controls = np.array(controls)
    
    print(f"\n\n仿真完成! 共 {len(trajectory)} 步")
    
    # 计算跟踪误差
    lateral_errors = []
    for i in range(len(trajectory)):
        if i < len(ref_traj):
            error = np.linalg.norm(trajectory[i, :2] - ref_traj[i, :2])
            lateral_errors.append(error)
    
    print(f"\n跟踪性能:")
    print(f"  平均横向误差: {np.mean(lateral_errors):.3f} m")
    print(f"  最大横向误差: {np.max(lateral_errors):.3f} m")
    
    stats = controller.get_statistics()
    if stats:
        print(f"\n求解性能:")
        print(f"  平均求解时间: {stats['mean_solve_time']*1000:.2f} ms")
        print(f"  最大求解时间: {stats['max_solve_time']*1000:.2f} ms")
        print(f"  总求解次数: {stats['total_solves']}")
    
    # 可视化
    print("\n生成可视化...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # 子图1: 轨迹
    ax1 = axes[0, 0]
    ax1.plot(ref_traj[:, 0], ref_traj[:, 1], 'b--', linewidth=2, label='参考轨迹', alpha=0.7)
    ax1.plot(trajectory[:, 0], trajectory[:, 1], 'r-', linewidth=2, label='MPC跟踪')
    ax1.scatter(initial_state[0], initial_state[1], c='green', s=150, marker='o', label='起点', zorder=5)
    
    # 绘制车辆姿态
    step = len(trajectory) // 15
    for i in range(0, len(trajectory), step):
        x, y, theta, v = trajectory[i]
        dx = np.cos(theta) * 1.5
        dy = np.sin(theta) * 1.5
        ax1.arrow(x, y, dx, dy, head_width=0.5, head_length=0.3, fc='blue', ec='blue', alpha=0.5)
    
    ax1.set_xlabel('X (m)', fontsize=12)
    ax1.set_ylabel('Y (m)', fontsize=12)
    ax1.set_title('MPC轨迹跟踪', fontsize=14)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    
    # 子图2: 横向误差
    ax2 = axes[0, 1]
    time = np.arange(len(lateral_errors)) * 0.1
    ax2.plot(time, lateral_errors, 'b-', linewidth=2)
    ax2.axhline(y=np.mean(lateral_errors), color='r', linestyle='--', 
                label=f'平均: {np.mean(lateral_errors):.3f}m')
    ax2.set_xlabel('时间 (s)', fontsize=12)
    ax2.set_ylabel('横向误差 (m)', fontsize=12)
    ax2.set_title('横向跟踪误差', fontsize=14)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 子图3: 转向角
    ax3 = axes[1, 0]
    time = np.arange(len(controls)) * 0.1
    ax3.plot(time, np.rad2deg(controls[:, 0]), 'g-', linewidth=2)
    ax3.axhline(y=35, color='r', linestyle='--', alpha=0.5, label='约束边界')
    ax3.axhline(y=-35, color='r', linestyle='--', alpha=0.5)
    ax3.set_xlabel('时间 (s)', fontsize=12)
    ax3.set_ylabel('转向角 (°)', fontsize=12)
    ax3.set_title('转向控制', fontsize=14)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # 子图4: 加速度
    ax4 = axes[1, 1]
    time = np.arange(len(controls)) * 0.1
    ax4.plot(time, controls[:, 1], 'm-', linewidth=2)
    ax4.axhline(y=2.0, color='r', linestyle='--', alpha=0.5, label='约束边界')
    ax4.axhline(y=-2.0, color='r', linestyle='--', alpha=0.5)
    ax4.set_xlabel('时间 (s)', fontsize=12)
    ax4.set_ylabel('加速度 (m/s²)', fontsize=12)
    ax4.set_title('加速度控制', fontsize=14)
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('mpc_test.png', dpi=150, bbox_inches='tight')
    print("  已保存图片: mpc_test.png")
    plt.show()
    
    print("\n" + "="*60)


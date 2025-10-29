"""
可视化工具模块

提供各种绘图和动画功能
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow
from matplotlib.animation import FuncAnimation
from typing import Optional, List


def plot_grid_map(
    grid: np.ndarray,
    start: Optional[tuple] = None,
    goal: Optional[tuple] = None,
    path: Optional[np.ndarray] = None,
    title: str = "Grid Map",
    ax: Optional[plt.Axes] = None
) -> plt.Axes:
    """
    绘制网格地图
    
    Args:
        grid: 网格地图 (0=空闲, 1=障碍物)
        start: 起点坐标 (x, y)
        goal: 终点坐标 (x, y)
        path: 路径数组
        title: 标题
        ax: matplotlib axes对象
    
    Returns:
        ax: axes对象
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
    
    # 绘制网格
    ax.imshow(grid, origin='lower', cmap='binary', alpha=0.5)
    
    # 绘制路径
    if path is not None:
        ax.plot(path[:, 0], path[:, 1], 'b-', linewidth=2, label='路径')
    
    # 绘制起点和终点
    if start is not None:
        ax.scatter(start[0], start[1], c='green', s=200, marker='o', 
                  label='起点', zorder=5, edgecolors='black', linewidths=2)
    if goal is not None:
        ax.scatter(goal[0], goal[1], c='red', s=200, marker='*', 
                  label='终点', zorder=5, edgecolors='black', linewidths=2)
    
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    
    return ax


def plot_path(
    path: np.ndarray,
    ref_path: Optional[np.ndarray] = None,
    title: str = "Path",
    ax: Optional[plt.Axes] = None
) -> plt.Axes:
    """
    绘制路径
    
    Args:
        path: 规划的路径
        ref_path: 参考路径
        title: 标题
        ax: axes对象
    
    Returns:
        ax: axes对象
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    # 参考路径
    if ref_path is not None:
        ax.plot(ref_path[:, 0], ref_path[:, 1], 'b--', 
               linewidth=2, alpha=0.7, label='参考路径')
    
    # 实际路径
    ax.plot(path[:, 0], path[:, 1], 'r-', linewidth=2, label='实际路径')
    
    # 起点和终点
    ax.scatter(path[0, 0], path[0, 1], c='green', s=150, 
              marker='o', label='起点', zorder=5)
    ax.scatter(path[-1, 0], path[-1, 1], c='red', s=150, 
              marker='*', label='终点', zorder=5)
    
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    
    return ax


def plot_trajectory(
    trajectory: np.ndarray,
    ref_path: Optional[np.ndarray] = None,
    show_heading: bool = True,
    heading_step: int = 10,
    title: str = "Trajectory",
    ax: Optional[plt.Axes] = None
) -> plt.Axes:
    """
    绘制轨迹（包含航向角）
    
    Args:
        trajectory: 轨迹 (N, 4) [x, y, θ, v]
        ref_path: 参考路径
        show_heading: 是否显示航向角箭头
        heading_step: 航向角箭头间隔
        title: 标题
        ax: axes对象
    
    Returns:
        ax: axes对象
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    # 参考路径
    if ref_path is not None:
        ax.plot(ref_path[:, 0], ref_path[:, 1], 'b--', 
               linewidth=2, alpha=0.7, label='参考轨迹')
    
    # 实际轨迹
    ax.plot(trajectory[:, 0], trajectory[:, 1], 'r-', linewidth=2, label='实际轨迹')
    
    # 航向角箭头
    if show_heading and trajectory.shape[1] >= 3:
        for i in range(0, len(trajectory), heading_step):
            x, y, theta = trajectory[i, :3]
            dx = np.cos(theta) * 1.0
            dy = np.sin(theta) * 1.0
            ax.arrow(x, y, dx, dy, head_width=0.4, head_length=0.3, 
                    fc='blue', ec='blue', alpha=0.6)
    
    ax.scatter(trajectory[0, 0], trajectory[0, 1], c='green', s=150, 
              marker='o', label='起点', zorder=5)
    ax.scatter(trajectory[-1, 0], trajectory[-1, 1], c='red', s=150, 
              marker='*', label='终点', zorder=5)
    
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    
    return ax


def plot_vehicle(
    ax,
    state: np.ndarray,
    L: float = 2.7,
    width: float = 1.5,
    color: str = 'blue'
):
    """
    在图上绘制车辆
    
    Args:
        ax: axes对象
        state: 车辆状态 [x, y, θ, ...]
        L: 轴距
        width: 宽度
        color: 颜色
    """
    x, y, theta = state[:3]
    
    # 车身长度
    length = L * 1.2
    
    # 车身四个角点
    corners = np.array([
        [-length/2, -width/2],
        [length/2, -width/2],
        [length/2, width/2],
        [-length/2, width/2],
        [-length/2, -width/2],
    ])
    
    # 旋转并平移
    c, s = np.cos(theta), np.sin(theta)
    rotation = np.array([[c, -s], [s, c]])
    corners_world = corners @ rotation.T + np.array([x, y])
    
    # 绘制
    ax.plot(corners_world[:, 0], corners_world[:, 1], color=color, linewidth=2)
    ax.fill(corners_world[:, 0], corners_world[:, 1], color=color, alpha=0.3)


def animate_path_following(
    trajectory: np.ndarray,
    ref_path: np.ndarray,
    filename: str = "animation.gif",
    interval: int = 50
):
    """
    创建路径跟踪动画
    
    Args:
        trajectory: 实际轨迹
        ref_path: 参考路径
        filename: 保存文件名
        interval: 帧间隔 (ms)
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 绘制参考路径
    ax.plot(ref_path[:, 0], ref_path[:, 1], 'b--', 
           linewidth=2, alpha=0.7, label='参考路径')
    
    # 初始化轨迹线
    line, = ax.plot([], [], 'r-', linewidth=2, label='实际轨迹')
    vehicle_plot = None
    
    # 设置坐标范围
    all_x = np.concatenate([trajectory[:, 0], ref_path[:, 0]])
    all_y = np.concatenate([trajectory[:, 1], ref_path[:, 1]])
    margin = 5
    ax.set_xlim(all_x.min()-margin, all_x.max()+margin)
    ax.set_ylim(all_y.min()-margin, all_y.max()+margin)
    ax.axis('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    def init():
        line.set_data([], [])
        return line,
    
    def update(frame):
        # 更新轨迹
        line.set_data(trajectory[:frame, 0], trajectory[:frame, 1])
        return line,
    
    anim = FuncAnimation(fig, update, init_func=init,
                        frames=len(trajectory), interval=interval, blit=True)
    
    anim.save(filename, writer='pillow')
    plt.close()
    print(f"动画已保存: {filename}")


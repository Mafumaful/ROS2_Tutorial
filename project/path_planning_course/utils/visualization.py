"""
可视化工具模块

提供各种绘图和动画功能
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow
from matplotlib.animation import FuncAnimation
from typing import Optional, List


class AStarStepVisualizer:
    """
    A*算法单步调试可视化工具

    使用左右方向键可以前进/后退查看算法执行的每一步
    """

    def __init__(self, planner, title="A* Algorithm Step-by-Step Visualization"):
        """
        初始化可视化工具

        Args:
            planner: 已经执行过plan(record_steps=True)的AStar对象
            title: 图表标题
        """
        self.planner = planner
        self.steps = planner.steps
        self.current_step = 0
        self.title = title

        # 创建图形
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        self.fig.canvas.manager.set_window_title('A* Step Debugger - Use ← → keys')

        # 连接键盘事件
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

        # 绘制初始状态
        self.update_plot()

    def on_key(self, event):
        """处理键盘事件"""
        if event.key == 'right' or event.key == 'd':
            # 前进一步
            if self.current_step < len(self.steps) - 1:
                self.current_step += 1
                self.update_plot()
        elif event.key == 'left' or event.key == 'a':
            # 后退一步
            if self.current_step > 0:
                self.current_step -= 1
                self.update_plot()
        elif event.key == 'home':
            # 回到开始
            self.current_step = 0
            self.update_plot()
        elif event.key == 'end':
            # 跳到结束
            self.current_step = len(self.steps) - 1
            self.update_plot()

    def update_plot(self):
        """更新图形显示"""
        self.ax.clear()

        step_data = self.steps[self.current_step]
        grid = self.planner.grid
        height, width = grid.shape

        # 创建网格边界坐标
        x_edges = np.arange(-0.5, width, 1)
        y_edges = np.arange(-0.5, height, 1)

        # 绘制网格
        self.ax.pcolormesh(x_edges, y_edges, grid, cmap='binary', alpha=0.3,
                          edgecolors='lightgray', linewidth=0.5, zorder=0)

        # 绘制Closed Set (已访问的节点)
        if step_data['closed_set']:
            closed_array = np.array(list(step_data['closed_set']))
            self.ax.scatter(closed_array[:, 0], closed_array[:, 1],
                          c='lightblue', s=200, marker='s', alpha=0.6,
                          label='Closed Set (visited)', zorder=2)

        # 绘制Open List (待扩展的节点)
        if step_data['open_list']:
            open_array = np.array(step_data['open_list'])
            self.ax.scatter(open_array[:, 0], open_array[:, 1],
                          c='yellow', s=200, marker='s', alpha=0.7,
                          label='Open List (frontier)', zorder=3, edgecolors='orange', linewidths=2)

        # 绘制当前正在扩展的节点
        if step_data['current'] is not None:
            curr = step_data['current']
            self.ax.scatter(curr[0], curr[1], c='orange', s=300, marker='*',
                          label='Current Node', zorder=4, edgecolors='red', linewidths=2)

            # 显示节点信息
            if 'current_node' in step_data and step_data['current_node'] is not None:
                node = step_data['current_node']
                info_text = f"f={node.f:.1f}\ng={node.g:.1f}\nh={node.h:.1f}"
                self.ax.text(curr[0] + 0.5, curr[1] + 0.5, info_text,
                           fontsize=8, color='red', fontweight='bold')

        # 绘制当前找到的路径
        if step_data['path'] is not None and len(step_data['path']) > 1:
            path_array = np.array(step_data['path'])
            self.ax.plot(path_array[:, 0], path_array[:, 1], 'g-',
                       linewidth=2, alpha=0.5, label='Current Path', zorder=1)

        # 绘制起点和终点
        start = self.planner.start
        goal = self.planner.goal
        self.ax.scatter(start[0], start[1], c='green', s=300, marker='o',
                      label='Start', zorder=5, edgecolors='darkgreen', linewidths=2)
        self.ax.scatter(goal[0], goal[1], c='red', s=400, marker='*',
                      label='Goal', zorder=5, edgecolors='darkred', linewidths=2)

        # 设置标题和标签
        step_msg = step_data.get('message', '')
        title = f"{self.title}\nStep {self.current_step}/{len(self.steps)-1}: {step_msg}"
        self.ax.set_title(title, fontsize=12, fontweight='bold')
        self.ax.set_xlabel('X', fontsize=11)
        self.ax.set_ylabel('Y', fontsize=11)

        # 设置图例
        self.ax.legend(loc='upper left', fontsize=9, framealpha=0.9)

        # 设置坐标轴
        self.ax.set_xlim(-1, width)
        self.ax.set_ylim(-1, height)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.2)

        # 添加控制说明
        control_text = "Controls: ← → (or A/D) Step Back/Forward | Home/End First/Last Step"
        self.fig.text(0.5, 0.02, control_text, ha='center', fontsize=10,
                     style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # 刷新图形
        self.fig.canvas.draw()

    def show(self):
        """显示交互式窗口"""
        plt.tight_layout(rect=[0, 0.04, 1, 1])
        plt.show()


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
    # 使用pcolormesh来精确显示A*算法中的格子
    # grid的shape是(height, width)，A*使用(x, y)坐标系统
    height, width = grid.shape

    # 创建网格边界坐标
    # 格子(i,j)的边界是[i-0.5, i+0.5] x [j-0.5, j+0.5]
    x_edges = np.arange(-0.5, width, 1)
    y_edges = np.arange(-0.5, height, 1)

    # 使用pcolormesh绘制，自动对齐到格子边界
    ax.pcolormesh(x_edges, y_edges, grid, cmap='binary', alpha=0.5,
                  edgecolors='gray', linewidth=0.5)
    
    # 绘制路径
    if path is not None:
        ax.plot(path[:, 0], path[:, 1], 'b-', linewidth=2, label='Path')

    # 绘制起点和终点
    if start is not None:
        ax.scatter(start[0], start[1], c='green', s=200, marker='o',
                  label='Start', zorder=5, edgecolors='black', linewidths=2)
    if goal is not None:
        ax.scatter(goal[0], goal[1], c='red', s=200, marker='*',
                  label='Goal', zorder=5, edgecolors='black', linewidths=2)
    
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
               linewidth=2, alpha=0.7, label='Reference Path')

    # 实际路径
    ax.plot(path[:, 0], path[:, 1], 'r-', linewidth=2, label='Actual Path')

    # 起点和终点
    ax.scatter(path[0, 0], path[0, 1], c='green', s=150,
              marker='o', label='Start', zorder=5)
    ax.scatter(path[-1, 0], path[-1, 1], c='red', s=150,
              marker='*', label='Goal', zorder=5)
    
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
               linewidth=2, alpha=0.7, label='Reference Trajectory')

    # 实际轨迹
    ax.plot(trajectory[:, 0], trajectory[:, 1], 'r-', linewidth=2, label='Actual Trajectory')
    
    # 航向角箭头
    if show_heading and trajectory.shape[1] >= 3:
        for i in range(0, len(trajectory), heading_step):
            x, y, theta = trajectory[i, :3]
            dx = np.cos(theta) * 1.0
            dy = np.sin(theta) * 1.0
            ax.arrow(x, y, dx, dy, head_width=0.4, head_length=0.3, 
                    fc='blue', ec='blue', alpha=0.6)
    
    ax.scatter(trajectory[0, 0], trajectory[0, 1], c='green', s=150,
              marker='o', label='Start', zorder=5)
    ax.scatter(trajectory[-1, 0], trajectory[-1, 1], c='red', s=150,
              marker='*', label='Goal', zorder=5)
    
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
           linewidth=2, alpha=0.7, label='Reference Path')

    # 初始化轨迹线
    line, = ax.plot([], [], 'r-', linewidth=2, label='Actual Trajectory')
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
    print(f"Animation saved: {filename}")


"""
辅助函数模块

提供常用的工具函数
"""

import numpy as np
from typing import List, Tuple


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
        obstacles: 障碍物列表 [(x_min, y_min, x_max, y_max), ...]
    
    Returns:
        grid: 0=空闲，1=障碍物
    """
    grid = np.zeros((height, width), dtype=np.uint8)
    
    if obstacles:
        for x_min, y_min, x_max, y_max in obstacles:
            x_min = max(0, min(x_min, width-1))
            y_min = max(0, min(y_min, height-1))
            x_max = max(0, min(x_max, width-1))
            y_max = max(0, min(y_max, height-1))
            grid[y_min:y_max+1, x_min:x_max+1] = 1
    
    return grid


def create_circular_path(
    radius: float = 10.0,
    num_points: int = 100,
    velocity: float = 2.0
) -> np.ndarray:
    """
    创建圆形参考路径
    
    Args:
        radius: 半径 (m)
        num_points: 点数
        velocity: 参考速度 (m/s)
    
    Returns:
        path: (N, 4) [x, y, θ, v]
    """
    t = np.linspace(0, 2*np.pi, num_points)
    
    path = np.column_stack([
        radius * np.cos(t),
        radius * np.sin(t),
        t + np.pi/2,  # θ
        velocity * np.ones(num_points)
    ])
    
    return path


def create_s_curve_path(
    length: float = 20.0,
    num_points: int = 100,
    velocity: float = 2.0
) -> np.ndarray:
    """
    创建S型曲线路径
    
    Args:
        length: 路径长度 (m)
        num_points: 点数
        velocity: 参考速度 (m/s)
    
    Returns:
        path: (N, 4) [x, y, θ, v]
    """
    s = np.linspace(0, length, num_points)
    
    # S型曲线方程
    x = s
    y = 3 * np.sin(2 * np.pi * s / length)
    
    # 计算航向角
    dx = np.gradient(x)
    dy = np.gradient(y)
    theta = np.arctan2(dy, dx)
    
    path = np.column_stack([x, y, theta, velocity * np.ones(num_points)])
    
    return path


def normalize_angle(angle: float) -> float:
    """归一化角度到[-π, π]"""
    return np.arctan2(np.sin(angle), np.cos(angle))


def calc_distance(pos1: np.ndarray, pos2: np.ndarray) -> float:
    """计算两点间的欧几里得距离"""
    return np.linalg.norm(pos1 - pos2)


def calc_heading_error(theta1: float, theta2: float) -> float:
    """
    计算航向角误差（归一化到[-π, π]）
    
    Args:
        theta1: 当前航向角
        theta2: 目标航向角
    
    Returns:
        error: 航向误差
    """
    error = theta2 - theta1
    return normalize_angle(error)


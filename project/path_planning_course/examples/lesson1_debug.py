"""
Lesson 1 Interactive Debug Demo: A* Path Planning Step-by-Step

这个演示展示了如何使用交互式单步调试工具来深入理解A*算法的执行过程

控制说明:
- 左方向键 (←) 或 A 键: 后退一步
- 右方向键 (→) 或 D 键: 前进一步
- Home 键: 回到第一步
- End 键: 跳到最后一步

可视化元素:
- 绿色圆圈: 起点
- 红色星号: 终点
- 灰色方块: 障碍物
- 浅蓝色方块: Closed Set (已访问的节点)
- 黄色方块: Open List (待扩展的节点)
- 橙色星号: 当前正在扩展的节点
- 绿色路径: 从起点到当前节点的最优路径
"""

import sys
sys.path.append('..')

import numpy as np
from algorithms.a_star import AStar, create_grid_map
from utils.visualization import AStarStepVisualizer

def main():
    print("="*70)
    print("Lesson 1: A* Algorithm Interactive Step-by-Step Debugger")
    print("="*70)

    # ===== 1. 创建简单地图用于演示 =====
    print("\n创建演示地图...")
    width, height = 15, 15

    # 定义障碍物 - 使用较少障碍物以便更好地观察
    obstacles = [
        (5, 5, 7, 7),    # 中央小方块障碍物
        (9, 2, 10, 8),   # 右侧垂直障碍物
    ]

    grid = create_grid_map(width, height, obstacles)
    print(f"  地图大小: {width} × {height}")
    print(f"  障碍物数量: {len(obstacles)}")

    # ===== 2. 定义起点和终点 =====
    start = (2, 2)
    goal = (12, 12)

    print(f"\n起点: {start}")
    print(f"终点: {goal}")

    # ===== 3. 执行A*规划并记录每一步 =====
    print(f"\n执行A*路径规划（记录模式）...")
    planner = AStar(grid, start, goal, heuristic_weight=1.0)

    # 重要：使用 record_steps=True 参数来记录每一步
    path = planner.plan(verbose=False, record_steps=True)

    if path is None:
        print("\n✗ 规划失败！")
        return

    print(f"✓ 规划成功！")
    print(f"  总步数: {len(planner.steps)}")
    print(f"  最终路径长度: {len(path)}")
    print(f"  扩展节点数: {planner.nodes_expanded}")

    # ===== 4. 启动交互式调试器 =====
    print(f"\n启动交互式调试器...")
    print("\n" + "="*70)
    print("控制说明:")
    print("  ← 或 A : 后退一步")
    print("  → 或 D : 前进一步")
    print("  Home   : 回到第一步")
    print("  End    : 跳到最后一步")
    print("="*70)
    print("\n提示: 仔细观察每一步中:")
    print("  1. 当前节点的f, g, h值")
    print("  2. Open List (黄色) 如何变化")
    print("  3. Closed Set (浅蓝色) 如何扩展")
    print("  4. 当前路径 (绿色) 如何更新")
    print("="*70)

    # 创建并显示交互式可视化
    visualizer = AStarStepVisualizer(
        planner,
        title="A* Algorithm Step-by-Step Debug (Lesson 1)"
    )
    visualizer.show()

    print("\n演示结束！")


if __name__ == "__main__":
    main()

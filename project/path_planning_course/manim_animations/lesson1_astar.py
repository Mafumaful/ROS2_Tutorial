"""
第1课 Manim动画: A*路径规划算法

包含5个教学动画场景:
1. AStarOverview - A*算法整体流程示意 (⭐ 整体理解，课程开场)
2. PathPlanningIntro - 路径规划问题介绍 (适合课程开场)
3. SearchSpaceDemo - 搜索空间和启发式函数 (解释核心概念)
4. AStarVisualization - A*完整搜索过程演示 (详细步骤)
5. AStarGridSearch - A*网格搜索动画 (简化演示)

教学建议:
- AStarOverview: 🌟 整体流程示意，帮助学生建立全局认知
- PathPlanningIntro: 用于引入路径规划概念
- SearchSpaceDemo: 讲解启发式搜索原理
- AStarVisualization: 完整演示算法流程（重点）
- AStarGridSearch: 快速回顾和总结

推荐教学顺序:
  开场: AStarOverview (建立整体认知)
  详解: SearchSpaceDemo → AStarVisualization
  总结: AStarGridSearch

渲染命令:
  manim -pql lesson1_astar.py AStarOverview
  manim -pql lesson1_astar.py AStarVisualization
"""

from manim import *
import numpy as np


# ===== 颜色配置 =====
START_COLOR = GREEN
GOAL_COLOR = RED
PATH_COLOR = BLUE
OBSTACLE_COLOR = GRAY
OPEN_COLOR = YELLOW
CLOSED_COLOR = GRAY
CURRENT_COLOR = ORANGE


class AStarOverview(Scene):
    """
    整体示意场景: A*算法流程总览
    
    教学目标:
    - 让学生从整体上理解A*算法的工作流程
    - 展示算法的关键步骤和核心思想
    - 建立全局认知，为后续详细学习打基础
    
    适用场景:
    - 课程开场（强烈推荐）⭐⭐⭐⭐⭐
    - 课程总结回顾
    - 给初学者建立整体框架
    
    时长: ~45秒
    """
    
    def construct(self):
        # ===== 标题 =====
        title = Text("A* 算法整体流程", font_size=48, color=BLUE, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.8)
        
        # ===== 流程图 =====
        flow_steps = VGroup(
            Text("1. 初始化", font_size=32, color=GREEN),
            Text("↓", font_size=40, color=WHITE),
            Text("2. 选择最优节点", font_size=32, color=YELLOW),
            Text("↓", font_size=40, color=WHITE),
            Text("3. 扩展邻居", font_size=32, color=ORANGE),
            Text("↓", font_size=40, color=WHITE),
            Text("4. 计算代价 f=g+h", font_size=32, color=BLUE),
            Text("↓", font_size=40, color=WHITE),
            Text("5. 到达目标？", font_size=32, color=RED),
        ).arrange(DOWN, buff=0.25)
        flow_steps.shift(LEFT * 3.5)
        
        self.play(Write(flow_steps), run_time=3)
        self.wait(1)
        
        # ===== 示意图 =====
        # 简化的网格
        grid_size = 5
        cell_size = 0.5
        grid = VGroup()
        
        for i in range(grid_size):
            for j in range(grid_size):
                cell = Square(side_length=cell_size)
                cell.move_to(np.array([
                    (i - grid_size/2 + 0.5) * cell_size + 3,
                    (j - grid_size/2 + 0.5) * cell_size,
                    0
                ]))
                cell.set_stroke(BLUE_D, width=0.8)
                cell.set_fill(BLACK, opacity=0)
                grid.add(cell)
        
        self.play(Create(grid), run_time=1)
        
        # 起点和终点
        start_dot = Dot(radius=0.15, color=GREEN).move_to(
            np.array([2 * cell_size + 3, -2 * cell_size, 0])
        )
        goal_dot = Dot(radius=0.15, color=RED).move_to(
            np.array([4 * cell_size + 3, 2 * cell_size, 0])
        )
        
        start_label = Text("起点", font_size=18, color=GREEN).next_to(start_dot, DOWN, buff=0.15)
        goal_label = Text("终点", font_size=18, color=RED).next_to(goal_dot, UP, buff=0.15)
        
        self.play(
            GrowFromCenter(start_dot),
            GrowFromCenter(goal_dot),
            Write(start_label),
            Write(goal_label)
        )
        self.wait(0.5)
        
        # 搜索过程动画
        search_path = [
            (0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (4, 2)
        ]
        
        search_dots = VGroup()
        for i, (x, y) in enumerate(search_path):
            if i == 0 or i == len(search_path) - 1:
                continue
            dot = Dot(
                radius=0.08,
                color=YELLOW,
                fill_opacity=0.6
            ).move_to(np.array([
                (x - grid_size/2 + 0.5) * cell_size + 3,
                (y - grid_size/2 + 0.5) * cell_size,
                0
            ]))
            search_dots.add(dot)
        
        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in search_dots], lag_ratio=0.2))
        self.wait(0.5)
        
        # 最终路径
        path_points = []
        for x, y in search_path:
            path_points.append(np.array([
                (x - grid_size/2 + 0.5) * cell_size + 3,
                (y - grid_size/2 + 0.5) * cell_size,
                0
            ]))
        
        path_line = VMobject(color=BLUE, stroke_width=4)
        path_line.set_points_as_corners(path_points)
        
        self.play(Create(path_line), run_time=1.5)
        self.wait(0.5)
        
        # 核心公式
        formula_box = VGroup(
            Text("核心公式:", font_size=28, color=YELLOW),
            Text("f(n) = g(n) + h(n)", font_size=32, color=WHITE, weight=BOLD),
            VGroup(
                Text("g: 起点→当前", font_size=20, color=GREEN),
                Text("h: 当前→终点", font_size=20, color=RED),
            ).arrange(RIGHT, buff=0.8)
        ).arrange(DOWN, buff=0.3)
        formula_box.to_corner(DR, buff=0.8)
        
        self.play(FadeIn(formula_box, shift=UP))
        self.wait(2)
        
        # 总结
        summary = VGroup(
            Text("✓ 启发式搜索", font_size=26),
            Text("✓ 保证最优", font_size=26),
            Text("✓ 高效快速", font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        summary.next_to(flow_steps, DOWN, buff=0.8, aligned_edge=LEFT)
        
        self.play(Write(summary), run_time=1.5)
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class PathPlanningIntro(Scene):
    """
    动画1: 路径规划问题介绍
    
    展示内容:
    - 网格地图
    - 起点和终点
    - 障碍物
    - 多条可能路径
    - 最优路径高亮
    """
    
    def construct(self):
        # 标题
        title = Text("什么是路径规划?", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        
        # 创建网格
        grid_size = 8
        cell_size = 0.6
        grid = VGroup()
        
        for i in range(grid_size):
            for j in range(grid_size):
                cell = Square(side_length=cell_size)
                cell.move_to(np.array([
                    (i - grid_size/2 + 0.5) * cell_size,
                    (j - grid_size/2 + 0.5) * cell_size,
                    0
                ]))
                cell.set_stroke(BLUE_D, width=1)
                grid.add(cell)
        
        grid.shift(DOWN * 0.5)
        self.play(Create(grid), run_time=1.5)
        self.wait(0.5)
        
        # 添加障碍物
        obstacles = VGroup()
        obstacle_coords = [(3, 3), (3, 4), (4, 3), (4, 4)]
        
        for x, y in obstacle_coords:
            obs = Square(side_length=cell_size)
            obs.move_to(np.array([
                (x - grid_size/2 + 0.5) * cell_size,
                (y - grid_size/2 + 0.5) * cell_size,
                0
            ]))
            obs.set_fill(OBSTACLE_COLOR, opacity=0.8)
            obs.set_stroke(WHITE, width=0)
            obstacles.add(obs)
        
        obstacles.shift(DOWN * 0.5)
        
        obs_label = Text("障碍物", font_size=28)
        obs_label.next_to(obstacles, RIGHT, buff=1)
        
        self.play(
            FadeIn(obstacles),
            Write(obs_label),
            run_time=1
        )
        self.wait(0.5)
        
        # 标记起点
        start = Dot(radius=0.15, color=START_COLOR)
        start.move_to(np.array([
            (1 - grid_size/2 + 0.5) * cell_size,
            (1 - grid_size/2 + 0.5) * cell_size,
            0
        ]))
        start.shift(DOWN * 0.5)
        
        start_label = Text("S", font_size=36, color=START_COLOR)
        start_label.move_to(start.get_center())
        
        self.play(
            GrowFromCenter(start),
            Write(start_label)
        )
        self.wait(0.3)
        
        # 标记终点
        goal = Star(n=5, outer_radius=0.2, color=GOAL_COLOR, fill_opacity=1)
        goal.move_to(np.array([
            (6 - grid_size/2 + 0.5) * cell_size,
            (6 - grid_size/2 + 0.5) * cell_size,
            0
        ]))
        goal.shift(DOWN * 0.5)
        
        goal_label = Text("G", font_size=36, color=GOAL_COLOR)
        goal_label.move_to(goal.get_center())
        
        self.play(
            GrowFromCenter(goal),
            Write(goal_label)
        )
        self.wait(0.5)
        
        # 展示一条路径
        path_points = [
            (1, 1), (2, 1), (2, 2), (2, 3), 
            (2, 4), (2, 5), (3, 5), (4, 5),
            (5, 5), (5, 6), (6, 6)
        ]
        
        path_lines = VGroup()
        for i in range(len(path_points) - 1):
            x1, y1 = path_points[i]
            x2, y2 = path_points[i+1]
            
            p1 = np.array([
                (x1 - grid_size/2 + 0.5) * cell_size,
                (y1 - grid_size/2 + 0.5) * cell_size,
                0
            ])
            p2 = np.array([
                (x2 - grid_size/2 + 0.5) * cell_size,
                (y2 - grid_size/2 + 0.5) * cell_size,
                0
            ])
            
            line = Line(p1, p2, color=PATH_COLOR, stroke_width=4)
            path_lines.add(line)
        
        path_lines.shift(DOWN * 0.5)
        
        self.play(
            Create(path_lines),
            run_time=2
        )
        self.wait(0.5)
        
        # 目标文字
        goal_text = Text("找到一条从S到G的无碰撞路径", font_size=32)
        goal_text.next_to(grid, DOWN, buff=0.8)
        
        self.play(Write(goal_text))
        self.wait(2)
        
        # 淡出
        self.play(
            *[FadeOut(mob) for mob in self.mobjects]
        )


class SearchSpaceDemo(Scene):
    """
    动画2: 搜索空间展示
    
    展示内容:
    - 状态空间定义
    - 8连通邻居
    - 移动代价
    """
    
    def construct(self):
        # 标题
        title = Text("搜索空间", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 中心节点
        center = Dot(radius=0.2, color=BLUE)
        center_label = Text("当前节点", font_size=28)
        center_label.next_to(center, DOWN, buff=0.5)
        
        self.play(
            GrowFromCenter(center),
            Write(center_label)
        )
        self.wait(0.5)
        
        # 8个邻居
        directions = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]
        
        neighbors = VGroup()
        arrows = VGroup()
        cost_labels = VGroup()
        
        for dx, dy in directions:
            # 邻居节点
            neighbor = Dot(radius=0.15, color=YELLOW)
            neighbor.shift(RIGHT * dx * 1.5 + UP * dy * 1.5)
            neighbors.add(neighbor)
            
            # 箭头
            arrow = Arrow(
                center.get_center(),
                neighbor.get_center(),
                buff=0.2,
                color=WHITE,
                stroke_width=2
            )
            arrows.add(arrow)
            
            # 代价标签
            cost = np.sqrt(dx**2 + dy**2)
            if cost > 1.1:  # 对角线
                cost_text = Text(f"√2", font_size=20, color=YELLOW)
            else:  # 直线
                cost_text = Text(f"1", font_size=20, color=GREEN)
            
            cost_text.move_to((center.get_center() + neighbor.get_center()) / 2)
            cost_text.shift(UP * 0.3)
            cost_labels.add(cost_text)
        
        self.play(
            Create(arrows),
            *[GrowFromCenter(n) for n in neighbors],
            run_time=2
        )
        self.wait(0.5)
        
        # 显示代价
        self.play(
            *[Write(c) for c in cost_labels],
            run_time=1.5
        )
        self.wait(1)
        
        # 说明文字
        explanation = VGroup(
            Text("8连通移动:", font_size=28),
            Text("• 直线移动代价 = 1", font_size=24),
            Text("• 对角移动代价 = √2 ≈ 1.414", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        explanation.to_edge(DOWN, buff=0.5)
        
        self.play(Write(explanation))
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class AStarVisualization(Scene):
    """
    动画3: A*搜索过程完整演示（教学重点场景）
    
    展示内容:
    - 步骤1: 初始化（起点、终点、障碍物）
    - 步骤2: 计算 f(n) = g(n) + h(n)
    - 步骤3: 逐步搜索过程
    - 步骤4: Open List 和 Closed Set 变化
    - 步骤5: 找到最优路径
    - 步骤6: 路径回溯
    
    教学要点:
    - 清晰展示每一步的状态变化
    - 强调启发式函数的作用
    - 展示为什么A*比Dijkstra更高效
    """
    
    def construct(self):
        # ===== 步骤0: 标题和核心公式 =====
        title = Text("A* 搜索算法", font_size=48, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.8)
        
        # 核心公式
        formula = Text(
            "f(n) = g(n) + h(n)",
            font_size=42,
            color=WHITE,
            weight=BOLD
        )
        formula.next_to(title, DOWN, buff=0.4)
        
        # 公式说明（带颜色标识）
        g_label = Text("g(n): 起点到当前的实际代价", font_size=26, color=GREEN)
        h_label = Text("h(n): 当前到终点的估计代价", font_size=26, color=YELLOW)
        f_label = Text("f(n): 总评估代价 = g + h", font_size=26, color=BLUE)
        
        labels = VGroup(g_label, h_label, f_label).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        labels.to_corner(UL, buff=0.6)
        labels.shift(DOWN * 2.2)
        
        self.play(Write(formula))
        self.wait(0.5)
        self.play(Write(labels), run_time=2)
        self.wait(1.5)
        
        # 添加步骤指示器
        step_indicator = Text("步骤 1/5: 初始化搜索空间", font_size=28, color=YELLOW)
        step_indicator.to_corner(DR, buff=0.6)
        self.play(FadeIn(step_indicator, shift=UP))
        self.wait(1)
        
        # 创建简化的网格
        grid_size = 5
        cell_size = 0.8
        grid = VGroup()
        
        for i in range(grid_size):
            for j in range(grid_size):
                cell = Square(side_length=cell_size)
                cell.move_to(np.array([
                    (i - grid_size/2 + 0.5) * cell_size + 2,
                    (j - grid_size/2 + 0.5) * cell_size - 1,
                    0
                ]))
                cell.set_stroke(BLUE_D, width=1)
                grid.add(cell)
        
        self.play(Create(grid), run_time=1)
        
        # 起点和终点
        start_pos = (0, 0)
        goal_pos = (4, 4)
        
        def grid_to_screen(x, y):
            return np.array([
                (x - grid_size/2 + 0.5) * cell_size + 2,
                (y - grid_size/2 + 0.5) * cell_size - 1,
                0
            ])
        
        start_dot = Dot(grid_to_screen(*start_pos), radius=0.15, color=START_COLOR)
        goal_dot = Star(5, outer_radius=0.2, color=GOAL_COLOR, fill_opacity=1)
        goal_dot.move_to(grid_to_screen(*goal_pos))
        
        self.play(
            GrowFromCenter(start_dot),
            GrowFromCenter(goal_dot)
        )
        self.wait(0.5)
        
        # 模拟搜索过程
        # 简化版本：展示几个关键步骤
        
        # 扩展第一个节点
        current = Dot(grid_to_screen(0, 0), radius=0.15, color=CURRENT_COLOR)
        self.play(Transform(start_dot.copy(), current))
        self.wait(0.3)
        
        # 显示邻居
        neighbors_pos = [(1, 0), (0, 1), (1, 1)]
        neighbor_dots = VGroup()
        
        for x, y in neighbors_pos:
            dot = Dot(grid_to_screen(x, y), radius=0.12, color=OPEN_COLOR)
            neighbor_dots.add(dot)
        
        self.play(*[GrowFromCenter(d) for d in neighbor_dots])
        self.wait(0.3)
        
        # 标记为已访问
        start_cell = Square(side_length=cell_size)
        start_cell.move_to(grid_to_screen(*start_pos))
        start_cell.set_fill(CLOSED_COLOR, opacity=0.3)
        start_cell.set_stroke(width=0)
        
        self.play(FadeIn(start_cell))
        self.wait(0.3)
        
        # 继续扩展（快进）
        expansion_sequence = [
            (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 3), (4, 3), (4, 4)
        ]
        
        for x, y in expansion_sequence[:-1]:
            # 当前节点
            current_new = Dot(grid_to_screen(x, y), radius=0.12, color=CURRENT_COLOR)
            self.play(FadeIn(current_new), run_time=0.2)
            
            # 标记为已访问
            visited_cell = Square(side_length=cell_size)
            visited_cell.move_to(grid_to_screen(x, y))
            visited_cell.set_fill(CLOSED_COLOR, opacity=0.3)
            visited_cell.set_stroke(width=0)
            self.play(FadeIn(visited_cell), run_time=0.1)
            
            self.wait(0.1)
        
        # 到达终点
        success_text = Text("找到路径！", font_size=40, color=GREEN)
        success_text.next_to(grid, DOWN, buff=0.5)
        self.play(Write(success_text))
        
        # 绘制最终路径
        path = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
        path_lines = VGroup()
        
        for i in range(len(path) - 1):
            line = Line(
                grid_to_screen(*path[i]),
                grid_to_screen(*path[i+1]),
                color=PATH_COLOR,
                stroke_width=6
            )
            path_lines.add(line)
        
        self.play(Create(path_lines), run_time=1.5)
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class AStarGridSearch(Scene):
    """
    动画4: A*网格搜索简化演示（快速回顾场景）
    
    适用场景：
    - 课程总结回顾
    - 时间有限时的快速演示
    - 展示完整的搜索流程
    
    特点：节奏紧凑、重点突出最终结果
    """
    
    def construct(self):
        # 标题
        title = Text("A* 路径搜索演示", font_size=44, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 创建网格
        grid_size = 8
        cell_size = 0.6
        grid = VGroup()
        
        for i in range(grid_size):
            for j in range(grid_size):
                cell = Square(side_length=cell_size)
                cell.move_to(np.array([
                    (i - grid_size/2 + 0.5) * cell_size,
                    (j - grid_size/2 + 0.5) * cell_size - 0.5,
                    0
                ]))
                cell.set_stroke(BLUE_D, width=0.8, opacity=0.5)
                cell.set_fill(BLACK, opacity=0)
                grid.add(cell)
        
        self.play(Create(grid), run_time=1)
        self.wait(0.3)
        
        # 添加障碍物
        obstacles = VGroup()
        obstacle_coords = [(3, 2), (3, 3), (3, 4), (3, 5), (4, 5), (5, 5)]
        
        for x, y in obstacle_coords:
            obs = Square(side_length=cell_size)
            obs.move_to(np.array([
                (x - grid_size/2 + 0.5) * cell_size,
                (y - grid_size/2 + 0.5) * cell_size - 0.5,
                0
            ]))
            obs.set_fill(GRAY, opacity=0.8)
            obs.set_stroke(WHITE, width=1)
            obstacles.add(obs)
        
        self.play(FadeIn(obstacles), run_time=0.8)
        self.wait(0.3)
        
        # 起点和终点
        start_dot = Dot(radius=0.2, color=GREEN)
        start_dot.move_to(np.array([
            (1 - grid_size/2 + 0.5) * cell_size,
            (1 - grid_size/2 + 0.5) * cell_size - 0.5,
            0
        ]))
        
        goal_dot = Dot(radius=0.2, color=RED)
        goal_dot.move_to(np.array([
            (6 - grid_size/2 + 0.5) * cell_size,
            (6 - grid_size/2 + 0.5) * cell_size - 0.5,
            0
        ]))
        
        start_label = Text("起点", font_size=20, color=GREEN).next_to(start_dot, DOWN, buff=0.2)
        goal_label = Text("终点", font_size=20, color=RED).next_to(goal_dot, UP, buff=0.2)
        
        self.play(
            GrowFromCenter(start_dot),
            GrowFromCenter(goal_dot),
            Write(start_label),
            Write(goal_label),
            run_time=1
        )
        self.wait(0.5)
        
        # 搜索提示
        search_text = Text("正在搜索最优路径...", font_size=28, color=YELLOW)
        search_text.to_edge(DOWN, buff=0.8)
        self.play(Write(search_text))
        self.wait(0.5)
        
        # 绘制路径
        path = [(1,1), (2,1), (2,2), (2,3), (2,4), (2,5), (2,6), (3,6), (4,6), (5,6), (6,6)]
        
        path_line = VMobject(color=BLUE, stroke_width=6)
        points = []
        for x, y in path:
            point = np.array([
                (x - grid_size/2 + 0.5) * cell_size,
                (y - grid_size/2 + 0.5) * cell_size - 0.5,
                0
            ])
            points.append(point)
        
        path_line.set_points_as_corners(points)
        
        self.play(
            Transform(search_text, Text("找到最优路径!", font_size=28, color=GREEN).to_edge(DOWN, buff=0.8)),
            Create(path_line, run_time=2)
        )
        self.wait(2)
        
        # 算法特点总结
        summary = VGroup(
            Text("A* 算法特点:", font_size=28, color=YELLOW),
            Text("✓ 启发式函数引导搜索", font_size=24),
            Text("✓ 保证找到最优路径", font_size=24),
            Text("✓ 比盲目搜索更高效", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        summary.to_corner(UR, buff=0.8)
        
        self.play(Write(summary), run_time=2)
        self.wait(3)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


# ===== 渲染指令和教学建议 =====
if __name__ == "__main__":
    """
    教学建议的渲染和使用顺序:
    
    1. 引入概念 (课程开场, ~30秒)
       manim -pql lesson1_astar.py PathPlanningIntro
    
    2. 讲解原理 (解释启发式搜索, ~40秒)
       manim -pql lesson1_astar.py SearchSpaceDemo
    
    3. 详细演示 (重点场景, ~60秒)
       manim -pql lesson1_astar.py AStarVisualization
    
    4. 快速回顾 (总结复习, ~30秒)
       manim -pql lesson1_astar.py AStarGridSearch
    
    高质量渲染（用于课件制作）:
       manim -pqh lesson1_astar.py AStarVisualization
    
    渲染所有场景:
       manim -pql lesson1_astar.py
    """
    pass


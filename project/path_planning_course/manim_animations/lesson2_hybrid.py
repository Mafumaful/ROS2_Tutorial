"""
第2课 Manim动画: Hybrid A*与车辆运动学

包含4个教学动画场景:
1. HybridAStarOverview - Hybrid A*整体流程示意 (⭐ 整体理解)
2. CompareAStarHybridAStar - 传统A* vs Hybrid A*对比 (对比差异)
3. VehicleKinematicsDemo - 车辆运动学演示 (核心概念，重点)
4. HybridAStarExpansion - Hybrid A*扩展过程 (算法细节)

教学建议:
- HybridAStarOverview: 🌟 整体流程示意，让学生理解Hybrid A*全貌
- CompareAStarHybridAStar: 开场对比，引出Hybrid A*的必要性
- VehicleKinematicsDemo: 详细讲解车辆运动学模型（教学重点）
- HybridAStarExpansion: 展示考虑运动学约束的路径规划

核心要点:
- 车辆是非完整约束系统
- 轴距L决定最小转弯半径
- 转向角δ影响航向角变化率

推荐教学顺序:
  开场: HybridAStarOverview (建立整体认知)
  对比: CompareAStarHybridAStar
  详解: VehicleKinematicsDemo (重点)

渲染命令:
  manim -pql lesson2_hybrid.py HybridAStarOverview
  manim -pql lesson2_hybrid.py VehicleKinematicsDemo
"""

from manim import *
import numpy as np


# ===== 颜色配置 =====
START_COLOR = GREEN
GOAL_COLOR = RED
PATH_COLOR = BLUE
OBSTACLE_COLOR = GRAY
VEHICLE_COLOR = BLUE


class HybridAStarOverview(Scene):
    """
    整体示意场景: Hybrid A*算法流程总览
    
    教学目标:
    - 让学生从整体上理解Hybrid A*算法的工作原理
    - 展示Hybrid A*与传统A*的核心区别
    - 建立车辆运动学约束的概念
    
    适用场景:
    - 课程开场（强烈推荐）⭐⭐⭐⭐⭐
    - 帮助学生建立全局认知
    
    时长: ~50秒
    """
    
    def construct(self):
        # ===== 标题 =====
        title = Text("Hybrid A* 算法整体流程", font_size=44, color=BLUE, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.8)
        
        subtitle = Text("(考虑车辆运动学的路径规划)", font_size=26, color=GRAY)
        subtitle.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(subtitle))
        self.wait(0.5)
        
        # ===== 左侧: 核心思想 =====
        core_ideas = VGroup(
            Text("核心思想:", font_size=30, color=YELLOW),
            VGroup(
                Text("✓ 考虑车辆运动学", font_size=24),
                Text("✓ 离散化状态空间", font_size=24),
                Text("✓ 使用运动原语", font_size=24),
                Text("✓ 保证路径可执行", font_size=24),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        core_ideas.to_edge(LEFT, buff=0.8)
        core_ideas.shift(DOWN * 0.5)
        
        self.play(Write(core_ideas), run_time=2.5)
        self.wait(1)
        
        # ===== 右侧: 车辆模型示意 =====
        # 简单的车辆示意图
        vehicle = Rectangle(width=0.8, height=0.4, color=VEHICLE_COLOR)
        vehicle.set_fill(VEHICLE_COLOR, opacity=0.5)
        vehicle.shift(RIGHT * 3 + UP * 1.5)
        
        arrow = Arrow(ORIGIN, RIGHT * 0.5, color=RED, buff=0)
        arrow.next_to(vehicle, RIGHT, buff=0)
        
        # 轴距标注
        wheelbase_line = Line(
            vehicle.get_left() + UP * 0.15,
            vehicle.get_right() + UP * 0.15,
            color=YELLOW
        )
        l_label = Text("L", font_size=24, color=YELLOW)
        l_label.next_to(wheelbase_line, UP, buff=0.15)
        
        vehicle_group = VGroup(vehicle, arrow, wheelbase_line, l_label)
        
        self.play(Create(vehicle_group))
        self.wait(0.5)
        
        # 运动学方程
        equations = VGroup(
            Text("运动学方程:", font_size=26, color=YELLOW),
            Text("ẋ = v · cos(θ)", font_size=22, color=WHITE),
            Text("ẏ = v · sin(θ)", font_size=22, color=WHITE),
            Text("θ̇ = v · tan(δ) / L", font_size=22, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        equations.next_to(vehicle_group, DOWN, buff=0.6, aligned_edge=LEFT)
        
        self.play(Write(equations), run_time=2)
        self.wait(1)
        
        # ===== 底部: 算法流程 =====
        flow = VGroup(
            Text("算法流程:", font_size=28, color=YELLOW),
            Text("初始化 → 选择节点 → 应用运动原语 →", font_size=22),
            Text("碰撞检测 → 计算代价 → 重复直到到达目标", font_size=22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        flow.to_edge(DOWN, buff=0.8)
        
        self.play(FadeIn(flow, shift=UP), run_time=1.5)
        self.wait(2)
        
        # ===== 关键优势 =====
        advantage = Text("关键优势: 路径平滑、可执行、适合自动驾驶", 
                        font_size=26, color=GREEN)
        advantage.next_to(flow, UP, buff=0.6)
        
        self.play(Write(advantage))
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class CompareAStarHybridAStar(Scene):
    """
    动画1: 传统A* vs Hybrid A*对比（开场动画）
    
    教学目标:
    - 直观展示传统A*的局限性（锯齿路径）
    - 引出Hybrid A*的优势（平滑可执行路径）
    - 说明为什么需要考虑车辆运动学
    
    展示内容:
    - 左侧: 传统A*的锯齿路径
    - 右侧: Hybrid A*的平滑路径
    - 对比说明: 可行性差异
    
    适合: 课程引入，激发学习兴趣
    """
    
    def construct(self):
        # 标题
        title = Text("传统A* vs Hybrid A*", font_size=44)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 分割线
        divider = Line(UP * 3, DOWN * 3, color=WHITE)
        self.play(Create(divider))
        
        # 左侧: 传统A*
        left_title = Text("传统A*", font_size=32, color=BLUE)
        left_title.to_corner(UL, buff=0.8)
        left_title.shift(DOWN * 1.2)
        
        # 右侧: Hybrid A*
        right_title = Text("Hybrid A*", font_size=32, color=RED)
        right_title.to_corner(UR, buff=0.8)
        right_title.shift(DOWN * 1.2)
        
        self.play(Write(left_title), Write(right_title))
        self.wait(0.5)
        
        # 左侧网格和路径
        grid_size = 6
        cell_size = 0.4
        
        # A*网格路径（锯齿状）
        astar_points = [
            (1, 1), (2, 1), (3, 2), (3, 3), (4, 3), (4, 4)
        ]
        
        astar_path = VGroup()
        for i in range(len(astar_points) - 1):
            x1, y1 = astar_points[i]
            x2, y2 = astar_points[i+1]
            
            p1 = np.array([
                (x1 - grid_size/2) * cell_size - 3,
                (y1 - grid_size/2) * cell_size - 0.5,
                0
            ])
            p2 = np.array([
                (x2 - grid_size/2) * cell_size - 3,
                (y2 - grid_size/2) * cell_size - 0.5,
                0
            ])
            
            line = Line(p1, p2, color=BLUE, stroke_width=4)
            astar_path.add(line)
        
        # Hybrid A*平滑路径
        t = np.linspace(0, 1, 50)
        hybrid_points = np.array([
            3 + 2 * t,
            -0.5 + 2 * t + 0.5 * np.sin(3 * np.pi * t),
            np.zeros_like(t)
        ]).T
        
        hybrid_path = VMobject(color=RED, stroke_width=4)
        hybrid_path.set_points_smoothly(hybrid_points)
        
        # 起点和终点标记
        start_left = Dot(np.array([-3.6, -1.3, 0]), color=START_COLOR, radius=0.12)
        goal_left = Dot(np.array([-1.4, 0.7, 0]), color=GOAL_COLOR, radius=0.12)
        
        start_right = Dot(np.array([3, -0.5, 0]), color=START_COLOR, radius=0.12)
        goal_right = Dot(np.array([5, 1.5, 0]), color=GOAL_COLOR, radius=0.12)
        
        # 动画展示
        self.play(
            GrowFromCenter(start_left),
            GrowFromCenter(goal_left),
            GrowFromCenter(start_right),
            GrowFromCenter(goal_right)
        )
        self.wait(0.3)
        
        self.play(
            Create(astar_path),
            Create(hybrid_path),
            run_time=2
        )
        self.wait(0.5)
        
        # 添加说明文字
        astar_label = Text("锯齿状\n不可直接执行", font_size=20, color=YELLOW)
        astar_label.next_to(astar_path, DOWN, buff=0.8)
        
        hybrid_label = Text("平滑\n可直接执行", font_size=20, color=YELLOW)
        hybrid_label.next_to(hybrid_path, DOWN, buff=0.8)
        
        self.play(Write(astar_label), Write(hybrid_label))
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class VehicleKinematicsDemo(Scene):
    """
    动画2: 车辆运动学演示
    
    展示内容:
    - 车辆模型示意图
    - 不同转向角的轨迹
    - 最小转弯半径
    """
    
    def construct(self):
        # 标题
        title = Text("车辆运动学", font_size=44)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 车辆示意图（简化为矩形+方向箭头）
        vehicle = Rectangle(width=0.8, height=0.4, color=VEHICLE_COLOR)
        vehicle.set_fill(VEHICLE_COLOR, opacity=0.5)
        
        # 车头箭头
        arrow = Arrow(ORIGIN, RIGHT * 0.5, color=RED, buff=0)
        arrow.next_to(vehicle, RIGHT, buff=0)
        
        vehicle_group = VGroup(vehicle, arrow)
        vehicle_group.move_to(ORIGIN)
        
        self.play(Create(vehicle), GrowArrow(arrow))
        self.wait(0.5)
        
        # 显示运动学方程
        equations = VGroup(
            Text("ẋ = v · cos(θ)", font_size=32, color=WHITE),
            Text("ẏ = v · sin(θ)", font_size=32, color=WHITE),
            Text("θ̇ = v · tan(δ) / L", font_size=32, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        equations.to_edge(LEFT, buff=0.8)
        equations.shift(DOWN * 0.5)
        
        self.play(Write(equations), run_time=2)
        self.wait(1)
        
        # 移动车辆到起始位置
        self.play(vehicle_group.animate.move_to(LEFT * 4 + DOWN * 1))
        
        # 演示三种转向情况
        steering_cases = [
            {"angle": 0, "color": BLUE, "label": "直行"},
            {"angle": np.pi/6, "color": GREEN, "label": "小转弯"},
            {"angle": np.pi/4, "color": RED, "label": "大转弯"},
        ]
        
        traces = VGroup()
        
        for case in steering_cases:
            # 计算轨迹
            if case["angle"] == 0:
                # 直线
                path = Line(
                    vehicle_group.get_center(),
                    vehicle_group.get_center() + RIGHT * 3,
                    color=case["color"],
                    stroke_width=3
                )
            else:
                # 圆弧
                L = 2.7  # 轴距
                R = L / np.tan(case["angle"])  # 转弯半径
                
                # 创建圆弧路径
                arc = Arc(
                    radius=abs(R) * 0.3,
                    start_angle=-np.pi/2,
                    angle=np.pi/2,
                    color=case["color"],
                    stroke_width=3
                )
                arc.next_to(vehicle_group, RIGHT, buff=0)
                path = arc
            
            label = Text(case["label"], font_size=24, color=case["color"])
            label.next_to(path, RIGHT, buff=0.3)
            
            self.play(Create(path), Write(label), run_time=1)
            traces.add(VGroup(path, label))
            self.wait(0.3)
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class HybridAStarExpansion(Scene):
    """
    动画3: Hybrid A*扩展过程
    
    展示内容:
    - 当前节点
    - 运动原语扩展
    - 生成的后继节点
    """
    
    def construct(self):
        # 标题
        title = Text("Hybrid A* 节点扩展", font_size=44)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 当前节点（车辆）
        current_vehicle = Rectangle(width=0.6, height=0.3, color=YELLOW)
        current_vehicle.set_fill(YELLOW, opacity=0.7)
        current_arrow = Arrow(ORIGIN, RIGHT * 0.4, color=RED, buff=0)
        current_arrow.next_to(current_vehicle, RIGHT, buff=0)
        current_node = VGroup(current_vehicle, current_arrow)
        current_node.move_to(ORIGIN)
        
        current_label = Text("当前节点", font_size=28, color=YELLOW)
        current_label.next_to(current_node, DOWN, buff=0.5)
        
        self.play(
            Create(current_node),
            Write(current_label)
        )
        self.wait(0.5)
        
        # 运动原语标签
        primitives_title = Text("运动原语:", font_size=28)
        primitives_title.to_corner(UL, buff=0.8)
        primitives_title.shift(DOWN)
        
        primitives_list = VGroup(
            Text("• 大幅左转", font_size=20),
            Text("• 小幅左转", font_size=20),
            Text("• 直行", font_size=20),
            Text("• 小幅右转", font_size=20),
            Text("• 大幅右转", font_size=20),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        primitives_list.next_to(primitives_title, DOWN, buff=0.3, aligned_edge=LEFT)
        
        self.play(Write(primitives_title), Write(primitives_list), run_time=1.5)
        self.wait(0.5)
        
        # 展示5个运动原语
        angles = [-np.pi/4, -np.pi/8, 0, np.pi/8, np.pi/4]
        colors = [BLUE, GREEN, YELLOW, GREEN, BLUE]
        
        successor_paths = VGroup()
        successor_nodes = VGroup()
        
        for i, (angle, color) in enumerate(zip(angles, colors)):
            # 计算终点位置
            distance = 2.0
            end_x = distance * np.cos(angle)
            end_y = distance * np.sin(angle)
            end_pos = np.array([end_x, end_y, 0])
            
            # 创建路径（圆弧或直线）
            if abs(angle) < 0.01:
                path = Line(ORIGIN, end_pos, color=color, stroke_width=2)
            else:
                # 简化为直线（实际应该是圆弧）
                path = CurvedArrow(
                    ORIGIN, end_pos,
                    color=color,
                    stroke_width=2,
                    angle=angle/2
                )
            
            # 后继节点
            succ_vehicle = Rectangle(width=0.4, height=0.2, color=color)
            succ_vehicle.set_fill(color, opacity=0.5)
            succ_vehicle.move_to(end_pos)
            succ_vehicle.rotate(angle)
            
            successor_paths.add(path)
            successor_nodes.add(succ_vehicle)
        
        # 动画展示扩展过程
        self.play(
            *[Create(path) for path in successor_paths],
            run_time=2
        )
        self.wait(0.3)
        
        self.play(
            *[GrowFromCenter(node) for node in successor_nodes],
            run_time=1
        )
        self.wait(0.5)
        
        # 说明文字
        explanation = Text("每个节点扩展出5个后继节点", font_size=24, color=YELLOW)
        explanation.to_edge(DOWN, buff=0.5)
        self.play(Write(explanation))
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])


# ===== 渲染指令 =====
if __name__ == "__main__":
    # 在命令行运行:
    # manim -pql lesson2_hybrid.py AStarVsHybridAStar
    # manim -pql lesson2_hybrid.py VehicleKinematicsDemo
    # manim -pql lesson2_hybrid.py HybridAStarExpansion
    pass


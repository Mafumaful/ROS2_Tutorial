"""
第3课 Manim动画: Pure Pursuit路径跟踪

包含4个教学动画场景:
1. PurePursuitOverview - Pure Pursuit整体流程示意 (⭐ 整体理解)
2. PathFollowingIntro - 路径跟踪问题介绍 (课程引入)
3. PurePursuitGeometry - Pure Pursuit几何关系 (核心概念，重点)
4. LookaheadDistanceEffect - 预瞄距离影响 (参数调优)

教学建议:
- PurePursuitOverview: 🌟 整体流程示意，帮助学生理解Pure Pursuit全貌
- PathFollowingIntro: 介绍路径跟踪与路径规划的区别
- PurePursuitGeometry: 详细讲解几何控制原理（教学重点）
  * 预瞄点的选择
  * 转向角计算公式: δ = arctan(2L·sin(α) / Ld)
  * 几何关系可视化
- LookaheadDistanceEffect: 展示参数对跟踪效果的影响
  * Ld过小: 震荡
  * Ld过大: 切弯
  * Ld适中: 平稳跟踪

核心要点:
- 预瞄距离Ld是关键参数
- Ld = k·v + Ld_min (速度自适应)
- Pure Pursuit是几何控制方法

推荐教学顺序:
  开场: PurePursuitOverview (建立整体认知)
  详解: PurePursuitGeometry (重点)
  分析: LookaheadDistanceEffect

渲染命令:
  manim -pql lesson3_pursuit.py PurePursuitOverview
  manim -pql lesson3_pursuit.py PurePursuitGeometry
"""

from manim import *
import numpy as np


# ===== 颜色配置 =====
REFERENCE_COLOR = BLUE
VEHICLE_COLOR = GREEN
LOOKAHEAD_COLOR = YELLOW
ERROR_COLOR = RED
REFERENCE_PATH_COLOR = BLUE


class PurePursuitOverview(Scene):
    """
    整体示意场景: Pure Pursuit算法流程总览
    
    教学目标:
    - 让学生从整体上理解Pure Pursuit的工作原理
    - 展示几何控制的核心思想
    - 建立预瞄点概念
    
    适用场景:
    - 课程开场（强烈推荐）⭐⭐⭐⭐⭐
    - 帮助学生建立路径跟踪的直观认识
    
    时长: ~45秒
    """
    
    def construct(self):
        # ===== 标题 =====
        title = Text("Pure Pursuit 算法整体流程", font_size=44, color=BLUE, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.8)
        
        subtitle = Text("(几何路径跟踪控制)", font_size=26, color=GRAY)
        subtitle.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(subtitle))
        self.wait(0.5)
        
        # ===== 核心思想 =====
        core_idea = VGroup(
            Text("核心思想:", font_size=30, color=YELLOW),
            Text("追踪路径上的预瞄点", font_size=26, color=WHITE),
            Text("根据几何关系计算转向角", font_size=26, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        core_idea.to_edge(LEFT, buff=0.8)
        core_idea.shift(DOWN * 0.3)
        
        self.play(Write(core_idea), run_time=2)
        self.wait(1)
        
        # ===== 示意图 =====
        # 参考路径
        path_points = []
        t = np.linspace(0, np.pi, 30)
        for i, angle in enumerate(t):
            x = 2 + angle * 0.8
            y = 0.8 * np.sin(angle) - 1
            path_points.append(np.array([x, y, 0]))
        
        ref_path = VMobject(color=REFERENCE_PATH_COLOR, stroke_width=3)
        ref_path.set_points_as_corners(path_points)
        
        self.play(Create(ref_path), run_time=1.5)
        self.wait(0.5)
        
        # 车辆
        vehicle = Rectangle(width=0.6, height=0.3, color=VEHICLE_COLOR)
        vehicle.set_fill(VEHICLE_COLOR, opacity=0.7)
        vehicle.move_to(path_points[5])
        
        arrow = Arrow(ORIGIN, RIGHT * 0.3, color=RED, buff=0)
        arrow.next_to(vehicle, RIGHT, buff=0)
        vehicle_group = VGroup(vehicle, arrow)
        
        self.play(FadeIn(vehicle_group))
        self.wait(0.5)
        
        # 预瞄点
        lookahead_point = Dot(path_points[15], color=LOOKAHEAD_COLOR, radius=0.12)
        lookahead_label = Text("预瞄点", font_size=20, color=LOOKAHEAD_COLOR)
        lookahead_label.next_to(lookahead_point, UP, buff=0.2)
        
        # 预瞄距离线
        lookahead_line = Line(
            vehicle.get_center(),
            lookahead_point.get_center(),
            color=LOOKAHEAD_COLOR,
            stroke_width=2
        )
        
        ld_label = Text("Ld", font_size=24, color=LOOKAHEAD_COLOR)
        ld_label.move_to(lookahead_line.get_center() + UP * 0.3)
        
        self.play(
            GrowFromCenter(lookahead_point),
            Write(lookahead_label),
            Create(lookahead_line),
            Write(ld_label)
        )
        self.wait(1)
        
        # ===== 控制公式 =====
        formula_box = VGroup(
            Text("控制公式:", font_size=28, color=YELLOW),
            Text("δ = arctan(2L·sin(α) / Ld)", font_size=26, color=WHITE, weight=BOLD),
            VGroup(
                Text("L: 轴距", font_size=20),
                Text("α: 航向角差", font_size=20),
                Text("Ld: 预瞄距离", font_size=20, color=LOOKAHEAD_COLOR),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        formula_box.to_corner(DR, buff=0.8)
        
        self.play(FadeIn(formula_box, shift=UP))
        self.wait(1.5)
        
        # ===== 算法步骤 =====
        steps = VGroup(
            Text("算法步骤:", font_size=26, color=YELLOW),
            Text("1. 找到最近点", font_size=22),
            Text("2. 确定预瞄点", font_size=22, color=LOOKAHEAD_COLOR),
            Text("3. 计算转向角", font_size=22),
            Text("4. 执行控制", font_size=22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        steps.next_to(core_idea, DOWN, buff=0.8, aligned_edge=LEFT)
        
        self.play(Write(steps), run_time=2)
        self.wait(2)
        
        # ===== 特点总结 =====
        summary = Text("特点: 简单、稳定、易实现", font_size=26, color=GREEN)
        summary.to_edge(DOWN, buff=0.8)
        
        self.play(Write(summary))
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class PathFollowingIntro(Scene):
    """
    动画1: 路径跟踪问题介绍
    
    展示内容:
    - 参考路径
    - 车辆当前位置
    - 横向误差和航向误差
    """
    
    def construct(self):
        # 标题
        title = Text("路径跟踪问题", font_size=44)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 参考路径（S型曲线）
        t = np.linspace(-2, 2, 100)
        path_points = np.array([
            t,
            0.5 * np.sin(2 * t),
            np.zeros_like(t)
        ]).T
        
        ref_path = VMobject(color=REFERENCE_COLOR, stroke_width=4)
        ref_path.set_points_smoothly(path_points)
        
        path_label = Text("参考路径", font_size=28, color=REFERENCE_COLOR)
        path_label.next_to(ref_path, UP, buff=0.5)
        
        self.play(Create(ref_path), Write(path_label))
        self.wait(0.5)
        
        # 车辆位置（偏离路径）
        vehicle_pos = np.array([0, -0.8, 0])
        vehicle = Rectangle(width=0.6, height=0.3, color=VEHICLE_COLOR)
        vehicle.set_fill(VEHICLE_COLOR, opacity=0.7)
        vehicle.move_to(vehicle_pos)
        
        vehicle_label = Text("车辆", font_size=24, color=VEHICLE_COLOR)
        vehicle_label.next_to(vehicle, DOWN, buff=0.3)
        
        self.play(Create(vehicle), Write(vehicle_label))
        self.wait(0.5)
        
        # 横向误差
        closest_point_on_path = np.array([0, 0, 0])
        lateral_error_line = DashedLine(
            vehicle_pos,
            closest_point_on_path,
            color=ERROR_COLOR,
            stroke_width=3
        )
        
        error_label = Text("横向误差", font_size=24, color=ERROR_COLOR)
        error_label.next_to(lateral_error_line, LEFT, buff=0.2)
        
        self.play(Create(lateral_error_line), Write(error_label))
        self.wait(0.5)
        
        # 目标文字
        goal_text = Text("目标: 使车辆跟随参考路径行驶", font_size=28)
        goal_text.to_edge(DOWN, buff=0.8)
        
        self.play(Write(goal_text))
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class PurePursuitGeometry(Scene):
    """
    动画2: Pure Pursuit几何关系
    
    展示内容:
    - 车辆当前位置
    - 预瞄点
    - 预瞄距离
    - 转向角计算
    """
    
    def construct(self):
        # 标题
        title = Text("Pure Pursuit 几何关系", font_size=44)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 显示公式
        formula = Text(
            "δ = arctan(2L·sin(α) / Ld)",
            font_size=36,
            color=WHITE
        )
        formula.next_to(title, DOWN, buff=0.3)
        self.play(Write(formula))
        self.wait(0.5)
        
        # 车辆（原点）
        vehicle = Rectangle(width=0.8, height=0.4, color=VEHICLE_COLOR)
        vehicle.set_fill(VEHICLE_COLOR, opacity=0.7)
        vehicle.move_to(ORIGIN)
        
        # 车头方向箭头
        heading_arrow = Arrow(ORIGIN, RIGHT * 1.2, color=RED, buff=0)
        heading_arrow.shift(RIGHT * 0.4)
        
        vehicle_group = VGroup(vehicle, heading_arrow)
        
        vehicle_label = Text("车辆", font_size=24, color=VEHICLE_COLOR)
        vehicle_label.next_to(vehicle, DOWN, buff=0.3)
        
        self.play(Create(vehicle_group), Write(vehicle_label))
        self.wait(0.5)
        
        # 参考路径
        t = np.linspace(0, 4, 50)
        path_points = np.array([
            t,
            0.3 * t + 0.2 * np.sin(t),
            np.zeros_like(t)
        ]).T
        
        ref_path = VMobject(color=REFERENCE_COLOR, stroke_width=3)
        ref_path.set_points_smoothly(path_points)
        
        self.play(Create(ref_path))
        self.wait(0.5)
        
        # 预瞄点
        lookahead_distance = 2.5
        lookahead_pos = np.array([lookahead_distance, 
                                  0.3 * lookahead_distance + 0.2 * np.sin(lookahead_distance), 
                                  0])
        
        lookahead_point = Dot(lookahead_pos, color=LOOKAHEAD_COLOR, radius=0.12)
        lookahead_label = Text("预瞄点", font_size=24, color=LOOKAHEAD_COLOR)
        lookahead_label.next_to(lookahead_point, UP, buff=0.2)
        
        self.play(GrowFromCenter(lookahead_point), Write(lookahead_label))
        self.wait(0.5)
        
        # 预瞄距离线
        lookahead_line = Line(ORIGIN, lookahead_pos, color=LOOKAHEAD_COLOR, stroke_width=2)
        
        ld_label = Text("Ld", font_size=32, color=LOOKAHEAD_COLOR)
        ld_label.move_to((lookahead_pos / 2) + UP * 0.3)
        
        self.play(Create(lookahead_line), Write(ld_label))
        self.wait(0.5)
        
        # 角度α
        angle_arc = Arc(
            radius=0.8,
            start_angle=0,
            angle=np.arctan2(lookahead_pos[1], lookahead_pos[0]),
            color=YELLOW
        )
        
        alpha_label = Text("α", font_size=32, color=YELLOW)
        alpha_label.move_to(RIGHT * 1.2 + UP * 0.3)
        
        self.play(Create(angle_arc), Write(alpha_label))
        self.wait(0.5)
        
        # 转向后的圆弧轨迹
        delta = np.arctan(2 * 2.7 * np.sin(angle_arc.angle) / lookahead_distance)
        
        # 简化显示：绘制朝向预瞄点的圆弧
        arc_path = CurvedArrow(
            ORIGIN,
            lookahead_pos,
            color=GREEN,
            stroke_width=3,
            angle=0.3
        )
        
        self.play(Create(arc_path))
        self.wait(0.5)
        
        # 说明文字
        explanation = Text("车辆沿圆弧接近预瞄点", font_size=24)
        explanation.to_edge(DOWN, buff=0.5)
        self.play(Write(explanation))
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class LookaheadDistanceEffect(Scene):
    """
    动画3: 预瞄距离的影响
    
    展示内容:
    - 短预瞄距离：跟踪精确但易震荡
    - 长预瞄距离：平稳但跟踪误差大
    """
    
    def construct(self):
        # 标题
        title = Text("预瞄距离的影响", font_size=44)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 参考路径（正弦曲线）
        t = np.linspace(0, 6, 100)
        path_points = np.array([
            t - 3,
            np.sin(t),
            np.zeros_like(t)
        ]).T
        
        ref_path = VMobject(color=BLUE, stroke_width=4)
        ref_path.set_points_smoothly(path_points)
        
        path_label = Text("参考路径", font_size=24, color=BLUE)
        path_label.to_corner(UL, buff=0.8)
        path_label.shift(DOWN * 0.8)
        
        self.play(Create(ref_path), Write(path_label))
        self.wait(0.5)
        
        # 短预瞄距离轨迹（震荡）
        t_short = np.linspace(0, 6, 100)
        short_traj_points = np.array([
            t_short - 3,
            np.sin(t_short) + 0.1 * np.sin(5 * t_short),  # 添加高频震荡
            np.zeros_like(t_short)
        ]).T
        
        short_traj = VMobject(color=RED, stroke_width=3)
        short_traj.set_points_smoothly(short_traj_points)
        
        short_label = Text("短预瞄", font_size=24, color=RED)
        short_label.next_to(path_label, DOWN, buff=0.3, aligned_edge=LEFT)
        
        self.play(Create(short_traj), Write(short_label), run_time=2)
        self.wait(0.5)
        
        # 长预瞄距离轨迹（平滑但偏离）
        t_long = np.linspace(0, 6, 50)
        long_traj_points = np.array([
            t_long - 3,
            0.7 * np.sin(t_long - 0.5),  # 幅度减小，相位滞后
            np.zeros_like(t_long)
        ]).T
        
        long_traj = VMobject(color=GREEN, stroke_width=3)
        long_traj.set_points_smoothly(long_traj_points)
        
        long_label = Text("长预瞄", font_size=24, color=GREEN)
        long_label.next_to(short_label, DOWN, buff=0.3, aligned_edge=LEFT)
        
        self.play(Create(long_traj), Write(long_label), run_time=2)
        self.wait(0.5)
        
        # 说明文字
        short_desc = Text("• 短预瞄: 精确但震荡", font_size=20, color=RED)
        long_desc = Text("• 长预瞄: 平稳但误差大", font_size=20, color=GREEN)
        optimal_desc = Text("• 需要根据速度调整", font_size=20, color=YELLOW)
        
        descriptions = VGroup(short_desc, long_desc, optimal_desc).arrange(
            DOWN, aligned_edge=LEFT, buff=0.2
        )
        descriptions.to_edge(DOWN, buff=0.8)
        
        self.play(Write(descriptions), run_time=2)
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


# ===== 渲染指令 =====
if __name__ == "__main__":
    # 在命令行运行:
    # manim -pql lesson3_pursuit.py PathFollowingIntro
    # manim -pql lesson3_pursuit.py PurePursuitGeometry
    # manim -pql lesson3_pursuit.py LookaheadDistanceEffect
    pass


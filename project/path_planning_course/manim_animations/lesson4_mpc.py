"""
第4课 Manim动画: MPC模型预测控制

包含4个教学动画场景:
1. MPCOverview - MPC算法整体流程示意 (⭐ 整体理解)
2. PurePursuitVsMPC - Pure Pursuit vs MPC对比 (引出MPC优势)
3. MPCPredictionHorizon - MPC预测时域演示 (核心概念，重点)
4. MPCOptimizationDemo - MPC优化过程演示 (算法原理)

教学建议:
- MPCOverview: 🌟 整体流程示意，帮助学生理解MPC的核心思想
- PurePursuitVsMPC: 对比几何控制和优化控制方法
  * Pure Pursuit: 简单但精度有限
  * MPC: 复杂但精度高、能处理约束
  
- MPCPredictionHorizon: 讲解预测时域概念（教学重点）
  * N步预测窗口的含义
  * 滚动优化策略 (Receding Horizon)
  * 只执行第一步控制
  
- MPCOptimizationDemo: 展示优化问题的构成
  * 目标函数: min Σ(‖xₖ - xᵣₑf‖²_Q + ‖uₖ‖²_R)
  * 动力学约束: xₖ₊₁ = f(xₖ, uₖ)
  * 控制约束: |δ| ≤ 35°, |a| ≤ 2 m/s²
  * 状态约束: 0 ≤ v ≤ 5 m/s

核心要点:
- MPC是基于优化的控制方法
- 预测时域N决定预见能力和计算量
- 权重矩阵Q/R决定跟踪性能
- 约束处理是MPC相对Pure Pursuit的核心优势

推荐教学顺序:
  开场: MPCOverview (建立整体认知)
  对比: PurePursuitVsMPC
  详解: MPCPredictionHorizon (重点)

渲染命令:
  manim -pql lesson4_mpc.py MPCOverview
  manim -pql lesson4_mpc.py MPCPredictionHorizon
"""

from manim import *
import numpy as np


# ===== 颜色配置 =====
REFERENCE_COLOR = BLUE
PP_COLOR = RED
MPC_COLOR = GREEN
PREDICTION_COLOR = YELLOW
PREDICTED_COLOR = YELLOW
CONTROL_COLOR = RED
CONSTRAINT_COLOR = ORANGE


class MPCOverview(Scene):
    """
    整体示意场景: MPC算法流程总览
    
    教学目标:
    - 让学生从整体上理解MPC的核心思想
    - 展示预测-优化-执行的循环过程
    - 建立滚动优化的概念
    
    适用场景:
    - 课程开场（强烈推荐）⭐⭐⭐⭐⭐
    - 帮助学生建立MPC的全局认知
    
    时长: ~50秒
    """
    
    def construct(self):
        # ===== 标题 =====
        title = Text("MPC 算法整体流程", font_size=44, color=BLUE, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.8)
        
        subtitle = Text("(Model Predictive Control - 模型预测控制)", font_size=24, color=GRAY)
        subtitle.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(subtitle))
        self.wait(0.5)
        
        # ===== 核心思想 =====
        core_concept = VGroup(
            Text("核心思想:", font_size=30, color=YELLOW),
            Text("预测未来 N 步", font_size=26, color=PREDICTED_COLOR),
            Text("优化控制序列", font_size=26, color=CONTROL_COLOR),
            Text("只执行第一步", font_size=26, color=GREEN),
            Text("滚动重复优化", font_size=26, color=ORANGE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        core_concept.to_edge(LEFT, buff=0.8)
        core_concept.shift(DOWN * 0.3)
        
        self.play(Write(core_concept), run_time=2.5)
        self.wait(1)
        
        # ===== 预测时域示意 =====
        # 时间轴
        timeline = NumberLine(
            x_range=[0, 12, 1],
            length=6,
            include_numbers=False,
            color=WHITE
        ).shift(RIGHT * 2)
        
        self.play(Create(timeline))
        
        # 当前时刻
        current_marker = Dot(timeline.n2p(0), color=GREEN, radius=0.12)
        current_label = Text("当前", font_size=20, color=GREEN)
        current_label.next_to(current_marker, DOWN, buff=0.2)
        
        self.play(GrowFromCenter(current_marker), Write(current_label))
        self.wait(0.5)
        
        # 预测时域
        horizon_range = Line(
            timeline.n2p(0),
            timeline.n2p(10),
            color=PREDICTED_COLOR,
            stroke_width=8
        )
        horizon_label = Text("预测时域 N", font_size=22, color=PREDICTED_COLOR)
        horizon_label.next_to(horizon_range, UP, buff=0.3)
        
        self.play(Create(horizon_range), Write(horizon_label))
        self.wait(0.5)
        
        # 预测点
        prediction_dots = VGroup(*[
            Dot(timeline.n2p(i), color=PREDICTED_COLOR, radius=0.06)
            for i in range(1, 11)
        ])
        
        self.play(LaggedStart(*[GrowFromCenter(d) for d in prediction_dots], lag_ratio=0.1))
        self.wait(0.5)
        
        # ===== 优化问题 =====
        opt_problem = VGroup(
            Text("优化问题:", font_size=28, color=YELLOW),
            Text("目标: min Σ(跟踪误差² + 控制代价²)", font_size=22),
            Text("约束: 动力学 + 控制限制 + 状态限制", font_size=22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        opt_problem.next_to(timeline, DOWN, buff=1.2)
        
        self.play(FadeIn(opt_problem, shift=UP), run_time=2)
        self.wait(1.5)
        
        # ===== 执行与滚动 =====
        exec_arrow = Arrow(
            current_marker.get_center(),
            timeline.n2p(1),
            color=GREEN,
            buff=0,
            stroke_width=6
        )
        exec_label = Text("执行", font_size=20, color=GREEN)
        exec_label.next_to(exec_arrow, RIGHT, buff=0.2)
        
        self.play(GrowArrow(exec_arrow), Write(exec_label))
        self.wait(0.5)
        
        # 滚动
        roll_text = Text("→ 滚动到下一时刻，重新优化", font_size=22, color=ORANGE)
        roll_text.next_to(opt_problem, DOWN, buff=0.5, aligned_edge=LEFT)
        
        self.play(Write(roll_text))
        self.wait(1.5)
        
        # ===== 关键优势 =====
        advantages = VGroup(
            Text("关键优势:", font_size=26, color=YELLOW),
            Text("✓ 预测能力强", font_size=22),
            Text("✓ 处理约束", font_size=22),
            Text("✓ 跟踪精度高", font_size=22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        advantages.to_corner(DR, buff=0.8)
        
        self.play(FadeIn(advantages, shift=UP))
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class PurePursuitVsMPC(Scene):
    """
    动画1: Pure Pursuit vs MPC对比
    
    展示内容:
    - 急转弯场景
    - Pure Pursuit切弯
    - MPC提前减速，平稳过弯
    """
    
    def construct(self):
        # 标题
        title = Text("Pure Pursuit vs MPC", font_size=44)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 分割线
        divider = Line(UP * 3, DOWN * 3, color=WHITE)
        self.play(Create(divider))
        
        # 左侧: Pure Pursuit
        pp_title = Text("Pure Pursuit", font_size=28, color=PP_COLOR)
        pp_title.to_corner(UL, buff=0.8)
        pp_title.shift(DOWN * 1.2)
        
        # 右侧: MPC
        mpc_title = Text("MPC", font_size=28, color=MPC_COLOR)
        mpc_title.to_corner(UR, buff=0.8)
        mpc_title.shift(DOWN * 1.2)
        
        self.play(Write(pp_title), Write(mpc_title))
        self.wait(0.5)
        
        # 参考路径（急转弯）
        # 左侧PP路径
        pp_ref = VMobject(color=BLUE, stroke_width=3)
        pp_t = np.linspace(0, np.pi, 30)
        pp_path_points = np.array([
            -3 + 1.5 * np.cos(pp_t),
            -1 + 1.5 * np.sin(pp_t),
            np.zeros_like(pp_t)
        ]).T
        pp_ref.set_points_smoothly(pp_path_points)
        
        # 右侧MPC路径
        mpc_ref = VMobject(color=BLUE, stroke_width=3)
        mpc_t = np.linspace(0, np.pi, 30)
        mpc_path_points = np.array([
            3 + 1.5 * np.cos(mpc_t),
            -1 + 1.5 * np.sin(mpc_t),
            np.zeros_like(mpc_t)
        ]).T
        mpc_ref.set_points_smoothly(mpc_path_points)
        
        self.play(Create(pp_ref), Create(mpc_ref))
        self.wait(0.5)
        
        # Pure Pursuit轨迹（切弯）
        pp_traj = VMobject(color=PP_COLOR, stroke_width=4)
        pp_traj_t = np.linspace(0, np.pi, 30)
        pp_traj_points = np.array([
            -3 + 1.2 * np.cos(pp_traj_t),  # 内切
            -1 + 1.2 * np.sin(pp_traj_t),
            np.zeros_like(pp_traj_t)
        ]).T
        pp_traj.set_points_smoothly(pp_traj_points)
        
        # MPC轨迹（平滑跟踪）
        mpc_traj = VMobject(color=MPC_COLOR, stroke_width=4)
        mpc_traj_t = np.linspace(0, np.pi, 30)
        mpc_traj_points = np.array([
            3 + 1.48 * np.cos(mpc_traj_t),  # 更接近参考
            -1 + 1.48 * np.sin(mpc_traj_t),
            np.zeros_like(mpc_traj_t)
        ]).T
        mpc_traj.set_points_smoothly(mpc_traj_points)
        
        # 动画展示跟踪过程
        self.play(
            Create(pp_traj),
            Create(mpc_traj),
            run_time=3
        )
        self.wait(0.5)
        
        # 添加说明
        pp_desc = Text("切弯，误差大", font_size=20, color=YELLOW)
        pp_desc.move_to(LEFT * 3 + DOWN * 2.5)
        
        mpc_desc = Text("预测未来，提前调整", font_size=20, color=YELLOW)
        mpc_desc.move_to(RIGHT * 3 + DOWN * 2.5)
        
        self.play(Write(pp_desc), Write(mpc_desc))
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class MPCPredictionHorizon(Scene):
    """
    动画2: MPC预测时域演示
    
    展示内容:
    - 当前车辆状态
    - 预测N=10步的轨迹
    - 只执行第一步
    - 滚动优化
    """
    
    def construct(self):
        # 标题
        title = Text("MPC 预测时域", font_size=44)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 显示预测时域N
        horizon_text = Text("N = 10", font_size=36, color=WHITE)
        horizon_text.next_to(title, DOWN, buff=0.3)
        self.play(Write(horizon_text))
        self.wait(0.5)
        
        # 参考路径
        t = np.linspace(0, 5, 100)
        ref_points = np.array([
            t - 2.5,
            0.3 * np.sin(t),
            np.zeros_like(t)
        ]).T
        
        ref_path = VMobject(color=REFERENCE_COLOR, stroke_width=3)
        ref_path.set_points_smoothly(ref_points)
        
        self.play(Create(ref_path))
        self.wait(0.5)
        
        # 当前车辆位置
        vehicle_pos = np.array([-2.5, 0, 0])
        vehicle = Rectangle(width=0.6, height=0.3, color=GREEN)
        vehicle.set_fill(GREEN, opacity=0.7)
        vehicle.move_to(vehicle_pos)
        
        current_label = Text("当前位置", font_size=24, color=GREEN)
        current_label.next_to(vehicle, DOWN, buff=0.3)
        
        self.play(Create(vehicle), Write(current_label))
        self.wait(0.5)
        
        # 预测未来10步
        N = 10
        prediction_points = VGroup()
        
        for i in range(1, N+1):
            pred_t = i * 0.5
            pred_x = vehicle_pos[0] + pred_t
            pred_y = 0.3 * np.sin(pred_t)
            pred_pos = np.array([pred_x, pred_y, 0])
            
            pred_dot = Dot(pred_pos, color=PREDICTION_COLOR, radius=0.08)
            pred_label = Text(f"k+{i}", font_size=16, color=PREDICTION_COLOR)
            pred_label.next_to(pred_dot, UP, buff=0.1)
            
            prediction_points.add(VGroup(pred_dot, pred_label))
        
        # 预测轨迹线
        pred_line = VMobject(color=PREDICTION_COLOR, stroke_width=2)
        pred_t = np.linspace(0, 5, 50)
        pred_line_points = np.array([
            vehicle_pos[0] + pred_t,
            0.3 * np.sin(pred_t),
            np.zeros_like(pred_t)
        ]).T
        pred_line.set_points_smoothly(pred_line_points)
        
        self.play(Create(pred_line))
        self.wait(0.3)
        
        self.play(*[FadeIn(point) for point in prediction_points], run_time=2)
        self.wait(0.5)
        
        # 高亮第一步
        first_step = prediction_points[0]
        first_highlight = Circle(radius=0.2, color=RED)
        first_highlight.move_to(first_step[0].get_center())
        
        exec_label = Text("只执行第一步", font_size=24, color=RED)
        exec_label.next_to(first_highlight, RIGHT, buff=0.5)
        
        self.play(Create(first_highlight), Write(exec_label))
        self.wait(0.5)
        
        # 移动到第一步
        new_vehicle_pos = first_step[0].get_center()
        self.play(vehicle.animate.move_to(new_vehicle_pos))
        self.wait(0.3)
        
        # 淡出旧预测，显示"重新优化"
        reoptimize_text = Text("重新优化...", font_size=28, color=YELLOW)
        reoptimize_text.to_edge(DOWN, buff=0.8)
        
        self.play(
            FadeOut(pred_line),
            FadeOut(prediction_points),
            FadeOut(first_highlight),
            Write(reoptimize_text)
        )
        self.wait(0.5)
        
        # 说明滚动时域
        explanation = Text("滚动时域: 不断重新规划", font_size=24)
        explanation.next_to(reoptimize_text, UP, buff=0.3)
        self.play(Write(explanation))
        
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class MPCOptimizationDemo(Scene):
    """
    动画3: MPC优化过程演示
    
    展示内容:
    - 优化目标（最小化误差+控制代价）
    - 约束条件
    - 求解过程
    """
    
    def construct(self):
        # 标题
        title = Text("MPC 优化问题", font_size=44)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # 目标函数
        objective = VGroup(
            Text("目标函数:", font_size=28, color=YELLOW),
            Text(
                "min Σ(||xₖ - xᵣₑf||²_Q + ||uₖ||²_R)",
                font_size=28,
                color=WHITE
            )
        ).arrange(DOWN, buff=0.3)
        objective.shift(UP * 1.5)
        
        self.play(Write(objective), run_time=2)
        self.wait(1)
        
        # 约束条件
        constraints = VGroup(
            Text("约束条件:", font_size=28, color=YELLOW),
            Text("xₖ₊₁ = f(xₖ, uₖ)", font_size=28, color=WHITE),
            Text("|δ| ≤ 35°", font_size=28, color=WHITE),
            Text("|a| ≤ 2 m/s²", font_size=28, color=WHITE),
            Text("0 ≤ v ≤ 5 m/s", font_size=28, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        constraints.shift(DOWN * 0.8)
        
        self.play(Write(constraints), run_time=3)
        self.wait(1)
        
        # 求解器
        solver_box = Rectangle(width=4, height=1, color=GREEN)
        solver_box.to_edge(DOWN, buff=1)
        
        solver_text = Text("OSQP求解器", font_size=28, color=GREEN)
        solver_text.move_to(solver_box)
        
        self.play(Create(solver_box), Write(solver_text))
        self.wait(0.5)
        
        # 显示"求解中"动画
        solving_dots = Text("...", font_size=48, color=YELLOW)
        solving_dots.next_to(solver_box, RIGHT, buff=0.5)
        
        self.play(Write(solving_dots))
        self.wait(1)
        
        # 显示结果
        result = Text("✓ 得到最优控制序列", font_size=28, color=GREEN)
        result.next_to(solver_box, DOWN, buff=0.5)
        
        self.play(
            FadeOut(solving_dots),
            Write(result)
        )
        self.wait(0.5)
        
        # 显示控制输出
        control_output = Text(
            "u* = [δ₀, a₀, δ₁, a₁, ...]",
            font_size=32,
            color=BLUE
        )
        control_output.next_to(result, DOWN, buff=0.3)
        
        self.play(Write(control_output))
        self.wait(2)
        
        self.play(*[FadeOut(mob) for mob in self.mobjects])


# ===== 渲染指令 =====
if __name__ == "__main__":
    # 在命令行运行:
    # manim -pql lesson4_mpc.py PurePursuitVsMPC
    # manim -pql lesson4_mpc.py MPCPredictionHorizon
    # manim -pql lesson4_mpc.py MPCOptimizationDemo
    pass


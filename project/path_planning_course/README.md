# 自动驾驶路径规划与跟踪教程

完整的路径规划和路径跟踪教学项目，包含从 A* 到 Hybrid A*、从 Pure Pursuit 到 MPC 的完整知识体系。

## 📚 课程概览

本课程分为 4 个核心课时，涵盖自动驾驶中的路径规划和路径跟踪两大核心技术：

| 课时 | 主题 | 核心内容 |
|------|------|---------|
| **第1课** | A* 路径规划 | 启发式搜索、网格地图、最优路径 |
| **第2课** | Hybrid A* 与车辆运动学 | 车辆运动模型、非完整约束、平滑路径 |
| **第3课** | Pure Pursuit 路径跟踪 | 几何控制、预瞄距离、横向跟踪 |
| **第4课** | MPC 模型预测控制 | 优化控制、约束处理、轨迹跟踪 |

## 🗂️ 项目结构

```
path_planning_course/
├── README.md                    # 本文件 - 项目总览和使用指南
├── requirements.txt             # Python 依赖
├── 修改总结.md                  # 最新修改说明
├── test_fixes.py                # 自动化测试脚本
│
├── algorithms/                  # 核心算法实现
│   ├── a_star.py               # A* 路径规划算法
│   └── hybrid_astar.py         # Hybrid A* 算法（考虑车辆运动学）
│
├── control/                     # 控制器实现
│   ├── pure_pursuit.py         # Pure Pursuit 路径跟踪控制器
│   └── mpc_controller.py       # MPC 模型预测控制器
│
├── vehicle/                     # 车辆模型
│   └── bicycle_model.py        # 自行车运动学模型
│
├── utils/                       # 工具函数
│   ├── helper.py               # 辅助函数
│   └── visualization.py        # 可视化工具
│
├── examples/                    # 📂 Python 示例代码（4个核心示例）
│   ├── lesson1_demo.py         # 第1课：A* 算法演示
│   ├── lesson2_demo.py         # 第2课：Hybrid A* 演示
│   ├── lesson3_demo.py         # 第3课：Pure Pursuit 演示
│   └── lesson4_demo.py         # 第4课：MPC 演示
│
└── manim_animations/            # 📂 Manim 动画代码（教学动画）
    ├── README.md               # Manim 详细使用说明
    ├── lesson1_astar.py        # 第1课动画
    ├── lesson2_hybrid.py       # 第2课动画
    ├── lesson3_pursuit.py      # 第3课动画
    └── lesson4_mpc.py          # 第4课动画
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆或进入项目目录
cd /Users/pony.ai/Documents/文档/path_planning_course

# 安装 Python 依赖
pip3 install -r requirements.txt
```

**依赖说明**:
- `numpy`: 数值计算
- `matplotlib`: 绘图和可视化
- `scipy`: 科学计算
- `cvxpy`: 凸优化（MPC 需要）
- `manim`: 动画制作（可选，仅需要制作动画时安装）

### 2. 快速验证

运行自动化测试脚本，验证所有模块是否正常：

```bash
python3 test_fixes.py
```

预期输出：
```
✓ A* 算法导入成功
✓ Hybrid A* 算法导入成功
✓ Pure Pursuit 控制器导入成功
✓ MPC 控制器导入成功
✓ 可视化工具导入成功
...
🎉 所有测试通过！
```

---

## 📂 一、Python 示例（examples/）

### 📖 目录说明

`examples/` 目录包含 4 个完整的 Python 示例，每个对应一节课的核心内容。所有示例都可以独立运行，生成可视化结果。

### 📝 示例列表

#### 第1课：A* 路径规划算法

**文件**: `examples/lesson1_demo.py`

**演示内容**:
1. 创建网格地图和障碍物
2. 运行 A* 算法进行路径规划
3. 可视化规划结果（地图 + 路径）
4. 对比不同启发式权重的影响

**运行方法**:
```bash
cd examples
python3 lesson1_demo.py
```

**输出**:
- `lesson1_result.png` - A* 路径规划结果图
- `lesson1_comparison.png` - 启发式权重对比图

**关键参数**:
- `heuristic_weight`: 启发式函数权重（0.0 = Dijkstra, 1.0 = A*, >1.0 = 加权A*）
- 地图大小: 20×20
- 障碍物: 3个矩形区域

---

#### 第2课：Hybrid A* 与车辆运动学

**文件**: `examples/lesson2_demo.py`

**演示内容**:
1. 车辆运动学模型测试（不同转向角的轨迹）
2. Hybrid A* 路径规划
3. 与传统 A* 的对比可视化
4. 车辆姿态（位置 + 航向角）展示

**运行方法**:
```bash
cd examples
python3 lesson2_demo.py
```

**输出**:
- 车辆运动学轨迹图（左转、直行、右转）
- A* vs Hybrid A* 对比图
- 控制台显示规划统计信息

**关键参数**:
- 轴距 `L`: 2.7m
- 最大转向角: ±35°
- 地图分辨率: 0.5m

---

#### 第3课：Pure Pursuit 路径跟踪

**文件**: `examples/lesson3_demo.py`

**演示内容**:
1. 不同预瞄距离的跟踪效果对比（Ld = 2.0m, 4.0m, 6.0m）
2. 圆形路径跟踪测试
3. S 型弯道跟踪测试
4. 跟踪误差分析和性能评估

**运行方法**:
```bash
cd examples
python3 lesson3_demo.py
```

**输出**:
- 不同预瞄距离的轨迹对比图
- 圆形路径跟踪结果
- S 型弯道跟踪结果
- 横向误差曲线图

**关键参数**:
- `k_lookahead`: 预瞄距离系数（默认 1.0）
- `ld_min`: 最小预瞄距离（默认 2.0m）
- 目标速度: 2.0 m/s

---

#### 第4课：MPC 模型预测控制

**文件**: `examples/lesson4_demo.py`

**演示内容**:
1. MPC 基础测试（圆形轨迹跟踪）
2. MPC vs Pure Pursuit 性能对比
3. 不同权重矩阵 Q/R 的影响分析
4. 约束处理演示（速度、加速度、转向角限制）

**运行方法**:
```bash
cd examples
python3 lesson4_demo.py
```

**输出**:
- MPC 轨迹跟踪结果（4 子图：轨迹、转向角、加速度、速度）
- MPC vs Pure Pursuit 对比图
- 不同权重配置的性能对比
- 约束处理效果展示

**关键参数**:
- 预测时域 `N`: 10 步
- 控制周期 `dt`: 0.1s
- 权重矩阵 `Q`: [1.0, 1.0, 0.5, 0.1]（位置、角度、速度权重）
- 权重矩阵 `R`: [0.1, 0.1]（转向、加速度权重）

---

### 🎨 中文支持说明

所有示例都已配置中文字体支持：

```python
# 自动配置的字体（按优先级）
plt.rcParams['font.sans-serif'] = [
    'PingFang SC',      # macOS 默认中文字体
    'Heiti SC',         # macOS 黑体
    'STHeiti',          # macOS 华文黑体
    'Arial Unicode MS'  # 通用 Unicode 字体
]
```

如果图表中文仍显示为方框，请检查系统字体安装。

---

### 🔧 通用参数说明

所有示例都使用相同的车辆参数：

| 参数 | 符号 | 值 | 单位 | 说明 |
|------|------|-----|------|------|
| 轴距 | L | 2.7 | m | 前后轮轴距离 |
| 最大转向角 | δ_max | 35 | ° | 前轮最大转向角度 |
| 最大速度 | v_max | 5.0 | m/s | 车辆最大行驶速度 |
| 最大加速度 | a_max | 2.0 | m/s² | 最大加速/减速度 |
| 车身宽度 | - | 1.8 | m | 用于可视化 |

---

## 🎬 二、Manim 动画（manim_animations/）

### 📖 目录说明

`manim_animations/` 目录包含 4 节课的教学动画，使用 Manim 制作高质量的数学和算法可视化。

**✨ 特别说明**:
- ✅ **无需安装 LaTeX** - 所有公式使用纯文本 + Unicode 符号
- ✅ **渲染速度快** - Text 渲染比 MathTex 快 5-10 倍
- ✅ **中文完美支持** - 中文和公式可以混合显示
- ✅ **跨平台兼容** - Windows/macOS/Linux 都可运行

### 🎥 动画场景列表

#### 第1课动画：A* 路径规划（5个场景）

**文件**: `manim_animations/lesson1_astar.py`

**动画场景**:

| 场景类名 | 内容描述 | 时长 | 教学用途 | 推荐度 |
|---------|---------|------|---------|--------|
| `AStarOverview` | 🌟 **算法整体流程示意** | ~45s | **开场必看** | ⭐⭐⭐⭐⭐ |
| `PathPlanningIntro` | 路径规划问题引入 | ~30s | 课程开场 | ⭐⭐⭐ |
| `SearchSpaceDemo` | 搜索空间和启发式 | ~40s | 解释原理 | ⭐⭐⭐⭐ |
| `AStarVisualization` | A*完整搜索演示 | ~60s | **重点教学** | ⭐⭐⭐⭐⭐ |
| `AStarGridSearch` | A*快速回顾 | ~30s | 课程总结 | ⭐⭐⭐ |

**教学建议**: 
- 🌟 **强烈推荐先播放** `AStarOverview`，建立算法整体认知
- 重点场景 `AStarVisualization`，需详细讲解 f(n)=g(n)+h(n) 的计算过程

**渲染示例**:
```bash
cd manim_animations

# 整体流程示意（开场推荐）⭐
manim -pql lesson1_astar.py AStarOverview

# 重点场景（详细讲解）
manim -pql lesson1_astar.py AStarVisualization

# 完整教学流程
manim -pql lesson1_astar.py AStarOverview
manim -pql lesson1_astar.py PathPlanningIntro
manim -pql lesson1_astar.py SearchSpaceDemo
manim -pql lesson1_astar.py AStarVisualization
manim -pql lesson1_astar.py AStarGridSearch
```

---

#### 第2课动画：Hybrid A* 与车辆运动学（4个场景）

**文件**: `manim_animations/lesson2_hybrid.py`

**动画场景**:

| 场景类名 | 内容描述 | 时长 | 教学用途 | 推荐度 |
|---------|---------|------|---------|--------|
| `HybridAStarOverview` | 🌟 **算法整体流程示意** | ~50s | **开场必看** | ⭐⭐⭐⭐⭐ |
| `CompareAStarHybridAStar` | A* vs Hybrid A*对比 | ~45s | 引出问题 | ⭐⭐⭐⭐ |
| `VehicleKinematicsDemo` | 车辆运动学详解 | ~50s | **重点教学** | ⭐⭐⭐⭐⭐ |
| `HybridAStarExpansion` | Hybrid A*扩展 | ~60s | 算法细节 | ⭐⭐⭐ |

**教学建议**: 
- 🌟 **强烈推荐先播放** `HybridAStarOverview`，理解Hybrid A*全貌和车辆运动学约束概念
- 重点场景 `VehicleKinematicsDemo`，需讲解运动学方程的物理意义和非完整约束

**核心公式**（纯文本显示）:
- `ẋ = v · cos(θ)` - X 方向速度
- `ẏ = v · sin(θ)` - Y 方向速度
- `θ̇ = v · tan(δ) / L` - 航向角变化率
- `R_min = L / tan(δ_max)` - 最小转弯半径

**渲染示例**:
```bash
cd manim_animations

# 整体流程示意（开场推荐）⭐
manim -pql lesson2_hybrid.py HybridAStarOverview

# 重点场景（详细讲解）
manim -pql lesson2_hybrid.py VehicleKinematicsDemo

# 完整教学流程
manim -pql lesson2_hybrid.py HybridAStarOverview
manim -pql lesson2_hybrid.py CompareAStarHybridAStar
manim -pql lesson2_hybrid.py VehicleKinematicsDemo
```

---

#### 第3课动画：Pure Pursuit 路径跟踪（4个场景）

**文件**: `manim_animations/lesson3_pursuit.py`

**动画场景**:

| 场景类名 | 内容描述 | 时长 | 教学用途 | 推荐度 |
|---------|---------|------|---------|--------|
| `PurePursuitOverview` | 🌟 **算法整体流程示意** | ~45s | **开场必看** | ⭐⭐⭐⭐⭐ |
| `PathFollowingIntro` | 路径跟踪问题引入 | ~30s | 课程开场 | ⭐⭐⭐ |
| `PurePursuitGeometry` | 几何关系详解 | ~50s | **重点教学** | ⭐⭐⭐⭐⭐ |
| `LookaheadDistanceEffect` | 预瞄距离影响 | ~60s | 参数调优 | ⭐⭐⭐⭐ |

**教学建议**: 
- 🌟 **强烈推荐先播放** `PurePursuitOverview`，建立几何控制和预瞄点的直观认识
- 重点场景 `PurePursuitGeometry`，需详细讲解几何控制原理和公式推导过程

**核心公式**（纯文本显示）:
- `δ = arctan(2L·sin(α) / Ld)` - Pure Pursuit 控制律
- `Ld = k·v + Ld_min` - 预瞄距离计算（速度自适应）

**关键概念**:
- 预瞄距离Ld过小 → 震荡
- 预瞄距离Ld过大 → 切弯
- 预瞄距离Ld适中 → 平稳跟踪

**渲染示例**:
```bash
cd manim_animations

# 整体流程示意（开场推荐）⭐
manim -pql lesson3_pursuit.py PurePursuitOverview

# 重点场景（详细讲解）
manim -pql lesson3_pursuit.py PurePursuitGeometry

# 完整教学流程
manim -pql lesson3_pursuit.py PurePursuitOverview
manim -pql lesson3_pursuit.py PathFollowingIntro
manim -pql lesson3_pursuit.py PurePursuitGeometry
manim -pql lesson3_pursuit.py LookaheadDistanceEffect
```

---

#### 第4课动画：MPC 模型预测控制（4个场景）

**文件**: `manim_animations/lesson4_mpc.py`

**动画场景**:

| 场景类名 | 内容描述 | 时长 | 教学用途 | 推荐度 |
|---------|---------|------|---------|--------|
| `MPCOverview` | 🌟 **算法整体流程示意** | ~50s | **开场必看** | ⭐⭐⭐⭐⭐ |
| `PurePursuitVsMPC` | 控制方法对比 | ~45s | 引出MPC | ⭐⭐⭐⭐ |
| `MPCPredictionHorizon` | 预测时域详解 | ~50s | **重点教学** | ⭐⭐⭐⭐⭐ |
| `MPCOptimizationDemo` | 优化问题展示 | ~60s | 算法原理 | ⭐⭐⭐⭐ |

**教学建议**: 
- 🌟 **强烈推荐先播放** `MPCOverview`，理解MPC的预测-优化-执行循环和滚动优化概念
- 重点场景 `MPCPredictionHorizon`，需讲解滚动优化策略，这是MPC的核心思想

**核心公式**（纯文本显示）:
- 目标函数: `min Σ(‖xₖ - xᵣₑf‖²_Q + ‖uₖ‖²_R)`
- 动力学约束: `xₖ₊₁ = f(xₖ, uₖ)`
- 控制约束: `|δ| ≤ 35°`, `|a| ≤ 2 m/s²`
- 状态约束: `0 ≤ v ≤ 5 m/s`

**关键概念**:
- 预测时域N：决定预见能力（典型值：10-20步）
- 权重矩阵Q/R：决定跟踪性能和控制平滑度
- 滚动优化：每步只执行第一个控制，然后重新优化

**渲染示例**:
```bash
cd manim_animations

# 整体流程示意（开场推荐）⭐
manim -pql lesson4_mpc.py MPCOverview

# 重点场景（详细讲解）
manim -pql lesson4_mpc.py MPCPredictionHorizon

# 完整教学流程
manim -pql lesson4_mpc.py MPCOverview
manim -pql lesson4_mpc.py PurePursuitVsMPC
manim -pql lesson4_mpc.py MPCPredictionHorizon
manim -pql lesson4_mpc.py MPCOptimizationDemo
```

---

### 🛠️ Manim 安装

**无需安装 LaTeX！**

```bash
# macOS
brew install py3cairo ffmpeg
pip3 install manim

# Ubuntu/Debian
sudo apt-get install libcairo2-dev libpango1.0-dev ffmpeg
pip3 install manim

# Windows
# 推荐使用 Chocolatey
choco install manimce

# 或使用 conda（跨平台）
conda install -c conda-forge manim
```

### 📹 渲染质量选项

| 参数 | 分辨率 | 帧率 | 用途 | 速度 |
|------|--------|------|------|------|
| `-ql` | 480p | 15fps | 快速预览 | ⚡⚡⚡ |
| `-qm` | 720p | 30fps | 一般质量 | ⚡⚡ |
| `-qh` | 1080p | 60fps | 高质量 | ⚡ |
| `-qk` | 2160p | 60fps | 4K 输出 | 🐌 |

**其他常用参数**:
- `-p`: 渲染后自动播放
- `-s`: 只保存最后一帧（生成缩略图）
- `-a`: 渲染文件中的所有场景
- `--format=gif`: 输出 GIF 格式

**示例**:
```bash
# 低质量预览 + 自动播放
manim -pql lesson1_astar.py AStarVisualization

# 高质量输出（不自动播放）
manim -qh lesson1_astar.py AStarVisualization

# 输出 GIF
manim -ql lesson1_astar.py AStarVisualization --format=gif
```

### 📁 输出位置

渲染的视频保存在 `manim_animations/media/videos/` 目录：

```
manim_animations/
└── media/
    └── videos/
        ├── lesson1_astar/
        │   ├── 480p15/          # -ql 输出
        │   ├── 720p30/          # -qm 输出
        │   └── 1080p60/         # -qh 输出
        ├── lesson2_hybrid/
        ├── lesson3_pursuit/
        └── lesson4_mpc/
```

---

## 🎯 学习路径建议

### 初学者路径

1. **第1课 - A* 算法**
   - 先运行: `python3 examples/lesson1_demo.py`
   - 再观看: `manim -pql manim_animations/lesson1_astar.py AStarVisualization`
   - 理解: 启发式搜索、f(n)=g(n)+h(n)

2. **第2课 - Hybrid A***
   - 先运行: `python3 examples/lesson2_demo.py`
   - 再观看: `manim -pql manim_animations/lesson2_hybrid.py VehicleKinematicsDemo`
   - 理解: 车辆运动学、非完整约束

3. **第3课 - Pure Pursuit**
   - 先运行: `python3 examples/lesson3_demo.py`
   - 再观看: `manim -pql manim_animations/lesson3_pursuit.py PurePursuitGeometry`
   - 理解: 几何控制、预瞄点

4. **第4课 - MPC**
   - 先运行: `python3 examples/lesson4_demo.py`
   - 再观看: `manim -pql manim_animations/lesson4_mpc.py MPCPredictionHorizon`
   - 理解: 优化控制、预测时域

### 进阶学习

- 修改 `examples/` 中的参数，观察算法行为变化
- 阅读算法源码: `algorithms/` 和 `control/`
- 尝试自己实现新的路径类型或障碍物配置
- 研究 MPC 权重矩阵调参对性能的影响

## 📊 性能对比

| 算法 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **A*** | 简单高效、保证最优 | 不考虑车辆约束、路径不平滑 | 网格地图、初步规划 |
| **Hybrid A*** | 考虑车辆运动学、路径可执行 | 计算量大、参数较多 | 停车场、狭窄空间 |
| **Pure Pursuit** | 简单稳定、易于实现 | 跟踪精度一般、无法处理约束 | 高速公路、简单道路 |
| **MPC** | 精度高、处理约束、预测能力强 | 计算量大、调参复杂 | 精确跟踪、复杂场景 |

---

## 🤝 贡献与反馈

如果您发现任何问题或有改进建议，欢迎：
- 提交 Issue
- 发送反馈邮件
- 提交 Pull Request

---

## 📜 许可证

本项目仅用于教学目的。

---

## 🙏 致谢

感谢所有为路径规划和自动驾驶控制理论做出贡献的研究者。

---

**最后更新**: 2025-10-29  
**版本**: 2.0


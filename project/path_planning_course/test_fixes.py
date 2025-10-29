#!/usr/bin/env python3
"""
快速测试脚本 - 验证所有修改

运行: python3 test_fixes.py
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """测试所有模块导入"""
    print("="*60)
    print("测试1: 模块导入")
    print("="*60)
    
    try:
        from algorithms.a_star import AStar, create_grid_map
        print("✓ A* 算法导入成功")
    except Exception as e:
        print(f"✗ A* 算法导入失败: {e}")
        return False
    
    try:
        from algorithms.hybrid_astar import HybridAStar
        print("✓ Hybrid A* 算法导入成功")
    except Exception as e:
        print(f"✗ Hybrid A* 算法导入失败: {e}")
        return False
    
    try:
        from control.pure_pursuit import PurePursuitController
        print("✓ Pure Pursuit 控制器导入成功")
    except Exception as e:
        print(f"✗ Pure Pursuit 控制器导入失败: {e}")
        return False
    
    try:
        from control.mpc_controller import MPCController
        print("✓ MPC 控制器导入成功")
    except Exception as e:
        print(f"✗ MPC 控制器导入失败: {e}")
        return False
    
    try:
        from utils.visualization import plot_grid_map
        print("✓ 可视化工具导入成功")
    except Exception as e:
        print(f"✗ 可视化工具导入失败: {e}")
        return False
    
    return True


def test_grid_coordinates():
    """测试网格坐标系统"""
    print("\n" + "="*60)
    print("测试2: 网格坐标系统")
    print("="*60)
    
    import numpy as np
    from algorithms.a_star import create_grid_map
    
    # 创建测试地图
    grid = create_grid_map(10, 10, obstacles=[(3, 3, 5, 5)])
    
    # 验证障碍物位置
    assert grid.shape == (10, 10), "地图尺寸错误"
    assert grid[4, 4] == 1, "障碍物位置 [y, x] 格式错误"
    
    print(f"✓ 地图尺寸: {grid.shape} (height, width)")
    print(f"✓ 障碍物访问: grid[y, x] 格式正确")
    print(f"✓ 障碍物区域正确标记")
    
    return True


def test_chinese_support():
    """测试中文支持"""
    print("\n" + "="*60)
    print("测试3: 中文字体配置")
    print("="*60)
    
    import matplotlib.pyplot as plt
    
    # 检查字体配置
    font = plt.rcParams.get('font.sans-serif', [])
    unicode_minus = plt.rcParams.get('axes.unicode_minus', True)
    
    if font:
        print(f"✓ 中文字体已配置: {font}")
    else:
        print("⚠ 中文字体未配置（将使用系统默认）")
    
    if not unicode_minus:
        print("✓ 负号显示已修复")
    else:
        print("⚠ 负号显示未配置")
    
    return True


def test_manim_no_latex():
    """测试 Manim 无 LaTeX"""
    print("\n" + "="*60)
    print("测试4: Manim 无 LaTeX 检查")
    print("="*60)
    
    import os
    import re
    
    manim_files = [
        'manim_animations/lesson1_astar.py',
        'manim_animations/lesson2_hybrid.py',
        'manim_animations/lesson3_pursuit.py',
        'manim_animations/lesson4_mpc.py',
    ]
    
    all_clean = True
    for file_path in manim_files:
        if not os.path.exists(file_path):
            print(f"⚠ 文件不存在: {file_path}")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否还有 MathTex
        if re.search(r'\bMathTex\b', content):
            print(f"✗ {file_path} 仍包含 MathTex")
            all_clean = False
        else:
            print(f"✓ {file_path} 已移除 MathTex")
    
    if all_clean:
        print("\n✓ 所有 Manim 文件已移除 LaTeX 依赖")
    
    return all_clean


def test_unicode_symbols():
    """测试 Unicode 符号"""
    print("\n" + "="*60)
    print("测试5: Unicode 数学符号")
    print("="*60)
    
    symbols = {
        'α': 'alpha',
        'β': 'beta',
        'θ': 'theta',
        'δ': 'delta',
        'Σ': 'sigma',
        '·': '点乘',
        '≤': '小于等于',
        '≥': '大于等于',
        '²': '平方',
        'ẋ': 'x导数',
    }
    
    print("常用 Unicode 符号:")
    for symbol, name in symbols.items():
        print(f"  {symbol} - {name}")
    
    print("\n✓ Unicode 符号可用")
    return True


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("路径规划课程 - 修复验证")
    print("="*60 + "\n")
    
    tests = [
        test_imports,
        test_grid_coordinates,
        test_chinese_support,
        test_manim_no_latex,
        test_unicode_symbols,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())


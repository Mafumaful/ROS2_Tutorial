"""
Lesson 2 Complete Example: Hybrid A* and Vehicle Kinematics

Demonstration Content:
1. Vehicle kinematics model test
2. Hybrid A* path planning
3. Comparison with traditional A*
4. Visualization of planning results
"""

import sys
sys.path.append('..')

import numpy as np
import matplotlib.pyplot as plt
from vehicle.bicycle_model import BicycleModel, plot_vehicle
from algorithms.hybrid_astar import HybridAStar
from algorithms.a_star import AStar, create_grid_map

def demo_vehicle_kinematics():
    """Demo 1: Vehicle Kinematics"""
    print("\n" + "="*60)
    print("Demo 1: Vehicle Kinematics Model")
    print("="*60)
    
    vehicle = BicycleModel(L=2.7)
    
    # Test trajectories with different steering angles
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    test_cases = [
        {"steer": 0, "title": "Straight Driving (δ=0°)", "color": "blue"},
        {"steer": np.deg2rad(15), "title": "Small Turn (δ=15°)", "color": "green"},
        {"steer": np.deg2rad(35), "title": "Maximum Turn (δ=35°)", "color": "red"},
    ]
    
    for ax, case in zip(axes, test_cases):
        state = np.array([0, 0, 0, 2.0])  # Initial state
        trajectory = [state.copy()]
        
        # Simulation
        for _ in range(100):
            control = [case["steer"], 0]
            state = vehicle.step(state, control, dt=0.1)
            trajectory.append(state.copy())
        
        trajectory = np.array(trajectory)
        
        # Plot trajectory
        ax.plot(trajectory[:, 0], trajectory[:, 1], 
               color=case["color"], linewidth=2, label='Trajectory')
        ax.scatter(0, 0, c='green', s=100, marker='o', label='Start', zorder=5)
        
        # Plot vehicle poses
        for i in [0, 25, 50, 75, 99]:
            plot_vehicle(ax, trajectory[i], L=2.7, color=case["color"])
        
        # Show turning radius if turning
        if case["steer"] != 0:
            R = vehicle.calc_turning_radius(case["steer"])
            ax.text(0.5, 0.95, f"Turning Radius: {R:.2f}m", 
                   transform=ax.transAxes, fontsize=11,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_title(case["title"], fontsize=14, fontweight='bold')
        ax.set_xlabel('X (m)', fontsize=11)
        ax.set_ylabel('Y (m)', fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
    
    plt.tight_layout()
    plt.savefig('lesson2_vehicle_kinematics.png', dpi=150, bbox_inches='tight')
    print("  Saved image: lesson2_vehicle_kinematics.png")
    plt.show()


def demo_hybrid_astar_vs_astar():
    """Demo 2: Hybrid A* vs Traditional A*"""
    print("\n" + "="*60)
    print("Demo 2: Hybrid A* vs Traditional A*")
    print("="*60)
    
    # Create map
    grid = np.zeros((25, 25))
    grid[10:15, 10:15] = 1  # Obstacles
    
    # Start and goal
    start_2d = (3, 3)
    goal_2d = (20, 20)
    start_3d = (3.0, 3.0, 0.0, 0.0)
    goal_3d = (20.0, 20.0, np.pi/4, 0.0)
    
    # Run A*
    print("\nRunning traditional A*...")
    astar = AStar(grid, start_2d, goal_2d)
    astar_path = astar.plan(verbose=True)
    
    # Run Hybrid A*
    print("\nRunning Hybrid A*...")
    vehicle = BicycleModel(L=2.7)
    hybrid = HybridAStar(vehicle, grid, xy_resolution=1.0, yaw_resolution=np.deg2rad(45))
    hybrid_path = hybrid.plan(start_3d, goal_3d, verbose=True)
    
    # Visualization comparison
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Subplot 1: A* result
    ax1 = axes[0]
    ax1.imshow(grid, origin='lower', cmap='binary', alpha=0.3)
    if astar_path:
        path_array = np.array(astar_path)
        ax1.plot(path_array[:, 0], path_array[:, 1], 'b-', linewidth=2, label='A* Path')
    ax1.scatter(start_2d[0], start_2d[1], c='green', s=200, marker='o', label='Start', zorder=5)
    ax1.scatter(goal_2d[0], goal_2d[1], c='red', s=200, marker='*', label='Goal', zorder=5)
    ax1.set_title('Traditional A* (Jagged Path)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('X (m)', fontsize=12)
    ax1.set_ylabel('Y (m)', fontsize=12)
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    
    # Subplot 2: Hybrid A* result
    ax2 = axes[1]
    ax2.imshow(grid, origin='lower', cmap='binary', alpha=0.3)
    if hybrid_path is not None:
        ax2.plot(hybrid_path[:, 0], hybrid_path[:, 1], 'r-', linewidth=2, label='Hybrid A* Path')
        # Plot vehicle orientations
        step = len(hybrid_path) // 10
        for i in range(0, len(hybrid_path), step):
            x, y, theta = hybrid_path[i, :3]
            dx = np.cos(theta) * 1.5
            dy = np.sin(theta) * 1.5
            ax2.arrow(x, y, dx, dy, head_width=0.6, head_length=0.4,
                     fc='blue', ec='blue', alpha=0.6)
    ax2.scatter(start_3d[0], start_3d[1], c='green', s=200, marker='o', label='Start', zorder=5)
    ax2.scatter(goal_3d[0], goal_3d[1], c='red', s=200, marker='*', label='Goal', zorder=5)
    ax2.set_title('Hybrid A* (With Vehicle Constraints)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('X (m)', fontsize=12)
    ax2.set_ylabel('Y (m)', fontsize=12)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.axis('equal')
    
    plt.tight_layout()
    plt.savefig('lesson2_astar_comparison.png', dpi=150, bbox_inches='tight')
    print("\n  Saved image: lesson2_astar_comparison.png")
    plt.show()
    
    # Performance comparison
    if astar_path and hybrid_path is not None:
        print("\n" + "="*60)
        print("Performance Comparison")
        print("="*60)
        print(f"\nTraditional A*:")
        print(f"  Path points: {len(astar_path)}")
        print(f"  Nodes expanded: {astar.nodes_expanded}")
        
        print(f"\nHybrid A*:")
        print(f"  Path points: {len(hybrid_path)}")
        print(f"  Nodes expanded: {hybrid.nodes_expanded}")
        print(f"\nNote: Hybrid A* produces smoother paths, suitable for direct vehicle control!")


def main():
    print("="*60)
    print("Lesson 2: Hybrid A* and Vehicle Kinematics - Full Demonstration")
    print("="*60)
    
    # Demo 1
    demo_vehicle_kinematics()
    
    # Demo 2
    demo_hybrid_astar_vs_astar()
    
    print("\n" + "="*60)
    print("Demonstration completed!")
    print("="*60)


if __name__ == "__main__":
    main()

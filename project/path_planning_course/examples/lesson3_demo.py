"""
Lesson 3 Complete Example: Pure Pursuit Path Tracking

Demonstration Content:
1. Pure Pursuit controller test
2. Effect of different lookahead distances
3. Tracking different path types
4. Performance analysis
"""

import sys
sys.path.append('..')

import numpy as np
import matplotlib.pyplot as plt
from control.pure_pursuit import PurePursuitController, PathFollowingSimulator
from vehicle.bicycle_model import BicycleModel
from utils.helper import create_circular_path, create_s_curve_path

def demo_lookahead_distance_effect():
    """Demo 1: Effect of lookahead distance"""
    print("\n" + "="*60)
    print("Demo 1: Effect of lookahead distance")
    print("="*60)
    
    # Create an S-curve reference path
    ref_path = create_s_curve_path(length=30, num_points=150, velocity=3.0)
    
    # Test different lookahead parameters
    configs = [
        {"k": 0.5, "ld_min": 2.0, "label": "Short Lookahead (k=0.5)", "color": "red"},
        {"k": 1.0, "ld_min": 3.0, "label": "Medium Lookahead (k=1.0)", "color": "green"},
        {"k": 2.0, "ld_min": 4.0, "label": "Long Lookahead (k=2.0)", "color": "blue"},
    ]
    
    vehicle = BicycleModel(L=2.7)
    initial_state = np.array([0, 0, 0, 3.0])
    
    results = []
    
    for config in configs:
        print(f"\nTest config: {config['label']}")
        
        controller = PurePursuitController(
            wheelbase=2.7,
            k_lookahead=config["k"],
            ld_min=config["ld_min"]
        )
        
        simulator = PathFollowingSimulator(controller, vehicle, dt=0.1)
        trajectory, info = simulator.simulate(initial_state, ref_path[:, :2], max_steps=300)
        
        print(f"  Mean lateral error: {info['mean_lateral_error']:.3f} m")
        print(f"  Max lateral error: {info['max_lateral_error']:.3f} m")
        
        results.append({
            **config,
            "trajectory": trajectory,
            "info": info,
            "controller": controller
        })
    
    # Visualization
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Subplot 1: Trajectory comparison
    ax1 = axes[0, 0]
    ax1.plot(ref_path[:, 0], ref_path[:, 1], 'k--', linewidth=2, 
            alpha=0.5, label='Reference Path')
    
    for result in results:
        traj = result["trajectory"]
        ax1.plot(traj[:, 0], traj[:, 1], color=result["color"],
                linewidth=2, label=result["label"])
    
    ax1.scatter(initial_state[0], initial_state[1], c='green', 
               s=150, marker='o', label='Start', zorder=5)
    ax1.set_xlabel('X (m)', fontsize=12)
    ax1.set_ylabel('Y (m)', fontsize=12)
    ax1.set_title('Trajectory Comparison', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    
    # Subplot 2: Lateral error comparison
    ax2 = axes[0, 1]
    for result in results:
        errors = result["controller"].lateral_errors
        time = np.arange(len(errors)) * 0.1
        ax2.plot(time, errors, color=result["color"], 
                linewidth=2, label=result["label"])
    
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Lateral Error (m)', fontsize=12)
    ax2.set_title('Lateral Error Over Time', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # Subplot 3: Mean error comparison
    ax3 = axes[1, 0]
    labels = [r["label"] for r in results]
    avg_errors = [r["info"]["mean_lateral_error"] for r in results]
    colors = [r["color"] for r in results]
    
    bars = ax3.bar(range(len(labels)), avg_errors, color=colors, alpha=0.7)
    ax3.set_xticks(range(len(labels)))
    ax3.set_xticklabels(labels, rotation=15, ha='right')
    ax3.set_ylabel('Mean Lateral Error (m)', fontsize=12)
    ax3.set_title('Performance Comparison', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Annotate values
    for bar, val in zip(bars, avg_errors):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.3f}m', ha='center', va='bottom', fontsize=10)
    
    # Subplot 4: Steering angle comparison
    ax4 = axes[1, 1]
    for result in results:
        controls = result["controller"].control_history
        time = np.arange(len(controls)) * 0.1
        ax4.plot(time, np.rad2deg(controls), color=result["color"],
                linewidth=2, label=result["label"])
    
    ax4.axhline(y=35, color='gray', linestyle='--', alpha=0.5, label='Max Steering Angle')
    ax4.axhline(y=-35, color='gray', linestyle='--', alpha=0.5)
    ax4.set_xlabel('Time (s)', fontsize=12)
    ax4.set_ylabel('Steering Angle (°)', fontsize=12)
    ax4.set_title('Steering Control', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lesson3_lookahead_comparison.png', dpi=150, bbox_inches='tight')
    print("\n  Saved image: lesson3_lookahead_comparison.png")
    plt.show()


def demo_different_paths():
    """Demo 2: Tracking different path types"""
    print("\n" + "="*60)
    print("Demo 2: Tracking different path types")
    print("="*60)
    
    # Create different types of paths
    paths = {
        "Circle": create_circular_path(radius=10, num_points=100, velocity=3.0),
        "S-curve": create_s_curve_path(length=25, num_points=120, velocity=3.0),
    }
    
    vehicle = BicycleModel(L=2.7)
    controller = PurePursuitController(wheelbase=2.7, k_lookahead=1.0, ld_min=3.0)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    for (path_name, ref_path), ax in zip(paths.items(), axes):
        print(f"\nTesting path: {path_name}")
        
        controller.reset_statistics()
        simulator = PathFollowingSimulator(controller, vehicle, dt=0.1)
        
        if path_name == "Circle":
            initial_state = np.array([10, 0, np.pi/2, 3.0])
        else:
            initial_state = np.array([0, 0, 0, 3.0])
        
        trajectory, info = simulator.simulate(initial_state, ref_path[:, :2], max_steps=400)
        
        print(f"  Mean lateral error: {info['mean_lateral_error']:.3f} m")
        print(f"  Max lateral error: {info['max_lateral_error']:.3f} m")
        
        # Plot
        ax.plot(ref_path[:, 0], ref_path[:, 1], 'b--', 
               linewidth=2, alpha=0.7, label='Reference Path')
        ax.plot(trajectory[:, 0], trajectory[:, 1], 'r-', 
               linewidth=2, label='Actual Trajectory')
        ax.scatter(initial_state[0], initial_state[1], c='green',
                  s=150, marker='o', label='Start', zorder=5)
        
        # Plot vehicle poses
        for i in range(0, len(trajectory)):
            x, y, theta = trajectory[i, :3]
            dx = np.cos(theta) * 1.2
            dy = np.sin(theta) * 1.2
            ax.arrow(x, y, dx, dy, head_width=0.5, head_length=0.3,
                    fc='blue', ec='blue', alpha=0.5)
        
        ax.set_title(f'{path_name} Path Tracking', fontsize=14, fontweight='bold')
        ax.set_xlabel('X (m)', fontsize=12)
        ax.set_ylabel('Y (m)', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        # Add performance annotations
        info_text = f"Mean Error: {info['mean_lateral_error']:.3f}m\n"
        info_text += f"Max Error: {info['max_lateral_error']:.3f}m"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('lesson3_different_paths.png', dpi=150, bbox_inches='tight')
    print("\n  Saved image: lesson3_different_paths.png")
    plt.show()


def main():
    print("="*60)
    print("Lesson 3: Pure Pursuit Path Tracking - Full Demonstration")
    print("="*60)
    
    # Demo 1
    demo_lookahead_distance_effect()
    
    # Demo 2
    demo_different_paths()
    
    print("\n" + "="*60)
    print("Demonstration completed!")
    print("="*60)
    print("\nKey Findings:")
    print("  • Lookahead too short → precise tracking but oscillatory")
    print("  • Lookahead too long → smooth motion but larger tracking error")
    print("  • Optimal parameters depend on speed and path curvature")


if __name__ == "__main__":
    main()

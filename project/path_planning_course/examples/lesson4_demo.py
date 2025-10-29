"""
Lesson 4 Complete Example: MPC (Model Predictive Control)

Demonstration Content:
1. Basic MPC controller test
2. MPC vs Pure Pursuit performance comparison
3. Effect of different weighting matrices
4. Constraint handling demo
"""

import sys
sys.path.append('..')

import numpy as np
import matplotlib.pyplot as plt
from control.mpc_controller import MPCController
from control.pure_pursuit import PurePursuitController, PathFollowingSimulator
from vehicle.bicycle_model import BicycleModel
from utils.helper import create_circular_path, create_s_curve_path

def demo_mpc_basic():
    """Demo 1: Basic MPC test"""
    print("\n" + "="*60)
    print("Demo 1: Basic MPC controller test")
    print("="*60)
    
    # Create controller
    vehicle = BicycleModel(L=2.7)
    mpc = MPCController(
        wheelbase=2.7,
        dt=0.1,
        horizon=10,
        Q=np.diag([1.0, 1.0, 0.5, 0.1]),
        R=np.diag([0.1, 0.1])
    )
    
    # Create reference trajectory (straight + arc)
    print("\nCreating test trajectory...")
    straight = np.column_stack([
        np.linspace(0, 15, 75),
        np.zeros(75),
        np.zeros(75),
        2.5 * np.ones(75)
    ])
    
    t = np.linspace(0, np.pi/2, 75)
    radius = 8.0
    arc = np.column_stack([
        15 + radius * np.sin(t),
        radius * (1 - np.cos(t)),
        t,
        2.5 * np.ones(75)
    ])
    
    ref_traj = np.vstack([straight, arc])
    
    # MPC simulation
    print("\nRunning MPC simulation...")
    state = np.array([0, 0, 0, 2.5])
    trajectory = [state.copy()]
    controls = []
    
    for step in range(len(ref_traj) - 12):
        control = mpc.control(state, ref_traj[step:])
        state = vehicle.step(state, control, dt=0.1)
        trajectory.append(state.copy())
        controls.append(control)
        
        if step % 30 == 0:
            print(f"  Step {step}/{len(ref_traj)-12}...", end='\r')
    
    trajectory = np.array(trajectory)
    controls = np.array(controls)
    
    print(f"\n\nSimulation finished! Total {len(trajectory)} steps")
    
    # Compute performance metrics
    lateral_errors = []
    for i in range(min(len(trajectory), len(ref_traj))):
        error = np.linalg.norm(trajectory[i, :2] - ref_traj[i, :2])
        lateral_errors.append(error)
    
    print(f"\nPerformance metrics:")
    print(f"  Mean lateral error: {np.mean(lateral_errors):.3f} m")
    print(f"  Max lateral error: {np.max(lateral_errors):.3f} m")
    print(f"  Mean steering angle: {np.rad2deg(np.mean(np.abs(controls[:, 0]))):.2f}°")
    
    stats = mpc.get_statistics()
    if stats:
        print(f"\nSolver performance:")
        print(f"  Mean solve time: {stats['mean_solve_time']*1000:.2f} ms")
        print(f"  Max solve time: {stats['max_solve_time']*1000:.2f} ms")
    
    # Visualization
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Subplot 1: Trajectory
    ax1 = axes[0, 0]
    ax1.plot(ref_traj[:, 0], ref_traj[:, 1], 'b--', linewidth=2, alpha=0.7, label='Reference trajectory')
    ax1.plot(trajectory[:, 0], trajectory[:, 1], 'r-', linewidth=2, label='MPC tracking')
    ax1.scatter(0, 0, c='green', s=150, marker='o', label='Start', zorder=5)
    
    # Mark prediction instants (a few timestamps)
    for i in [20, 60, 100]:
        if i < len(trajectory):
            x, y = trajectory[i, :2]
            ax1.scatter(x, y, c='orange', s=80, marker='x', zorder=5)
    
    ax1.set_xlabel('X (m)', fontsize=12)
    ax1.set_ylabel('Y (m)', fontsize=12)
    ax1.set_title('MPC Trajectory Tracking', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    
    # Subplot 2: Lateral error
    ax2 = axes[0, 1]
    time = np.arange(len(lateral_errors)) * 0.1
    ax2.plot(time, lateral_errors, 'b-', linewidth=2)
    ax2.axhline(y=np.mean(lateral_errors), color='r', linestyle='--',
               label=f'Mean: {np.mean(lateral_errors):.3f} m')
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Lateral error (m)', fontsize=12)
    ax2.set_title('Tracking Error', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # Subplot 3: Control input (steering)
    ax3 = axes[1, 0]
    time = np.arange(len(controls)) * 0.1
    ax3.plot(time, np.rad2deg(controls[:, 0]), 'g-', linewidth=2, label='Steering angle')
    ax3.axhline(y=35, color='r', linestyle='--', alpha=0.5, label='Constraint boundary')
    ax3.axhline(y=-35, color='r', linestyle='--', alpha=0.5)
    ax3.set_xlabel('Time (s)', fontsize=12)
    ax3.set_ylabel('Steering angle (°)', fontsize=12)
    ax3.set_title('Steering Control', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=11)
    ax3.grid(True, alpha=0.3)
    
    # Subplot 4: Acceleration
    ax4 = axes[1, 1]
    time = np.arange(len(controls)) * 0.1
    ax4.plot(time, controls[:, 1], 'm-', linewidth=2, label='Acceleration')
    ax4.axhline(y=2.0, color='r', linestyle='--', alpha=0.5, label='Constraint boundary')
    ax4.axhline(y=-2.0, color='r', linestyle='--', alpha=0.5)
    ax4.set_xlabel('Time (s)', fontsize=12)
    ax4.set_ylabel('Acceleration (m/s²)', fontsize=12)
    ax4.set_title('Acceleration Control', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=11)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lesson4_mpc_basic.png', dpi=150, bbox_inches='tight')
    print("\n  Saved image: lesson4_mpc_basic.png")
    plt.show()


def demo_mpc_vs_pure_pursuit():
    """Demo 2: MPC vs Pure Pursuit comparison"""
    print("\n" + "="*60)
    print("Demo 2: MPC vs Pure Pursuit Performance Comparison")
    print("="*60)
    
    # Create S-curve (more challenging)
    ref_path = create_s_curve_path(length=25, num_points=125, velocity=3.0)
    
    vehicle = BicycleModel(L=2.7)
    initial_state = np.array([0, 0, 0, 3.0])
    
    # Pure Pursuit
    print("\nTesting Pure Pursuit...")
    pp_controller = PurePursuitController(wheelbase=2.7, k_lookahead=1.0, ld_min=3.0)
    pp_simulator = PathFollowingSimulator(pp_controller, vehicle, dt=0.1)
    pp_trajectory, pp_info = pp_simulator.simulate(initial_state, ref_path[:, :2], max_steps=250)
    
    print(f"  Mean lateral error: {pp_info['mean_lateral_error']:.3f} m")
    
    # MPC
    print("\nTesting MPC...")
    mpc_controller = MPCController(wheelbase=2.7, dt=0.1, horizon=10)
    
    state = initial_state.copy()
    mpc_trajectory = [state.copy()]
    
    for step in range(min(200, len(ref_path)-12)):
        control = mpc_controller.control(state, ref_path[step:])
        state = vehicle.step(state, control, dt=0.1)
        mpc_trajectory.append(state.copy())
        
        if step % 40 == 0:
            print(f"  Step {step}/200...", end='\r')
    
    mpc_trajectory = np.array(mpc_trajectory)
    
    # Compute MPC errors
    mpc_errors = []
    for i in range(min(len(mpc_trajectory), len(ref_path))):
        error = np.linalg.norm(mpc_trajectory[i, :2] - ref_path[i, :2])
        mpc_errors.append(error)
    
    print(f"\n  Mean lateral error: {np.mean(mpc_errors):.3f} m")
    
    # Visualization comparison
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Subplot 1: Trajectory comparison
    ax1 = axes[0, 0]
    ax1.plot(ref_path[:, 0], ref_path[:, 1], 'k--', linewidth=2, alpha=0.5, label='Reference Path')
    ax1.plot(pp_trajectory[:, 0], pp_trajectory[:, 1], 'r-', linewidth=2, label='Pure Pursuit')
    ax1.plot(mpc_trajectory[:, 0], mpc_trajectory[:, 1], 'g-', linewidth=2, label='MPC')
    ax1.scatter(0, 0, c='blue', s=150, marker='o', label='Start', zorder=5)
    ax1.set_xlabel('X (m)', fontsize=12)
    ax1.set_ylabel('Y (m)', fontsize=12)
    ax1.set_title('Trajectory Comparison', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    
    # Subplot 2: Lateral error comparison
    ax2 = axes[0, 1]
    time_pp = np.arange(len(pp_controller.lateral_errors)) * 0.1
    time_mpc = np.arange(len(mpc_errors)) * 0.1
    ax2.plot(time_pp, pp_controller.lateral_errors, 'r-', linewidth=2, label='Pure Pursuit')
    ax2.plot(time_mpc, mpc_errors, 'g-', linewidth=2, label='MPC')
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Lateral error (m)', fontsize=12)
    ax2.set_title('Tracking Error Comparison', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # Subplot 3: Performance metrics comparison
    ax3 = axes[1, 0]
    methods = ['Pure Pursuit', 'MPC']
    avg_errors = [pp_info['mean_lateral_error'], np.mean(mpc_errors)]
    max_errors = [pp_info['max_lateral_error'], np.max(mpc_errors)]
    
    x = np.arange(len(methods))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, avg_errors, width, label='Mean error', color='steelblue', alpha=0.8)
    bars2 = ax3.bar(x + width/2, max_errors, width, label='Max error', color='coral', alpha=0.8)
    
    ax3.set_ylabel('Error (m)', fontsize=12)
    ax3.set_title('Performance Metrics Comparison', fontsize=14, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(methods)
    ax3.legend(fontsize=11)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Annotate values
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10)
    
    # Subplot 4: Control comparison (PP steering & MPC solve time)
    ax4 = axes[1, 1]
    time_pp = np.arange(len(pp_controller.control_history)) * 0.1
    ax4.plot(time_pp, np.rad2deg(pp_controller.control_history), 'r-', 
            linewidth=2, label='Pure Pursuit steering', alpha=0.7)
    
    if len(mpc_controller.solve_times) > 0:
        ax4_twin = ax4.twinx()
        ax4_twin.plot(np.arange(len(mpc_controller.solve_times)) * 0.1,
                     np.array(mpc_controller.solve_times) * 1000, 'g--',
                     linewidth=2, label='MPC solve time')
        ax4_twin.set_ylabel('MPC solve time (ms)', fontsize=12, color='g')
        ax4_twin.tick_params(axis='y', labelcolor='g')
    
    ax4.set_xlabel('Time (s)', fontsize=12)
    ax4.set_ylabel('Pure Pursuit steering (°)', fontsize=12, color='r')
    ax4.set_title('Control Comparison', fontsize=14, fontweight='bold')
    ax4.tick_params(axis='y', labelcolor='r')
    ax4.grid(True, alpha=0.3)
    
    # Combine legends
    lines1, labels1 = ax4.get_legend_handles_labels()
    if len(mpc_controller.solve_times) > 0:
        lines2, labels2 = ax4_twin.get_legend_handles_labels()
        ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10)
    else:
        ax4.legend(fontsize=10)
    
    plt.tight_layout()
    plt.savefig('lesson4_mpc_vs_pp.png', dpi=150, bbox_inches='tight')
    print("\n  Saved image: lesson4_mpc_vs_pp.png")
    plt.show()
    
    # Summary
    print("\n" + "="*60)
    print("Performance Summary")
    print("="*60)
    print(f"\nPure Pursuit:")
    print(f"  Mean error: {pp_info['mean_lateral_error']:.3f} m")
    print(f"  Max error: {pp_info['max_lateral_error']:.3f} m")
    print(f"  Simple computation, good real-time performance")
    
    print(f"\nMPC:")
    print(f"  Mean error: {np.mean(mpc_errors):.3f} m")
    print(f"  Max error: {np.max(mpc_errors):.3f} m")
    if mpc_controller.get_statistics():
        stats = mpc_controller.get_statistics()
        print(f"  Mean solve time: {stats['mean_solve_time']*1000:.2f} ms")
    print(f"  Better performance but more complex computation")


def main():
    print("="*60)
    print("Lesson 4: MPC Model Predictive Control - Full Demonstration")
    print("="*60)
    
    # Demo 1
    demo_mpc_basic()
    
    # Demo 2
    demo_mpc_vs_pure_pursuit()
    
    print("\n" + "="*60)
    print("Demonstration completed!")
    print("="*60)
    print("\nKey Findings:")
    print("  • MPC provides better tracking performance via optimization")
    print("  • MPC can handle various constraints (speed, steering angle, etc.)")
    print("  • MPC predicts the future to plan control in advance")
    print("  • Computation cost is the main limitation of MPC")


if __name__ == "__main__":
    main()

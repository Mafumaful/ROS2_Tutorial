"""
Lesson 1 Complete Example: A* Path Planning

Demonstration Content:
1. Create a grid map
2. Run the A* algorithm
3. Visualize the planning results
4. Test different heuristic functions
"""

import sys
sys.path.append('..')

import numpy as np
import matplotlib.pyplot as plt
from algorithms.a_star import AStar, create_grid_map
from utils.visualization import plot_grid_map

def main():
    print("="*60)
    print("Lesson 1: A* Path Planning Algorithm Demonstration")
    print("="*60)
    
    # ===== 1. Create Map =====
    print("\nStep 1: Creating test map...")
    width, height = 20, 20
    
    # Define obstacles
    obstacles = [
        (5, 5, 8, 8),    # Central square obstacle
        (10, 2, 12, 10),  # Vertical obstacle on the right
        (2, 12, 15, 14),  # Horizontal obstacle on the top
    ]
    
    grid = create_grid_map(width, height, obstacles)
    print(f"  Map size: {width} × {height}")
    print(f"  Number of obstacles: {len(obstacles)}")
    
    # ===== 2. Define Start and Goal =====
    start = (2, 2)
    goal = (17, 17)
    
    print(f"\nStep 2: Setting start and goal points...")
    print(f"  Start: {start}")
    print(f"  Goal: {goal}")
    
    # ===== 3. Run A* Planning =====
    print(f"\nStep 3: Executing A* path planning...")
    planner = AStar(grid, start, goal, heuristic_weight=1.0)
    path = planner.plan(verbose=True)
    
    if path is None:
        print("\n✗ Planning failed!")
        return
    
    # ===== 4. Analyze Results =====
    print(f"\nStep 4: Analyzing planning results...")
    
    # Compute path length
    path_length = 0
    for i in range(len(path)-1):
        dx = path[i+1][0] - path[i][0]
        dy = path[i+1][1] - path[i][1]
        path_length += np.sqrt(dx**2 + dy**2)
    
    print(f"  Number of path points: {len(path)}")
    print(f"  Path length: {path_length:.2f}")
    print(f"  Nodes expanded: {planner.nodes_expanded}")
    print(f"  Nodes visited: {planner.nodes_visited}")
    print(f"  Search efficiency: {len(path) / planner.nodes_expanded * 100:.1f}%")
    
    # ===== 5. Visualization =====
    print(f"\nStep 5: Generating visualization...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Subplot 1: Map + Path
    ax1 = axes[0]
    plot_grid_map(grid, start, goal, 
                 path=np.array(path), 
                 title="A* Path Planning Result",
                 ax=ax1)
    
    # Subplot 2: Path only
    ax2 = axes[1]
    path_array = np.array(path)
    ax2.plot(path_array[:, 0], path_array[:, 1], 'b-', linewidth=2, marker='o', markersize=4)
    ax2.scatter(start[0], start[1], c='green', s=200, marker='o', label='Start', zorder=5)
    ax2.scatter(goal[0], goal[1], c='red', s=200, marker='*', label='Goal', zorder=5)
    ax2.set_xlabel('X (m)', fontsize=12)
    ax2.set_ylabel('Y (m)', fontsize=12)
    ax2.set_title('Detailed Path View', fontsize=14)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.axis('equal')
    
    plt.tight_layout()
    plt.savefig('lesson1_result.png', dpi=150, bbox_inches='tight')
    print("  Saved image: lesson1_result.png")
    
    # ===== 6. Compare Different Heuristic Weights =====
    print(f"\nStep 6: Comparing different heuristic weights...")
    
    weights = [0.0, 1.0, 2.0]
    results = []
    
    for w in weights:
        planner = AStar(grid, start, goal, heuristic_weight=w)
        path = planner.plan(verbose=False)
        
        if path:
            results.append({
                'weight': w,
                'path_length': len(path),
                'nodes_expanded': planner.nodes_expanded,
            })
            print(f"  Weight={w:.1f}: Path length={len(path)}, Nodes expanded={planner.nodes_expanded}")
    
    # Visualization Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    
    weights_list = [r['weight'] for r in results]
    path_lengths = [r['path_length'] for r in results]
    nodes_expanded = [r['nodes_expanded'] for r in results]
    
    ax.plot(weights_list, path_lengths, 'b-o', linewidth=2, markersize=8, label='Path Length')
    ax.set_xlabel('Heuristic Weight', fontsize=12)
    ax.set_ylabel('Path Length (points)', fontsize=12, color='b')
    ax.tick_params(axis='y', labelcolor='b')
    
    ax2 = ax.twinx()
    ax2.plot(weights_list, nodes_expanded, 'r-s', linewidth=2, markersize=8, label='Nodes Expanded')
    ax2.set_ylabel('Number of Expanded Nodes', fontsize=12, color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    
    ax.set_title('Effect of Heuristic Weight', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    # Combine Legends
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('lesson1_comparison.png', dpi=150, bbox_inches='tight')
    print("  Saved image: lesson1_comparison.png")
    
    plt.show()
    
    print(f"\n{'='*60}")
    print("Demonstration completed!")
    print("="*60)


if __name__ == "__main__":
    main()

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import numpy as np
import math

# --- 1. Geometry Utility ---

def orientation(p, q, r):
    """
    Finds the orientation of triplet (p, q, r).
    Returns: 0 if collinear, 1 if clockwise, 2 if counterclockwise.
    (Cross-product based calculation)
    """
    val = (q[1] - p[1]) * (r[0] - q[0]) - \
          (q[0] - p[0]) * (r[1] - q[1])
    
    if val == 0: return 0  # Collinear
    return 1 if val > 0 else 2 # Clockwise or Counter-clockwise

# --- 2. The Algorithm (Graham Scan Generator) ---

def graham_scan_generator(points):
    """
    Generates steps for the Graham Scan algorithm.
    """
    # 1. Find the point with the lowest Y-coordinate (pivot)
    min_y = min(p[1] for p in points)
    pivot = next(p for p in points if p[1] == min_y)
    
    # 2. Sort points by angle with respect to the pivot
    def angle_and_dist(p):
        angle = math.atan2(p[1] - pivot[1], p[0] - pivot[0])
        dist = (p[0] - pivot[0])**2 + (p[1] - pivot[1])**2
        return angle, dist

    # Sorts by angle, then by distance for collinear points
    sorted_points = sorted(points, key=angle_and_dist)
    
    # 3. Initialize the hull with the first three points
    hull = [sorted_points[0], sorted_points[1], sorted_points[2]]
    
    # Yield the initial state
    yield sorted_points, hull, 2 # (points, current hull, current index)

    # 4. Process remaining points
    for i in range(3, len(sorted_points)):
        p = sorted_points[i]
        
        # While the last three points do not make a counter-clockwise turn, backtrack
        while len(hull) > 1 and orientation(hull[-2], hull[-1], p) != 2:
            # Yield before popping: [Show why the turn fails]
            yield sorted_points, hull, i
            hull.pop()
            
        hull.append(p)
        
        # Yield after adding: [Show the new, accepted edge]
        yield sorted_points, hull, i 

    # Final Hull State
    yield sorted_points, hull, -1

# --- 3. Visualization Function (Matplotlib Animation) ---

def animate_hull(frame_data):
    """
    The function passed to FuncAnimation to draw the current frame.
    """
    sorted_points, hull, current_index = frame_data
    
    plt.cla()  # Clear previous frame
    ax.set_title("Graham Scan: Convex Hull Algorithm")
    ax.set_aspect('equal', adjustable='box')
    
    # --- A. Draw all Points ---
    X = [p[0] for p in sorted_points]
    Y = [p[1] for p in sorted_points]
    ax.scatter(X, Y, color='gray', s=50, label='All Points')
    
    # --- B. Highlight Current Processing Point ---
    if current_index != -1:
        current_p = sorted_points[current_index]
        ax.scatter(current_p[0], current_p[1], color='red', s=150, zorder=5, label='Current Point')
        
    # --- C. Draw the Current Hull (Lines and Nodes) ---
    if hull:
        # Create a closed loop for the hull visualization
        hull_coords = np.array(hull + [hull[0]]) 
        
        # Hull Edges (Lines)
        ax.plot(hull_coords[:, 0], hull_coords[:, 1], color='blue', linewidth=2, zorder=3)
        
        # Hull Nodes (Highlighting vertices)
        hull_X = hull_coords[:, 0]
        hull_Y = hull_coords[:, 1]
        ax.scatter(hull_X, hull_Y, color='cyan', s=100, zorder=4, label='Hull Vertices')
        
    # Set fixed limits for consistent animation scaling
    ax.set_xlim(min(X) - 1, max(X) + 1)
    ax.set_ylim(min(Y) - 1, max(Y) + 1)
    
    ax.legend(loc='lower right')


# --- 4. Main Execution ---
if __name__ == "__main__":
    # Create 50 random 2D points (x, y tuples)
    NUM_POINTS = 50
    points = [(random.uniform(0, 10), random.uniform(0, 10)) for _ in range(NUM_POINTS)]
    
    # Setup Matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Create the generator for the algorithm steps
    generator = graham_scan_generator(points)
    
    # Create the animation object
    # We explicitly disable caching to avoid the UserWarning
    anim = animation.FuncAnimation(
        fig, 
        animate_hull, 
        frames=generator, 
        repeat=False, 
        interval=200, # 200ms delay per step
        cache_frame_data=False 
    )
    
    plt.show()
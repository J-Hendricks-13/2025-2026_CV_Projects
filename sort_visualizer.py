import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time

# --- 1. The Algorithm (Insertion Sort) ---
def insertion_sort(data):
    # Yields the state of the array after each swap/comparison for visualization
    n = len(data)
    for i in range(1, n):
        key = data[i]
        j = i - 1
        
        # Yield state before inner loop (highlighting the key)
        yield data, [j, i]  
        
        # Inner loop for shifting elements
        while j >= 0 and key < data[j]:
            data[j + 1] = data[j]
            j -= 1
            # Yield state after a shift (highlighting the swap)
            yield data, [j + 1, i]
            
        data[j + 1] = key
        
        # Yield final state of the iteration
        yield data, [-1, -1] # Use -1 to indicate no specific highlighting

# --- 2. The Animation Function ---
def animate_sort(frame):
    # 'frame' receives the yielded data (array state and highlight indices)
    array, highlights = frame
    
    # Clear the old plot and draw the new bar heights
    plt.cla()
    
    # Create the color array for highlighting
    colors = ['gray'] * len(array)
    if highlights[0] != -1:
        colors[highlights[0]] = 'red'  # Highlight the comparison/swap position
    if highlights[1] != -1:
        colors[highlights[1]] = 'blue' # Highlight the 'key' element
        
    # Draw the bars
    bar_rects = plt.bar(range(len(array)), array, color=colors)
    
    # Set plot aesthetics
    plt.title("Insertion Sort Visualization")
    plt.xlabel("Index")
    plt.ylabel("Value")
    
    return bar_rects

# --- 3. Main Execution ---
if __name__ == "__main__":
    # Create a random array of 50 integers
    N = 50
    data = [random.randint(1, 100) for _ in range(N)]
    
    # Create the generator for the algorithm steps
    generator = insertion_sort(data)
    
    # Set up the Matplotlib figure
    fig, ax = plt.subplots()
    
    # Initial draw to set the stage
    ax.bar(range(N), data, color='gray')
    ax.set_title("Insertion Sort Visualization")
    
    # Create the animation object
    # The 'frames' argument takes the generator function
    # 'interval' is the delay between frames in milliseconds
    anim = animation.FuncAnimation(
        fig, 
        animate_sort, 
        frames=generator, 
        repeat=False, 
        blit=False, 
        interval=50 # Adjust for faster/slower animation
    )
    
    # Uncomment the line below to save the animation as a video file (requires ffmpeg)
    # anim.save('insertion_sort.mp4', writer='ffmpeg', fps=30)
    
    plt.show()
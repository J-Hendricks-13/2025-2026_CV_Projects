import pygame
import random
import time
import sys

# --- Color Definitions ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)      # Default box color
RED = (255, 0, 0)         # Highlight color for current key
YELLOW = (255, 200, 0)    # Comparison
GREEN = (0, 200, 0)       # Final sorted color
GREY = (50, 50, 50)

# --- Insertion Sort Generator (rich yields) ---
def insertion_sort_verbose(data):
    n = len(data)
    # first yield to show initial state
    yield data[:], [], 'start', 'Initial array'

    for i in range(1, n):
        key = data[i]
        j = i - 1
        # show selecting key
        yield data[:], [i], 'select', f'Select key {key} at index {i}'

        # comparisons and shifts
        while j >= 0 and key < data[j]:
            # highlight comparison
            yield data[:], [j, i], 'compare', f'Compare key {key} with {data[j]} at index {j}'
            # shift
            data[j + 1] = data[j]
            yield data[:], [j + 1, i], 'shift', f'Shift {data[j+1]} right to index {j+1}'
            j -= 1

        data[j + 1] = key
        yield data[:], [j + 1], 'insert', f'Place key {key} at index {j+1}'

    yield data[:], list(range(n)), 'done', 'Array sorted'

# --- Drawing & UI helpers ---
WIDTH, HEIGHT = 1000, 600
SCREEN = None
FONT = None

HISTORY_LINES = 3

def draw_legend(surface, x, y):
    small = pygame.font.Font(None, 20)
    legend_items = [
        ('RED: key', RED),
        ('YELLOW: comparison', YELLOW),
        ('BLUE: unchanged', BLUE),
        ('GREEN: sorted', GREEN),
    ]
    for i, (label, color) in enumerate(legend_items):
        rect = pygame.Rect(x, y + i*28, 18, 18)
        pygame.draw.rect(surface, color, rect, border_radius=4)
        text = small.render(label, True, WHITE)
        surface.blit(text, (x + 28, y + i*28))

def draw_array(surface, array, highlights, status_text, history):
    surface.fill(BLACK)
    N = len(array)
    BOX_WIDTH = (WIDTH - (N + 1) * 5) / N
    y = HEIGHT - 80
    BOX_HEIGHT = 50

    # Status
    status_surf = FONT.render(f"Status: {status_text}", True, WHITE)
    surface.blit(status_surf, (10, 10))

    # History box (top-left)
    hist_x, hist_y = 10, 40
    pygame.draw.rect(surface, GREY, (hist_x-6, hist_y-6, 360, HISTORY_LINES*22+12), border_radius=6)
    hist_title = FONT.render("History:", True, WHITE)
    surface.blit(hist_title, (hist_x, hist_y-4))
    for i, h in enumerate(history[-HISTORY_LINES:]):
        t = FONT.render(h, True, WHITE)
        surface.blit(t, (hist_x, hist_y + 18*(i+1)))

    # Legend (right)
    draw_legend(surface, WIDTH - 240, 40)

    for i, value in enumerate(array):
        x = i * (BOX_WIDTH + 5) + 5
        color = BLUE
        if status_text == 'Finished':
            color = GREEN
        elif i in highlights:
            # choose between single highlight (key) and multi highlight (compare)
            if len(highlights) == 1:
                color = RED
            else:
                color = YELLOW

        pygame.draw.rect(surface, color, (x, y, BOX_WIDTH, BOX_HEIGHT), border_radius=6)
        txt = FONT.render(str(value), True, WHITE)
        rect = txt.get_rect(center=(x + BOX_WIDTH/2, y + BOX_HEIGHT/2))
        surface.blit(txt, rect)

    pygame.display.update()

# --- Educational App ---
def run_educational():
    global SCREEN, FONT
    pygame.init()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Insertion Sort Visualizer - Educational')
    FONT = pygame.font.Font(None, 24)

    N = 20
    data = [random.randint(1, 99) for _ in range(N)]
    gen = insertion_sort_verbose(data)

    history = []
    clock = pygame.time.Clock()
    running = True

    # fixed slower delay for education
    DELAY = 0.5

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        try:
            array, highlights, action, desc = next(gen)
            # Build human friendly status
            if action == 'start':
                status = 'Starting'
            elif action == 'select':
                status = 'Selecting key'
            elif action == 'compare':
                status = 'Comparing'
            elif action == 'shift':
                status = 'Shifting'
            elif action == 'insert':
                status = 'Inserting'
            elif action == 'done':
                status = 'Finished'
            else:
                status = 'Sorting'

            history.append(desc)
            # Draw
            draw_array(SCREEN, array, highlights, status, history)

            # Delay tailored: longer for insert/done, shorter for compare/shift
            if action in ('insert', 'done'):
                time.sleep(DELAY * 1.2)
            elif action == 'select':
                time.sleep(DELAY * 0.9)
            else:
                time.sleep(DELAY * 0.8)

        except StopIteration:
            # finished; keep final state for a moment
            draw_array(SCREEN, data, list(range(N)), 'Finished', history)
            pygame.time.wait(3000)
            running = False

        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    run_educational()

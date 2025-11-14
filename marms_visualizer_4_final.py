import pygame, random, sys

# --- CONFIG ---
WINDOW_W, WINDOW_H = 1200, 700
PANEL_W = 400
NUM_ACCOUNTS = 10
START_EQ = 10000.0
TARGET_EQ = 11000.0   # 10% Target
DEATH_EQ = 9000.0     # $1000 Loss Threshold
MAX_TRADES = 500      # Safety stop for non-freezing accounts
BASE_FPS = 30         # Base frame rate for display
SPEED_FACTOR = 0.5      # Initial speed factor (1x)

# Trading Parameters
RISK_PERCENT = 0.01   # 1.0% risk
RISK_AMOUNT = START_EQ * RISK_PERCENT # $100
WIN_MULT = 2.0        # Reward is 1.5x Risk (e.g., +$150)
LOSS_MULT = 1.0       # Loss is 1.0x Risk (e.g., -$100)

# Account data initialization
def init_accounts():
    return [{
        "id": i + 1,
        "equity": START_EQ,
        "history": [START_EQ],
        "wins": 0,
        "losses": 0,
        "total": 0,
        "status": "running" # 'running', 'finished', 'failed'
    } for i in range(NUM_ACCOUNTS)]

accounts = init_accounts()

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("MARMS: Multi-Account Risk Simulation")
font = pygame.font.Font(None, 26)
small_font = pygame.font.Font(None, 20)
clock = pygame.time.Clock()

paused = False
all_finished = False

def simulate_trade(acc):
    if acc["status"] != "running" or acc["total"] >= MAX_TRADES: 
        return

    outcome = random.choice(["win", "loss"])
    acc["total"] += 1
    
    if outcome == "win":
        acc["equity"] += RISK_AMOUNT * WIN_MULT
        acc["wins"] += 1
    else:
        acc["equity"] -= RISK_AMOUNT * LOSS_MULT
        acc["losses"] += 1
        
    acc["equity"] = max(0.0, acc["equity"]) # Prevent negative equity
    acc["history"].append(acc["equity"])
    
    # Check finish/fail conditions and freeze
    if acc["equity"] >= TARGET_EQ:
        acc["status"] = "finished"
        acc["equity"] = TARGET_EQ # Clamp for clean display
    elif acc["equity"] <= DEATH_EQ:
        acc["status"] = "failed"
        acc["equity"] = DEATH_EQ # Clamp for clean display

def check_global_stop():
    global all_finished
    all_finished = all(a["status"] != "running" for a in accounts)

def draw_graph():
    screen.fill((25, 25, 25))
    plot_area = pygame.Rect(0, 0, WINDOW_W - PANEL_W, WINDOW_H)
    pygame.draw.rect(screen, (30, 30, 30), plot_area)

    # 1. Determine graph scaling
    max_len = max(len(a["history"]) for a in accounts) if accounts else 0
    
    # Determine max/min Y equity values across ALL accounts/history
    max_y = TARGET_EQ * 1.05
    min_y = DEATH_EQ * 0.95 
    
    for acc in accounts:
        if acc["history"]:
            max_y = max(max_y, max(acc["history"]) * 1.05)
            min_y = min(min_y, min(acc["history"]) * 0.95)
    
    if max_y <= min_y: max_y = min_y + 1 # Prevent division by zero if all values are equal

    # 2. Draw Target Line and Death Line
    def get_y_pos(eq):
        return int(WINDOW_H - ((eq - min_y) / (max_y - min_y)) * WINDOW_H * 0.9)
        
    y_target = get_y_pos(TARGET_EQ)
    y_death = get_y_pos(DEATH_EQ)
    
    # Draw Target Line (Green)
    pygame.draw.line(screen, (0, 100, 0), (20, y_target), (plot_area.width - 20, y_target), 1)
    # Draw Death Line (Red)
    pygame.draw.line(screen, (100, 0, 0), (20, y_death), (plot_area.width - 20, y_death), 1)
    
    # 3. Draw equity curves
    x_scale_factor = (plot_area.width - 40) / max(1, max_len)
    
    for i, acc in enumerate(accounts):
        if acc["status"] == "finished":
            color = (0, 255, 0)
        elif acc["status"] == "failed":
            color = (255, 0, 0)
        else:
            color = (100, 180, 255) # Running color
            
        hist = acc["history"]
        
        if len(hist) > 1:
            pts = []
            for j, eq in enumerate(hist):
                x = 20 + j * x_scale_factor
                y = get_y_pos(eq)
                y = min(WINDOW_H - 10, max(10, y))
                pts.append((x, y))
            
            pygame.draw.lines(screen, color, False, pts, 2)

def draw_panel():
    panel_x = WINDOW_W - PANEL_W + 20
    pygame.draw.rect(screen, (35, 35, 35), (WINDOW_W - PANEL_W, 0, PANEL_W, WINDOW_H))
    y = 20
    
    # Header
    screen.blit(font.render(f"MARMS: Risk (Speed: {SPEED_FACTOR}x)", True, (255, 255, 255)), (panel_x, y))
    y += 30
    screen.blit(small_font.render(f"R:R 1.0:1.5 | Risk 1.0% (${RISK_AMOUNT:.0f})", True, (200, 200, 200)), (panel_x, y))
    y += 30

    total_wins = total_losses = total_trades = 0
    
    # Account details
    for acc in accounts:
        hit_rate = (acc["wins"] / acc["total"] * 100) if acc["total"] > 0 else 0
        total_wins += acc["wins"]
        total_losses += acc["losses"]
        total_trades += acc["total"]

        if acc["status"] == "finished":
            color = (0, 200, 0)
            status_text = "(TARGET HIT)"
        elif acc["status"] == "failed":
            color = (200, 0, 0)
            status_text = "(DEATH HIT)"
        else:
            color = (255, 255, 255)
            status_text = "(RUNNING)"
        
        # Equity Display
        eq_text = f"Acc {acc['id']}: Eq ${acc['equity']:.0f} {status_text}"
        screen.blit(font.render(eq_text, True, color), (panel_x, y))
        y += 20
        
        # Stats Display
        stats_text = f"Trades: {acc['total']:3}  Wins: {acc['wins']:2}  Loss: {acc['losses']:2}  Hit: {hit_rate:5.1f}%"
        screen.blit(small_font.render(stats_text, True, (200, 200, 200)), (panel_x, y))
        y += 25        

    # Aggregate Stats (Existing display for Hit Rate)
 # Calculate Average Trades per Account
    avg_trades = total_trades / NUM_ACCOUNTS
    
    # Aggregate Stats (Existing display for Hit Rate)
    if total_trades > 0:
        agg_rate = total_wins / total_trades * 100
        y += 10
        # Display the Agg Hit Rate (already present)
        screen.blit(font.render(f"AGG Hit Rate: {agg_rate:.2f}%", True, (255, 200, 0)), (panel_x, y))
    
    # --- Portfolio Totals ---
    y += 35 
    screen.blit(font.render("--- Portfolio Totals ---", True, (150, 150, 150)), (panel_x, y))
    y += 25
    
    # Display Total Trades
    screen.blit(font.render(f"Total Trades: {total_trades}", True, (255, 255, 255)), (panel_x, y))
    y += 25
    
    # 🟢 NEW: Display Average Trades
    screen.blit(font.render(f"Avg Trades Per Account: {avg_trades:.1f}", True, (150, 150, 255)), (panel_x, y))
    y += 25
    
    # Display Total Wins and Losses
    screen.blit(font.render(f"Total Wins: {total_wins}", True, (0, 255, 0)), (panel_x, y))
    y += 25
    screen.blit(font.render(f"Total Losses: {total_losses}", True, (255, 0, 0)), (panel_x, y))
    
    # ---------------------------------------------------
        
    # Status & Controls (This block is now correctly positioned below the totals)
    y += 35 
    
    if all_finished:
        status_text = "SIMULATION COMPLETE (R to Reset)"
    # ... (rest of the function, including the final status and clock.tick)
    
    # ---------------------------------------------------
        
    # Status & Controls (This block is now correctly positioned below the totals)
    # We use the current 'y' position, and add a small buffer (25)
    y += 35 
    
    if all_finished:
        status_text = "SIMULATION COMPLETE (R to Reset)"
        status_col = (255, 255, 0)
    else:
        status_text = "PAUSED (SPACE)" if paused else "RUNNING (SPACE)"
        status_col = (255, 100, 100) if paused else (100, 255, 100)
    
    screen.blit(font.render(status_text, True, status_col), (panel_x, y))
    y += 25
    screen.blit(small_font.render("UP/DOWN: Speed | R: Reset", True, (200, 200, 200)), (panel_x, y))


def reset_sim():
    global accounts, all_finished
    accounts = init_accounts()
    all_finished = False

def handle_speed_change(key):
    global SPEED_FACTOR
    
    if key == pygame.K_UP: 
        SPEED_FACTOR = min(5.0, SPEED_FACTOR * 2) # Max 16x
    elif key == pygame.K_DOWN: 
        SPEED_FACTOR = max(0.10, SPEED_FACTOR / 2) # Min 1x

# Main loop
# Main loop
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN:
            
            # 1. Handle non-global variables first
            if e.key == pygame.K_SPACE: 
                paused = not paused
            elif e.key == pygame.K_r: 
                reset_sim()
            elif e.key == pygame.K_ESCAPE: 
                pygame.quit(); sys.exit()
            
            # 2. Call the helper function for SPEED_FACTOR (where 'global' is correctly defined)
            if e.key in (pygame.K_UP, pygame.K_DOWN):
                 handle_speed_change(e.key) 
            
    # ... rest of the loop remains the same ...

    if not paused and not all_finished:
        # Run one trade for each account per frame
        for acc in accounts:
            simulate_trade(acc)
        
        # Check stop condition after the trades
        check_global_stop()

    draw_graph()
    draw_panel()
    pygame.display.flip()
    
    # Adjust frame rate based on the speed factor
    clock.tick(BASE_FPS * SPEED_FACTOR)
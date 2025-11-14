import numpy as np
import random
import pygame
import sys
import math
import copy

# Colors
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
WHITE = (255,255,255)

# Game constants
ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

# MCTS constants
UCT_C = 1.4

def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT), dtype=int)
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

    return False

# Keep evaluation functions (optional for heuristics)
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    ## Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    ## Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    ## Score positive sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

# MCTS Node
class Node:
    def __init__(self, board, parent=None, move=None, player=None):
        self.board = board  # board state after move
        self.parent = parent
        self.children = {}  # move_col -> Node
        self.untried_moves = get_valid_locations(board)
        self.visits = 0
        self.wins = 0  # wins for the player who just moved (node.player)
        self.move = move  # move that led to this node (column)
        self.player = player  # player who made the move to reach this node (PLAYER_PIECE or AI_PIECE)

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_uct_child(self, c_param=UCT_C):
        # UCT = w_i/n_i + c * sqrt( ln(N) / n_i )
        choices = []
        for move, child in self.children.items():
            if child.visits == 0:
                uct = float('inf')
            else:
                exploitation = child.wins / child.visits
                exploration = c_param * math.sqrt(math.log(self.visits) / child.visits)
                uct = exploitation + exploration
            choices.append((uct, child))
        return max(choices, key=lambda x: x[0])[1]

    def expand(self):
        move = random.choice(self.untried_moves)
        row = get_next_open_row(self.board, move)
        b_copy = self.board.copy()
        # determine the player who will move for this move
        next_player_piece = AI_PIECE if count_pieces(b_copy) % 2 == 0 else PLAYER_PIECE
        drop_piece(b_copy, row, move, next_player_piece)
        child = Node(b_copy, parent=self, move=move, player=next_player_piece)
        self.untried_moves.remove(move)
        self.children[move] = child
        return child

    def best_child_by_visits(self):
        return max(self.children.values(), key=lambda n: n.visits)

# Helper to count pieces (to infer next player in expansions/simulations)
def count_pieces(board):
    return np.count_nonzero(board)

# Simulation / rollout: random play until terminal
def simulate_random_playout(board, starting_player_piece=None):
    b = board.copy()
    # infer who moves next: if starting_player_piece given, start with that, else infer
    if starting_player_piece is None:
        next_player = AI_PIECE if count_pieces(b) % 2 == 0 else PLAYER_PIECE
    else:
        next_player = starting_player_piece

    while True:
        if winning_move(b, PLAYER_PIECE):
            return PLAYER_PIECE
        if winning_move(b, AI_PIECE):
            return AI_PIECE
        valid_locations = get_valid_locations(b)
        if len(valid_locations) == 0:
            return None  # draw
        move = random.choice(valid_locations)
        row = get_next_open_row(b, move)
        drop_piece(b, row, move, next_player)
        next_player = PLAYER_PIECE if next_player == AI_PIECE else AI_PIECE

# Backpropagation: winner is the winning piece or None
def backpropagate(node, winner):
    while node is not None:
        node.visits += 1
        # node.player is the player who made the move that resulted in this node
        if winner is not None and node.player == winner:
            node.wins += 1
        node = node.parent

# MCTS main
def MCTS_Search(root_board, iterations=1000):
    root = Node(root_board.copy(), parent=None, move=None, player=None)

    for _ in range(iterations):
        node = root

        # Selection
        while not is_terminal_node(node.board) and node.is_fully_expanded():
            node = node.best_uct_child()

        # Expansion
        if not is_terminal_node(node.board):
            if not node.is_fully_expanded():
                node = node.expand()

        # Simulation
        # The next player to move after node.player
        next_player = AI_PIECE if count_pieces(node.board) % 2 == 0 else PLAYER_PIECE
        winner = simulate_random_playout(node.board, starting_player_piece=next_player)

        # Backpropagation
        backpropagate(node, winner)

    # Choose the move with the most visits
    if len(root.children) == 0:
        return random.choice(get_valid_locations(root_board)), {}

    best_child = root.best_child_by_visits()
    # Prepare stats for visualization
    stats = {}
    max_visits = max(child.visits for child in root.children.values())
    for col, child in root.children.items():
        stats[col] = {
            'visits': child.visits,
            'win_rate': child.wins / child.visits if child.visits > 0 else 0.0,
            'visits_ratio': child.visits / max_visits if max_visits > 0 else 0.0
        }

    return best_child.move, stats

# Utility functions

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def pick_best_move(board, piece):

    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col

# Drawing (updated to include MCTS stats)
def draw_board(board, mcts_stats=None):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)

    # Draw pieces
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)

    # Overlay MCTS statistics above columns
    if mcts_stats is not None:
        # text font
        smallfont = pygame.font.SysFont("monospace", 18)
        # find max visits for scaling if not provided
        max_visits = 1
        for v in mcts_stats.values():
            if v['visits'] > max_visits:
                max_visits = v['visits']

        for col in range(COLUMN_COUNT):
            x_center = int(col*SQUARESIZE + SQUARESIZE/2)
            # draw visits bar
            if col in mcts_stats:
                visits = mcts_stats[col]['visits']
                win_rate = mcts_stats[col]['win_rate']
                ratio = mcts_stats[col]['visits_ratio']
                bar_height = int(ratio * (SQUARESIZE - 10))
                bar_top = int(SQUARESIZE - bar_height)
                # background rect for bar
                pygame.draw.rect(screen, BLACK, (col*SQUARESIZE+10, 5, SQUARESIZE-20, SQUARESIZE-10))
                # filled bar (use WHITE outline then YELLOW fill)
                pygame.draw.rect(screen, WHITE, (col*SQUARESIZE+12, 7, SQUARESIZE-24, SQUARESIZE-14), 1)
                pygame.draw.rect(screen, YELLOW, (col*SQUARESIZE+12, SQUARESIZE-7-bar_height, SQUARESIZE-24, bar_height))

                # draw text: visits and win rate
                visits_label = smallfont.render(f"n={visits}", 1, WHITE)
                rate_label = smallfont.render(f"w={win_rate:.2f}", 1, WHITE)
                screen.blit(visits_label, (x_center - visits_label.get_width()//2, SQUARESIZE+2))
                screen.blit(rate_label, (x_center - rate_label.get_width()//2, SQUARESIZE+20))
            else:
                # no simulations for this column
                small = smallfont.render("n=0", 1, WHITE)
                screen.blit(small, (x_center - small.get_width()//2, SQUARESIZE+2))

    pygame.display.update()

# Main game loop with MCTS integrated
if __name__ == '__main__':
    board = create_board()
    print_board(board)
    game_over = False

    pygame.init()

    SQUARESIZE = 100

    width = COLUMN_COUNT * SQUARESIZE
    height = (ROW_COUNT+1) * SQUARESIZE

    size = (width, height)

    RADIUS = int(SQUARESIZE/2 - 5)

    screen = pygame.display.set_mode(size)
    draw_board(board)
    pygame.display.update()

    myfont = pygame.font.SysFont("monospace", 75)

    turn = random.randint(PLAYER, AI)

    mcts_stats = {}

    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                # Ask for Player 1 Input
                if turn == PLAYER:
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)

                        if winning_move(board, PLAYER_PIECE):
                            label = myfont.render("Player 1 wins!!", 1, RED)
                            screen.blit(label, (40,10))
                            game_over = True

                        turn += 1
                        turn = turn % 2

                        print_board(board)
                        draw_board(board, mcts_stats)

        # AI turn
        if turn == AI and not game_over:
            # Run MCTS to pick a move
            iterations = 800  # tune this: higher -> stronger but slower
            col, stats = MCTS_Search(board, iterations=iterations)
            mcts_stats = stats

            if is_valid_location(board, col):
                #pygame.time.wait(500)
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)

                if winning_move(board, AI_PIECE):
                    label = myfont.render("Player 2 wins!!", 1, YELLOW)
                    screen.blit(label, (40,10))
                    game_over = True

                print_board(board)
                draw_board(board, mcts_stats)

                turn += 1
                turn = turn % 2

        if game_over:
            pygame.time.wait(3000)

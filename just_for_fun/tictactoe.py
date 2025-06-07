import random

def print_board(board):
    for i, row in enumerate(board):
        print(" | ".join(row))
        if i < 2:
            print("--" * 5)

def check_winner(board, player):
    for i in range(3):
        if all([cell == player for cell in board[i]]) or all([board[j][i] == player for j in range(3)]):
            return True
    if (board[0][0] == player and board[1][1] == player and board[2][2] == player) or \
       (board[0][2] == player and board[1][1] == player and board[2][0] == player):
        return True
    return False

def check_draw(board):
    return all(cell != " " for row in board for cell in row)

def get_move(player, board):
    while True:
        try:
            move = int(input(f"Player {player}, enter your move (1-9): ")) - 1
            row, col = divmod(move, 3)
            if board[row][col] == " ":
                return row, col
            else:
                print("This cell is already taken. Try again.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter a number between 1 and 9.")

# ---------------- Minimax Algorithm for Hard Mode -------------------
def minimax(board, depth, is_maximizing, ai_player):
    opponent = "O" if ai_player == "X" else "X"
    if check_winner(board, ai_player):
        return 10 - depth
    elif check_winner(board, opponent):
        return depth - 10
    elif check_draw(board):
        return 0

    if is_maximizing:
        best_score = float('-inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = ai_player
                    score = minimax(board, depth + 1, False, ai_player)
                    board[i][j] = " "
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = opponent
                    score = minimax(board, depth + 1, True, ai_player)
                    board[i][j] = " "
                    best_score = min(score, best_score)
        return best_score

# ---------------- Heuristic for Medium Mode -------------------
def find_medium_move(board, ai_player):
    opponent = "O" if ai_player == "X" else "X"

    # Try to win
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                board[i][j] = ai_player
                if check_winner(board, ai_player):
                    board[i][j] = " "
                    return (i, j)
                board[i][j] = " "

    # Try to block opponent's win
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                board[i][j] = opponent
                if check_winner(board, opponent):
                    board[i][j] = " "
                    return (i, j)
                board[i][j] = " "

    # Else pick random
    empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]
    return random.choice(empty_cells)

# ---------------- Find Move by Difficulty -------------------
def find_best_move(board, ai_player, difficulty):
    empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]

    if difficulty == "easy":
        return random.choice(empty_cells)
    elif difficulty == "medium":
        return find_medium_move(board, ai_player)
    elif difficulty == "hard":
        best_score = float('-inf')
        move = None
        for i, j in empty_cells:
            board[i][j] = ai_player
            score = minimax(board, 0, False, ai_player)
            board[i][j] = " "
            if score > best_score:
                best_score = score
                move = (i, j)
        return move

# ---------------- Inevitable Draw Check -------------------
def is_inevitable_draw(board, current_player, ai_player, difficulty):
    empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]
    if len(empty_cells) <= 3:
        score = minimax(board, 0, current_player == ai_player, ai_player)
        return score == 0
    return False

# ---------------- Main Game -------------------
def main():
    board = [[" " for _ in range(3)] for _ in range(3)]

    human_player = input("Choose your player (X/O): ").upper()
    while human_player not in ["X", "O"]:
        human_player = input("Invalid choice. Choose X or O: ").upper()

    ai_player = "O" if human_player == "X" else "X"

    difficulty = input("Choose difficulty (easy / medium / hard): ").lower()
    while difficulty not in ["easy", "medium", "hard"]:
        difficulty = input("Invalid choice. Choose difficulty (easy / medium / hard): ").lower()

    current_player = "X"

    while True:
        print_board(board)

        if current_player == human_player:
            row, col = get_move(human_player, board)
        else:
            print("AI is making a move...")
            row, col = find_best_move(board, ai_player, difficulty)

        board[row][col] = current_player

        if check_winner(board, current_player):
            print_board(board)
            print(f"Player {current_player} wins!")
            break
        elif check_draw(board):
            print_board(board)
            print("It's a draw!")
            break
        elif is_inevitable_draw(board, current_player, ai_player, difficulty):
            print_board(board)
            print("The game is heading toward a guaranteed draw.")
            choice = input("Would you like to restart (R) or quit (Q)? ").upper()
            while choice not in ["R", "Q"]:
                choice = input("Invalid choice. Press R to restart or Q to quit: ").upper()
            if choice == "R":
                print("\nRestarting the game...\n")
                main()
                return
            else:
                print("Thanks for playing!")
                break

        current_player = "O" if current_player == "X" else "X"

if __name__ == "__main__":
    main()

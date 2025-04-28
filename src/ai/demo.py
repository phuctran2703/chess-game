from src.core.Board.board import Board
from src.move_generator import MoveGenerator
from src.ai.player import ChessAI
import time

def play_ai_vs_ai_game():
    """
    Demonstration of two AI players playing against each other
    """
    # Create a new board with the starting position
    board = Board.create_board()
    
    # Create two AI players with different depths
    white_ai = ChessAI(depth=3)  # Depth 3 for White
    black_ai = ChessAI(depth=3)  # Depth 3 for Black
    
    move_count = 0
    max_moves = 100  # Prevent infinite games
    
    print("Starting AI vs AI game:")
    print(board)
    
    while move_count < max_moves:
        # Choose AI based on whose turn it is
        current_ai = white_ai if board.is_white_to_move else black_ai
        side_name = "White" if board.is_white_to_move else "Black"
        
        print(f"\n{side_name} is thinking...")
        start_time = time.time()
        move = current_ai.choose_move(board)
        elapsed = time.time() - start_time
        
        # Check for game end
        if move is None:
            print(f"Game over! {side_name} has no legal moves.")
            break
            
        # Make the move
        board.make_move(move)
        move_count += 1
        
        # Display the move and board
        print(f"{side_name} plays: {move} (in {elapsed:.2f} seconds)")
        print(board)
        
        # Check for checkmate or stalemate
        move_gen = MoveGenerator(board)
        legal_moves = move_gen.generate_legal_moves()
        if not legal_moves:
            next_side = "Black" if board.is_white_to_move else "White"
            if board.is_in_check():
                print(f"Checkmate! {side_name} wins!")
            else:
                print("Stalemate! The game is a draw.")
            break
            
        # Check for draw by fifty-move rule
        if board.fifty_move_counter >= 100:
            print("Draw by fifty-move rule!")
            break
            
    print("Game completed!")

def play_ai_move_on_board(board, depth=4, time_limit=None):
    """
    Function to make an AI move on a given board
    
    Parameters:
    - board: Current board state
    - depth: Search depth for the AI
    - time_limit: Maximum time in seconds
    
    Returns:
    - The move chosen by the AI
    """
    ai = ChessAI(depth=depth, time_limit=time_limit)
    return ai.choose_move(board)

def play_human_vs_ai_game():
    """
    Demonstration of human vs AI game (text-based interface)
    """
    board = Board.create_board()
    ai = ChessAI(depth=3)
    
    print("Starting Human vs AI game:")
    print("You are playing as White, AI is Black")
    print("To enter a move, use format: 'e2e4' for moving from e2 to e4")
    print(board)
    
    while True:
        # Human move (White)
        if board.is_white_to_move:
            move_gen = MoveGenerator(board)
            legal_moves = move_gen.generate_legal_moves()
            
            if not legal_moves:
                if board.is_in_check():
                    print("Checkmate! AI wins!")
                else:
                    print("Stalemate! The game is a draw.")
                break
                
            valid_move = False
            while not valid_move:
                try:
                    move_str = input("Enter your move (e.g., 'e2e4'): ")
                    
                    # Convert input string to corresponding move object
                    from_file = ord(move_str[0]) - ord('a')
                    from_rank = int(move_str[1]) - 1
                    to_file = ord(move_str[2]) - ord('a')
                    to_rank = int(move_str[3]) - 1
                    
                    from_square = from_rank * 8 + from_file
                    to_square = to_rank * 8 + to_file
                    
                    # Find the move object that corresponds to this move
                    matched_move = None
                    for move in legal_moves:
                        if move.start_square == from_square and move.target_square == to_square:
                            # Handle promotions
                            if len(move_str) > 4 and move.is_promotion:
                                promo_type = move_str[4].lower()
                                if (promo_type == 'q' and move.move_flag == Move.PROMOTE_TO_QUEEN_FLAG) or \
                                   (promo_type == 'r' and move.move_flag == Move.PROMOTE_TO_ROOK_FLAG) or \
                                   (promo_type == 'b' and move.move_flag == Move.PROMOTE_TO_BISHOP_FLAG) or \
                                   (promo_type == 'n' and move.move_flag == Move.PROMOTE_TO_KNIGHT_FLAG):
                                    matched_move = move
                                    break
                            else:
                                matched_move = move
                                break
                    
                    if matched_move:
                        board.make_move(matched_move)
                        valid_move = True
                        print("Your move:", matched_move)
                        print(board)
                    else:
                        print("Invalid move. Try again.")
                except Exception as e:
                    print(f"Error: {e}")
                    print("Invalid input format. Please use format 'e2e4'.")
        
        # AI move (Black)
        else:
            move_gen = MoveGenerator(board)
            legal_moves = move_gen.generate_legal_moves()
            
            if not legal_moves:
                if board.is_in_check():
                    print("Checkmate! You win!")
                else:
                    print("Stalemate! The game is a draw.")
                break
                
            print("AI is thinking...")
            move = ai.choose_move(board)
            board.make_move(move)
            print("AI move:", move)
            print(board)

if __name__ == "__main__":
    print("Chess AI Demonstration")
    print("1. Play AI vs AI")
    print("2. Play Human vs AI")
    choice = input("Select option (1/2): ")
    
    if choice == "1":
        play_ai_vs_ai_game()
    elif choice == "2":
        play_human_vs_ai_game()
    else:
        print("Invalid choice. Exiting.")
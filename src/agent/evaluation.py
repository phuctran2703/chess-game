from src.core.Board.piece import *

# Piece values in centipawns (1 pawn = 100 centipawns)
PIECE_VALUES = {
    PAWN: 100,
    KNIGHT: 300,
    BISHOP: 300,
    ROOK: 500,
    QUEEN: 900,
    KING: 20000  # High value to ensure king's safety
}

# Piece-square tables for positional evaluation
# Adapted from simplified chess programming theory
# Each table is from white's perspective, will be flipped for black
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5,  5,  5,  5,  5,-10,
    -10,  0,  5,  0,  0,  5,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_MIDDLE_GAME_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]

KING_END_GAME_TABLE = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

# Dictionary to map pieces to their position tables
POSITION_TABLES = {
    PAWN: PAWN_TABLE,
    KNIGHT: KNIGHT_TABLE,
    BISHOP: BISHOP_TABLE,
    ROOK: ROOK_TABLE,
    QUEEN: QUEEN_TABLE,
    KING: KING_MIDDLE_GAME_TABLE  # Default to middle game
}

def get_piece_position_score(piece, square):
    """Get positional score for a piece at a square."""
    piece_type_val = piece_type(piece)
    if piece_type_val == NONE:
        return 0
        
    # Get the position table for this piece type
    position_table = POSITION_TABLES.get(piece_type_val, [0] * 64)
    
    # Get the score based on piece color (flipped for black)
    if is_white(piece):
        return position_table[square]
    else:
        # Flip the square for black pieces (mirror vertically)
        mirror_square = (7 - square // 8) * 8 + (square % 8)
        return position_table[mirror_square]

def evaluate_board(board):
    """
    Evaluate the current board position.
    Returns a score from white's perspective:
    - Positive score means white is winning
    - Negative score means black is winning
    """
    score = 0
    
    # Check if king is captured (shouldn't normally happen in a real game)
    white_king_captured, black_king_captured = board.is_king_captured()
    if white_king_captured:
        return -100000  # Black wins
    if black_king_captured:
        return 100000   # White wins
    
    # Position evaluation
    position_score = 0
    
    # Determine if we're in endgame
    is_endgame = is_endgame_position(board)
    if is_endgame:
        POSITION_TABLES[KING] = KING_END_GAME_TABLE
    else:
        POSITION_TABLES[KING] = KING_MIDDLE_GAME_TABLE
    
    # Evaluate each square
    for square in range(64):
        piece = board.square[square]
        if piece == NONE:
            continue
            
        piece_value = PIECE_VALUES.get(piece_type(piece), 0)
        piece_position_score = get_piece_position_score(piece, square)
        
        # Add to the appropriate score based on piece color
        if is_white(piece):
            position_score += piece_position_score
        else:
            position_score -= piece_position_score
    
    # Get positional score difference (separate calculation)
    positional_score_difference = evaluate_positional_score_difference(board)
    
    # Check for specific board features
    mobility_score = evaluate_mobility(board)
    pawn_structure_score = evaluate_pawn_structure(board)
    king_safety_score = evaluate_king_safety(board)
    king_in_check_score = evaluate_king_in_check(board)
    
    # Combine all scoring factors
    score = position_score + mobility_score + pawn_structure_score + king_safety_score + king_in_check_score + positional_score_difference
    
    return score

def is_endgame_position(board):
    """Determine if the position is an endgame based on material."""
    # Count major pieces (queen and rooks)
    white_major_pieces = count_major_pieces(board, True)
    black_major_pieces = count_major_pieces(board, False)
    
    # Endgame if both sides have 1 or fewer major pieces, or if queens are off the board
    return (white_major_pieces <= 1 and black_major_pieces <= 1) or \
           (board.all_piece_lists[WHITE_QUEEN].count == 0 and board.all_piece_lists[BLACK_QUEEN].count == 0)

def count_major_pieces(board, is_white):
    """Count major pieces (queen and rooks) for a specific color."""
    color = WHITE if is_white else BLACK
    queen_piece = make_piece(QUEEN, color)
    rook_piece = make_piece(ROOK, color)
    return board.all_piece_lists[queen_piece].count + board.all_piece_lists[rook_piece].count

def evaluate_mobility(board):
    """Evaluate piece mobility (simplified)."""
    from src.core.Board.move_generator import MoveGenerator
    
    # Save current game state
    original_is_white_to_move = board.is_white_to_move
    
    # Evaluate white mobility
    board.is_white_to_move = True
    white_move_gen = MoveGenerator(board)
    white_mobility = len(white_move_gen.generate_legal_moves())
    
    # Evaluate black mobility
    board.is_white_to_move = False
    black_move_gen = MoveGenerator(board)
    black_mobility = len(black_move_gen.generate_legal_moves())
    
    # Restore original game state
    board.is_white_to_move = original_is_white_to_move
    
    # Return mobility difference (with a scaling factor)
    return (white_mobility - black_mobility) * 10

def evaluate_positional_score_difference(board):
    """
    Calculate the difference between all white pieces' positional scores
    and all black pieces' positional scores.
    Returns a positive value if white has better positioning, negative otherwise.
    """
    white_position_score = 0
    black_position_score = 0
    
    # Evaluate each square
    for square in range(64):
        piece = board.square[square]
        if piece == NONE:
            continue
            
        # Get position score for this piece
        piece_position_score = get_piece_position_score(piece, square)
        
        # Add to the appropriate score based on piece color
        if is_white(piece):
            white_position_score += piece_position_score
        else:
            black_position_score += piece_position_score
    
    # Return the difference (white - black)
    return white_position_score - black_position_score

def evaluate_pawn_structure(board):
    """Evaluate pawn structure (simplified)."""
    score = 0
    
    # Doubled pawns penalty
    white_pawn_files = [0] * 8
    black_pawn_files = [0] * 8
    
    # Count pawns on each file
    for square in range(64):
        piece = board.square[square]
        if piece_type(piece) == PAWN:
            file_index = square % 8
            if is_white(piece):
                white_pawn_files[file_index] += 1
            else:
                black_pawn_files[file_index] += 1
    
    # Penalize doubled pawns
    for i in range(8):
        if white_pawn_files[i] > 1:
            score -= 10 * (white_pawn_files[i] - 1)
        if black_pawn_files[i] > 1:
            score += 10 * (black_pawn_files[i] - 1)
    
    return score

def evaluate_king_in_check(board):
    """
    Evaluates if the king is in check and applies a large penalty.
    Returns a score from white's perspective.
    """
    score = 0
    
    # Lưu trạng thái hiện tại
    original_side_to_move = board.is_white_to_move
    
    # Kiểm tra vua trắng
    board.is_white_to_move = True
    # Reset cached value since we changed the side to move
    board.has_cached_in_check_value = False
    if board.is_in_check():
        score -= 70000  # Phạt nếu vua trắng bị chiếu
    
    # Kiểm tra vua đen
    board.is_white_to_move = False
    # Reset cached value again for the other side
    board.has_cached_in_check_value = False
    if board.is_in_check():
        score += 70000  # Thưởng nếu vua đen bị chiếu (phạt đen)
    
    # Khôi phục trạng thái ban đầu
    board.is_white_to_move = original_side_to_move
    board.has_cached_in_check_value = False  # Đặt lại bộ đệm
    return score

def evaluate_king_safety(board):
    """Evaluate king safety (simplified)."""
    score = 0
    
    # Penalize exposed kings
    white_king_square = board.king_square[board.WHITE_INDEX]
    black_king_square = board.king_square[board.BLACK_INDEX]
    
    # Check if kings are close to the edge (safer in the opening/middlegame)
    if not is_endgame_position(board):
        white_king_file = white_king_square % 8
        white_king_rank = white_king_square // 8
        black_king_file = black_king_square % 8
        black_king_rank = black_king_square // 8
        
        # Kings should be castled (on the first rank for white, 8th for black)
        if white_king_rank != 0:
            score -= 30
        if black_king_rank != 7:
            score += 30
            
        # Kings should be toward the edges in middle game
        white_king_centrality = 3.5 - abs(3.5 - white_king_file)
        black_king_centrality = 3.5 - abs(3.5 - black_king_file)
        score -= white_king_centrality * 10
        score += black_king_centrality * 10
    
    return score
from src.core.Board.piece import *
from src.core.Board.move_generator import MoveGenerator

# Piece values in centipawns (1 pawn = 100 centipawns)
PIECE_VALUES = {
    PAWN: 10,
    KNIGHT: 30,
    BISHOP: 30,
    ROOK: 50,
    QUEEN: 90,
    KING: 900,  # High value to ensure king's safety
}

# Piece-square tables for positional evaluation
# Adapted from simplified chess programming theory
# Each table is from white's perspective, will be flipped for black
PAWN_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0,
    1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0,
    0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5,
    0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0,
    0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5,
    0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
]

KNIGHT_TABLE = [
    -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
    -4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0,
    -3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0,
    -3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0,
    -3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0,
    -3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0,
    -4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0,
    -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0
]

BISHOP_TABLE = [
    -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
    -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0,
    -1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0,
    -1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0,
    -1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0,
    -1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, -1.0,
    -1.0, 0.0, 0.5, 0.0, 0.0, 0.5, 0.0, -1.0,
    -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0
]

ROOK_TABLE = [
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5,
    -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
    -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
    -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
    -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
    -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5,
    0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0
]

QUEEN_TABLE = [
    -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
    -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0,
    -1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0,
    -0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5,
    0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5,
    -1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0,
    -1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0,
    -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0
]

KING_MIDDLE_GAME_TABLE = [
    -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
    -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
    -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
    -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
    -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0,
    -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0,
    2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0,
    2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0
]

KING_END_GAME_TABLE = [
    -5.0, -4.0, -3.0, -2.0, -2.0, -3.0, -4.0, -5.0,
    -3.0, -2.0, -1.0, 0.0, 0.0, -1.0, -2.0, -3.0,
    -3.0, -1.0, 2.0, 3.0, 3.0, 2.0, -1.0, -3.0,
    -3.0, -1.0, 3.0, 4.0, 4.0, 3.0, -1.0, -3.0,
    -3.0, -1.0, 3.0, 4.0, 4.0, 3.0, -1.0, -3.0,
    -3.0, -1.0, 2.0, 3.0, 3.0, 2.0, -1.0, -3.0,
    -3.0, -3.0, 0.0, 0.0, 0.0, 0.0, -3.0, -3.0,
    -5.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -5.0
]


# Dictionary to map pieces to their position tables
POSITION_TABLES = {
    PAWN: PAWN_TABLE,
    KNIGHT: KNIGHT_TABLE,
    BISHOP: BISHOP_TABLE,
    ROOK: ROOK_TABLE,
    QUEEN: QUEEN_TABLE,
    KING: KING_MIDDLE_GAME_TABLE,  # Default to middle game
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
    # white_king_captured, black_king_captured = board.is_king_captured()
    # if white_king_captured:
    #     return -700  # Black wins
    # if black_king_captured:
    #     return 700  # White wins
    
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
            position_score += piece_value + piece_position_score
        else:
            position_score -= piece_value + piece_position_score

    # Check for specific board features
    mobility_score = evaluate_mobility(board)
    pawn_structure_score = evaluate_pawn_structure(board)
    # fifty_move_rule_score = evaluate_fifty_move_rule(board)
    stalemate_score = evaluate_stalemate(board)
    
    # show all scores
    # print(f"Position Score: {position_score}")
    # print(f"Mobility Score: {mobility_score}")
    # print(f"Pawn Structure Score: {pawn_structure_score}")
    # print(f"Stalemate Score: {stalemate_score}")
    # Combine all scoring factors
    score = (
        position_score
        + mobility_score
        + pawn_structure_score
        # + fifty_move_rule_score
        + stalemate_score
    )

    return score


def is_endgame_position(board):
    """Determine if the position is an endgame based on material."""
    # Count major pieces (queen and rooks)
    white_major_pieces = count_major_pieces(board, True)
    black_major_pieces = count_major_pieces(board, False)

    # Endgame if both sides have 1 or fewer major pieces, or if queens are off the board
    return (white_major_pieces <= 1 and black_major_pieces <= 1) or (
        board.all_piece_lists[WHITE_QUEEN].count == 0
        and board.all_piece_lists[BLACK_QUEEN].count == 0
    )


def count_major_pieces(board, is_white):
    """Count major pieces (queen and rooks) for a specific color."""
    color = WHITE if is_white else BLACK
    queen_piece = make_piece(QUEEN, color)
    rook_piece = make_piece(ROOK, color)
    return (
        board.all_piece_lists[queen_piece].count
        + board.all_piece_lists[rook_piece].count
    )


def evaluate_mobility(board):
    """Evaluate piece mobility (simplified)."""
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
    # return (white_mobility - black_mobility) * 100
    if original_is_white_to_move:
        return (- black_mobility)
    else:
        return (white_mobility)


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


# def evaluate_fifty_move_rule(board):
#     """
#     Evaluate the position based on the fifty move rule counter.
#     Penalizes positions that are getting close to a draw by the 50-move rule.
#     Returns a score that is applied from the perspective of the side to move.
#     """
#     # Get the current fifty move counter (increments with each half-move without capture or pawn move)
#     fifty_move_counter = board.fifty_move_counter
    
#     # If we're very close to a draw by fifty move rule (over 80 half-moves)
#     penalty = (fifty_move_counter) * 50

#     if board.is_white_to_move:
#         return penalty
#     else:
#         return -penalty
    
def is_stalemate(board):
    """
    Check if the position is a stalemate (no legal moves and not in check).
    
    Parameters:
    - board: Current board state
    
    Returns:
    - True if stalemate, False otherwise
    """
    
    move_gen = MoveGenerator(board)
    legal_moves = move_gen.generate_legal_moves()
    
    # Stalemate occurs when there are no legal moves and the king is not in check
    return not legal_moves and not board.is_in_check()

def evaluate_stalemate(board):
    """
    Evaluate stalemate position with a penalty.
    Returns a negative score to be added to total evaluation.
    
    Parameters:
    - board: Current board state
    
    Returns:
    - Penalty score for stalemate (-100)
    """
    if is_stalemate(board):
        if board.is_white_to_move:
            return 10000
        else:
            return -10000
    return 0
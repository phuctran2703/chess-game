# Bitboard utility functions for chess engine

def set_square(bitboard, square_index):
    return bitboard | (1 << square_index)

def clear_square(bitboard, square_index):
    return bitboard & ~(1 << square_index)

def toggle_square(bitboard, square_index):
    return bitboard ^ (1 << square_index)

def toggle_squares(bitboard, square_a, square_b):
    return bitboard ^ ((1 << square_a) | (1 << square_b))

def contains_square(bitboard, square):
    return ((bitboard >> square) & 1) != 0

def shift(bitboard, num_squares_to_shift):
    if num_squares_to_shift > 0:
        return bitboard << num_squares_to_shift
    else:
        return bitboard >> -num_squares_to_shift

# Helper functions for bitboard attack generation

def knight_attacks(square):
    attacks = 0
    rank = square // 8
    file = square % 8
    knight_moves = [
        (2, 1), (1, 2), (-1, 2), (-2, 1),
        (-2, -1), (-1, -2), (1, -2), (2, -1)
    ]
    for dr, df in knight_moves:
        r, f = rank + dr, file + df
        if 0 <= r < 8 and 0 <= f < 8:
            attacks |= 1 << (r * 8 + f)
    return attacks

def king_attacks(square):
    attacks = 0
    rank = square // 8
    file = square % 8
    king_moves = [
        (1, 0), (1, 1), (0, 1), (-1, 1),
        (-1, 0), (-1, -1), (0, -1), (1, -1)
    ]
    for dr, df in king_moves:
        r, f = rank + dr, file + df
        if 0 <= r < 8 and 0 <= f < 8:
            attacks |= 1 << (r * 8 + f)
    return attacks

def white_pawn_attacks(square):
    attacks = 0
    rank = square // 8
    file = square % 8
    if rank < 7:
        if file > 0:
            attacks |= 1 << ((rank + 1) * 8 + (file - 1))
        if file < 7:
            attacks |= 1 << ((rank + 1) * 8 + (file + 1))
    return attacks

def black_pawn_attacks(square):
    attacks = 0
    rank = square // 8
    file = square % 8
    if rank > 0:
        if file > 0:
            attacks |= 1 << ((rank - 1) * 8 + (file - 1))
        if file < 7:
            attacks |= 1 << ((rank - 1) * 8 + (file + 1))
    return attacks

# Precompute attack tables
KNIGHT_ATTACKS = [knight_attacks(sq) for sq in range(64)]
KING_MOVES = [king_attacks(sq) for sq in range(64)]
WHITE_PAWN_ATTACKS = [white_pawn_attacks(sq) for sq in range(64)]
BLACK_PAWN_ATTACKS = [black_pawn_attacks(sq) for sq in range(64)]

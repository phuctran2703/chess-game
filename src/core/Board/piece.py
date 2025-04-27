# Piece Types
NONE = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6

# Piece Colours
WHITE = 0
BLACK = 8

# Pieces
WHITE_PAWN = PAWN | WHITE  # 1
WHITE_KNIGHT = KNIGHT | WHITE  # 2
WHITE_BISHOP = BISHOP | WHITE  # 3
WHITE_ROOK = ROOK | WHITE  # 4
WHITE_QUEEN = QUEEN | WHITE  # 5
WHITE_KING = KING | WHITE  # 6

BLACK_PAWN = PAWN | BLACK  # 9
BLACK_KNIGHT = KNIGHT | BLACK  # 10
BLACK_BISHOP = BISHOP | BLACK  # 11
BLACK_ROOK = ROOK | BLACK  # 12
BLACK_QUEEN = QUEEN | BLACK  # 13
BLACK_KING = KING | BLACK  # 14

MAX_PIECE_INDEX = BLACK_KING

PIECE_INDICES = [
    WHITE_PAWN, WHITE_KNIGHT, WHITE_BISHOP, WHITE_ROOK, WHITE_QUEEN, WHITE_KING,
    BLACK_PAWN, BLACK_KNIGHT, BLACK_BISHOP, BLACK_ROOK, BLACK_QUEEN, BLACK_KING
]

# Bit Masks
type_mask = 0b0111
colour_mask = 0b1000

def make_piece(piece_type, piece_colour):
    return piece_type | piece_colour

def make_piece_bool(piece_type, piece_is_white):
    return make_piece(piece_type, WHITE if piece_is_white else BLACK)

def is_colour(piece, colour):
    return (piece & colour_mask) == colour and piece != 0

def is_white(piece):
    return is_colour(piece, WHITE)

def piece_colour(piece):
    return piece & colour_mask

def piece_type(piece):
    return piece & type_mask

def is_orthogonal_slider(piece):
    return piece_type(piece) in (QUEEN, ROOK)

def is_diagonal_slider(piece):
    return piece_type(piece) in (QUEEN, BISHOP)

def is_sliding_piece(piece):
    return piece_type(piece) in (QUEEN, BISHOP, ROOK)

def get_symbol(piece):
    pt = piece_type(piece)
    symbol = {
        ROOK: 'R',
        KNIGHT: 'N',
        BISHOP: 'B',
        QUEEN: 'Q',
        KING: 'K',
        PAWN: 'P',
    }.get(pt, ' ')
    if not is_white(piece):
        symbol = symbol.lower()
    return symbol

def get_piece_type_from_symbol(symbol):
    symbol = symbol.upper()
    return {
        'R': ROOK,
        'N': KNIGHT,
        'B': BISHOP,
        'Q': QUEEN,
        'K': KING,
        'P': PAWN,
    }.get(symbol, NONE)


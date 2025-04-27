from collections import namedtuple

# Coord structure
Coord = namedtuple('Coord', ['file_index', 'rank_index'])

ROOK_DIRECTIONS = [Coord(-1, 0), Coord(1, 0), Coord(0, 1), Coord(0, -1)]
BISHOP_DIRECTIONS = [Coord(-1, 1), Coord(1, 1), Coord(1, -1), Coord(-1, -1)]

FILE_NAMES = "abcdefgh"
RANK_NAMES = "12345678"

a1, b1, c1, d1, e1, f1, g1, h1 = 0, 1, 2, 3, 4, 5, 6, 7
a8, b8, c8, d8, e8, f8, g8, h8 = 56, 57, 58, 59, 60, 61, 62, 63

def rank_index(square_index):
    return square_index >> 3

def file_index(square_index):
    return square_index & 0b111

def index_from_coord(file_idx, rank_idx):
    return rank_idx * 8 + file_idx

def index_from_coord_obj(coord):
    return index_from_coord(coord.file_index, coord.rank_index)

def coord_from_index(square_index):
    return Coord(file_index(square_index), rank_index(square_index))

def light_square(file_idx, rank_idx):
    return (file_idx + rank_idx) % 2 != 0

def light_square_index(square_index):
    return light_square(file_index(square_index), rank_index(square_index))

def square_name_from_coordinate(file_idx, rank_idx):
    return f"{FILE_NAMES[file_idx]}{rank_idx+1}"

def square_name_from_index(square_index):
    return square_name_from_coordinate(*coord_from_index(square_index))

def square_name_from_coord_obj(coord):
    return square_name_from_coordinate(coord.file_index, coord.rank_index)

def square_index_from_name(name):
    file_char, rank_char = name[0], name[1]
    file_idx = FILE_NAMES.index(file_char)
    rank_idx = RANK_NAMES.index(rank_char)
    return index_from_coord(file_idx, rank_idx)

def is_valid_coordinate(x, y):
    return 0 <= x < 8 and 0 <= y < 8

# ASCII diagram function (stub, needs Board, Piece, FenUtility, etc.)
def create_diagram(board, black_at_top=True, include_fen=True, include_zobrist_key=True):
    # TODO: Implement using board, piece, fen_utility modules
    return "<Board diagram here>"

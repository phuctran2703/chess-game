from collections import namedtuple
from src.core.helper.board_helper import *
from src.core.Board.piece import *

START_POSITION_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

class PositionInfo:
    def __init__(self, fen):
        self.fen = fen
        self.squares = [NONE] * 64 # Thông tin vị trí của các quân cờ
        sections = fen.split(' ')
        file = 0
        rank = 7
        for symbol in sections[0]:
            if symbol == '/':
                file = 0
                rank -= 1
            elif symbol.isdigit():
                file += int(symbol)
            else:
                piece_colour = WHITE if symbol.isupper() else BLACK
                piece_type = {
                    'k': KING,
                    'p': PAWN,
                    'n': KNIGHT,
                    'b': BISHOP,
                    'r': ROOK,
                    'q': QUEEN
                }.get(symbol.lower(), NONE)
                self.squares[rank * 8 + file] = piece_type | piece_colour
                file += 1
        self.white_to_move = (sections[1] == 'w')
        castling_rights = sections[2]
        self.white_castle_kingside = 'K' in castling_rights
        self.white_castle_queenside = 'Q' in castling_rights
        self.black_castle_kingside = 'k' in castling_rights
        self.black_castle_queenside = 'q' in castling_rights
        
        self.ep_file = 0
        self.fifty_move_ply_count = 0
        self.move_count = 0
        if len(sections) > 3:
            en_passant_file_name = sections[3][0]
            if en_passant_file_name in FILE_NAMES:
                self.ep_file = FILE_NAMES.index(en_passant_file_name) + 1
        if len(sections) > 4:
            try:
                self.fifty_move_ply_count = int(sections[4])
            except:
                self.fifty_move_ply_count = 0
        if len(sections) > 5:
            try:
                self.move_count = int(sections[5])
            except:
                self.move_count = 0

def position_from_fen(fen):
    return PositionInfo(fen)

def current_fen(board, always_include_ep_square=True):
    # Piece placement
    fen_rows = []
    for rank in range(7, -1, -1):
        row = ''
        empty = 0
        for file in range(8):
            sq = rank * 8 + file
            piece = board.square[sq]
            if piece == NONE:
                empty += 1
            else:
                if empty > 0:
                    row += str(empty)
                    empty = 0
                row += get_symbol(piece)
        if empty > 0:
            row += str(empty)
        fen_rows.append(row)
    fen = '/'.join(fen_rows)

    # Active color
    fen += ' ' + ('w' if board.is_white_to_move else 'b')

    # Castling rights
    rights = ''
    gs = board.current_game_state
    if gs:
        if gs.has_kingside_castle_right(True):
            rights += 'K'
        if gs.has_queenside_castle_right(True):
            rights += 'Q'
        if gs.has_kingside_castle_right(False):
            rights += 'k'
        if gs.has_queenside_castle_right(False):
            rights += 'q'
    fen += ' ' + (rights if rights else '-')

    # En passant target square
    ep = '-'
    if gs and gs.en_passant_file:
        file_idx = gs.en_passant_file - 1
        rank_idx = 5 if board.is_white_to_move else 2
        ep = FILE_NAMES[file_idx] + RANK_NAMES[rank_idx]
    fen += ' ' + ep

    # Halfmove clock
    halfmove = gs.fifty_move_counter if gs else 0
    fen += f' {halfmove}'

    # Fullmove number
    fullmove = (board.ply_count // 2) + 1
    fen += f' {fullmove}'
    return fen

def flip_fen(fen):
    sections = fen.split(' ')
    fen_ranks = sections[0].split('/')
    flipped_fen = ''
    for i in range(len(fen_ranks)-1, -1, -1):
        rank = fen_ranks[i]
        for c in rank:
            flipped_fen += c.swapcase() if c.isalpha() else c
        if i != 0:
            flipped_fen += '/'
    flipped_fen += ' ' + ('b' if sections[1][0] == 'w' else 'w')
    castling_rights = sections[2]
    flipped_rights = ''
    for c in 'kqKQ':
        if c in castling_rights:
            flipped_rights += c.swapcase()
    flipped_fen += ' ' + (flipped_rights if flipped_rights else '-')
    ep = sections[3]
    flipped_ep = ep[0]
    if len(ep) > 1:
        flipped_ep += '3' if ep[1] == '6' else '6'
    flipped_fen += ' ' + flipped_ep
    flipped_fen += ' ' + sections[4] + ' ' + sections[5]
    return flipped_fen

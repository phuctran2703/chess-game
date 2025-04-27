import random
from src.core.Board.piece import MAX_PIECE_INDEX, PIECE_INDICES, NONE, piece_type

class Zobrist:
    pieces_array = [[0 for _ in range(64)] for _ in range(MAX_PIECE_INDEX + 1)]
    castling_rights = [0 for _ in range(16)]
    en_passant_file = [0 for _ in range(9)]
    side_to_move = 0

    @classmethod
    def initialize(cls, seed=29426028):
        rng = random.Random(seed)
        for square_index in range(64):
            for piece in PIECE_INDICES:
                cls.pieces_array[piece][square_index] = cls.random_unsigned_64bit_number(rng)
        for i in range(len(cls.castling_rights)):
            cls.castling_rights[i] = cls.random_unsigned_64bit_number(rng)
        for i in range(len(cls.en_passant_file)):
            cls.en_passant_file[i] = 0 if i == 0 else cls.random_unsigned_64bit_number(rng)
        cls.side_to_move = cls.random_unsigned_64bit_number(rng)

    @staticmethod
    def random_unsigned_64bit_number(rng):
        return rng.getrandbits(64)

    @classmethod
    def calculate_zobrist_key(cls, board):
        zobrist_key = 0
        for square_index in range(64):
            piece = board.squares[square_index // 8][square_index % 8] if hasattr(board, 'squares') else board.square[square_index]
            if piece_type(piece) != NONE:
                zobrist_key ^= cls.pieces_array[piece][square_index]
        en_passant_file = getattr(getattr(board, 'current_game_state', None), 'en_passant_file', None)
        if en_passant_file is not None:
            zobrist_key ^= cls.en_passant_file[en_passant_file]
        move_colour = getattr(board, 'move_colour', None)
        if move_colour is not None and move_colour == 8:  # 8 = BLACK
            zobrist_key ^= cls.side_to_move
        castling_rights = getattr(getattr(board, 'current_game_state', None), 'castling_rights', None)
        if castling_rights is not None:
            zobrist_key ^= cls.castling_rights[castling_rights]
        return zobrist_key

Zobrist.initialize()
class GameState:
    CLEAR_WHITE_KINGSIDE_MASK = 0b1110
    CLEAR_WHITE_QUEENSIDE_MASK = 0b1101
    CLEAR_BLACK_KINGSIDE_MASK = 0b1011
    CLEAR_BLACK_QUEENSIDE_MASK = 0b0111

    def __init__(
        self,
        captured_piece_type,
        en_passant_file,
        castling_rights,
        fifty_move_counter,
        zobrist_key,
    ):
        self.captured_piece_type = (
            captured_piece_type  # Stores the type of captured piece in the game
        )
        self.en_passant_file = en_passant_file  # Stores the position of opponent pawn that can be captured by en passant
        self.castling_rights = castling_rights  # Stores the castling rights of pieces
        self.fifty_move_counter = fifty_move_counter  # Stores the number of moves made without any piece capture or pawn movement
        self.zobrist_key = (
            zobrist_key  # Stores the Zobrist key value of the current game position
        )

    def has_kingside_castle_right(self, white):
        mask = 1 if white else 4
        return (self.castling_rights & mask) != 0

    def has_queenside_castle_right(self, white):
        mask = 2 if white else 8
        return (self.castling_rights & mask) != 0

    @staticmethod
    def clear_white_kingside(castling_rights):
        return castling_rights & GameState.CLEAR_WHITE_KINGSIDE_MASK

    @staticmethod
    def clear_white_queenside(castling_rights):
        return castling_rights & GameState.CLEAR_WHITE_QUEENSIDE_MASK

    @staticmethod
    def clear_black_kingside(castling_rights):
        return castling_rights & GameState.CLEAR_BLACK_KINGSIDE_MASK

    @staticmethod
    def clear_black_queenside(castling_rights):
        return castling_rights & GameState.CLEAR_BLACK_QUEENSIDE_MASK

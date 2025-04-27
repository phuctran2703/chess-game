# Move representation and flags for chess engine
class Move:
    NO_FLAG = 0b0000
    EN_PASSANT_CAPTURE_FLAG = 0b0001
    CASTLE_FLAG = 0b0010
    PAWN_TWO_UP_FLAG = 0b0011
    PROMOTE_TO_QUEEN_FLAG = 0b0100
    PROMOTE_TO_KNIGHT_FLAG = 0b0101
    PROMOTE_TO_ROOK_FLAG = 0b0110
    PROMOTE_TO_BISHOP_FLAG = 0b0111

    def __init__(self, start_square, target_square, move_flag=0):
        self.start_square = start_square
        self.target_square = target_square
        self.move_flag = move_flag

    @property
    def is_promotion(self):
        return self.move_flag >= Move.PROMOTE_TO_QUEEN_FLAG

    @staticmethod
    def null_move():
        return Move(0, 0, Move.NO_FLAG)

    def __eq__(self, other):
        return (
            self.start_square == other.start_square and
            self.target_square == other.target_square and
            self.move_flag == other.move_flag
        )

    def __repr__(self):
        return f"Move({self.start_square}, {self.target_square}, flag={self.move_flag})"
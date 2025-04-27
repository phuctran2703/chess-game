class PieceList:
    def __init__(self, max_piece_count=16):
        # Indices of squares occupied by given piece type (only elements up to count are valid)
        self.occupied_squares = [None] * max_piece_count
        # Map from square index to index in occupied_squares
        self.map = [None] * 64
        self.num_pieces = 0

    @property
    def count(self):
        return self.num_pieces

    def add_piece_at_square(self, square):
        self.occupied_squares[self.num_pieces] = square
        self.map[square] = self.num_pieces
        self.num_pieces += 1

    def remove_piece_at_square(self, square):
        piece_index = self.map[square]
        self.occupied_squares[piece_index] = self.occupied_squares[self.num_pieces - 1]
        self.map[self.occupied_squares[piece_index]] = piece_index
        self.num_pieces -= 1

    def move_piece(self, start_square, target_square):
        piece_index = self.map[start_square]
        self.occupied_squares[piece_index] = target_square
        self.map[target_square] = piece_index

    def __getitem__(self, index):
        return self.occupied_squares[index]
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
        # Check if we have capacity to add more pieces
        if self.num_pieces >= len(self.occupied_squares):
            # No more space in the array, cannot add more pieces
            return
        
        # Check if the square is valid
        if square < 0 or square >= 64:
            return
            
        # Check if the piece is already in the list
        if self.map[square] is not None:
            return
        
        # Add the piece
        self.occupied_squares[self.num_pieces] = square
        self.map[square] = self.num_pieces
        self.num_pieces += 1

    def remove_piece_at_square(self, square):
        # Get the index of the piece to remove
        piece_index = self.map[square]
        
        # If the piece is not found in the map, do nothing
        if piece_index is None:
            return
            
        # If we're removing the last piece, just decrease the count
        if piece_index == self.num_pieces - 1:
            self.map[square] = None
            self.num_pieces -= 1
            return
            
        # Move the last piece into the position of the removed piece
        last_square = self.occupied_squares[self.num_pieces - 1]
        self.occupied_squares[piece_index] = last_square
        
        # Update the map for the moved piece
        if last_square is not None:
            self.map[last_square] = piece_index
            
        # Clear the map entry for the removed piece
        self.map[square] = None
        
        # Decrease piece count
        self.num_pieces -= 1

    def move_piece(self, start_square, target_square):
        piece_index = self.map[start_square]
        self.occupied_squares[piece_index] = target_square
        self.map[target_square] = piece_index

    def __getitem__(self, index):
        return self.occupied_squares[index]
class Coord:
    def __init__(self, file_index, rank_index):
        self.file_index = file_index # cột (0 = cột a, 7 = cột h)
        self.rank_index = rank_index # hàng (0 = hàng 1, 7 = hàng 8)

    @classmethod
    def from_square_index(cls, square_index):
        return cls(square_index % 8, square_index // 8)

    def is_light_square(self):
        return (self.file_index + self.rank_index) % 2 != 0

    def is_valid_square(self):
        return 0 <= self.file_index < 8 and 0 <= self.rank_index < 8

    def square_index(self):
        return self.rank_index * 8 + self.file_index

    def __add__(self, other):
        return Coord(self.file_index + other.file_index, self.rank_index + other.rank_index)

    def __sub__(self, other):
        return Coord(self.file_index - other.file_index, self.rank_index - other.rank_index)

    def __mul__(self, m):
        return Coord(self.file_index * m, self.rank_index * m)

    def __eq__(self, other):
        return self.file_index == other.file_index and self.rank_index == other.rank_index

    def __repr__(self):
        return f"Coord(file={self.file_index}, rank={self.rank_index})"
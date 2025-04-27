from src.core.Board.piece import *
from src.core.Board.move import Move

class MoveGenerator:
    def __init__(self, board):
        """
        Khởi tạo MoveGenerator với một đối tượng board (bàn cờ).
        """
        self.board = board

    def generate_legal_moves(self):
        """
        Sinh ra tất cả nước đi hợp lệ cho bên đang đi dựa trên trạng thái hiện tại của bàn cờ.
        Trả về danh sách các đối tượng Move.
        """
        moves = []
        for square in range(64):
            piece = self.board.square[square]
            if piece == NONE:
                continue
            if (self.board.is_white_to_move and not is_white(piece)) or (not self.board.is_white_to_move and is_white(piece)):
                continue
            piece_type_val = piece_type(piece)
            if piece_type_val == PAWN:
                moves.extend(self._pawn_moves(square, piece))
            elif piece_type_val == KNIGHT:
                moves.extend(self._knight_moves(square, piece))
            elif piece_type_val == BISHOP:
                moves.extend(self._bishop_moves(square, piece))
            elif piece_type_val == ROOK:
                moves.extend(self._rook_moves(square, piece))
            elif piece_type_val == QUEEN:
                moves.extend(self._queen_moves(square, piece))
            elif piece_type_val == KING:
                moves.extend(self._king_moves(square, piece))
        return moves

    def _pawn_moves(self, square, piece):
        """
        Sinh ra tất cả nước đi hợp lệ cho quân tốt ở vị trí 'square'.
        Bao gồm đi thẳng, ăn chéo, phong cấp và bắt tốt qua đường (en passant).
        """
        moves = []
        direction = 8 if is_white(piece) else -8
        start_rank = 1 if is_white(piece) else 6
        promotion_rank = 6 if is_white(piece) else 1
        row = square // 8
        col = square % 8
        # One step forward
        target = square + direction
        if 0 <= target < 64 and self.board.square[target] == NONE:
            # Promotion
            if row == promotion_rank:
                for promo_flag in [Move.PROMOTE_TO_QUEEN_FLAG, Move.PROMOTE_TO_ROOK_FLAG, Move.PROMOTE_TO_BISHOP_FLAG, Move.PROMOTE_TO_KNIGHT_FLAG]:
                    moves.append(Move(square, target, promo_flag))
            else:
                moves.append(Move(square, target))
            # Two steps from start
            if row == start_rank:
                target2 = square + 2 * direction
                if self.board.square[target2] == NONE:
                    moves.append(Move(square, target2, Move.PAWN_TWO_UP_FLAG))
        # Captures
        for dc in [-1, 1]:
            c2 = col + dc
            if 0 <= c2 < 8:
                target = square + direction + dc
                if 0 <= target < 64:
                    target_piece = self.board.square[target]
                    if target_piece != NONE and is_white(target_piece) != is_white(piece):
                        # Promotion
                        if row == promotion_rank:
                            for promo_flag in [Move.PROMOTE_TO_QUEEN_FLAG, Move.PROMOTE_TO_ROOK_FLAG, Move.PROMOTE_TO_BISHOP_FLAG, Move.PROMOTE_TO_KNIGHT_FLAG]:
                                moves.append(Move(square, target, promo_flag))
                        else:
                            moves.append(Move(square, target))
        # En passant
        # Nếu tốt ở hàng 4 (trắng) hoặc 3 (đen) và có en passant file, kiểm tra nước đi en passant
        if hasattr(self.board.current_game_state, 'en_passant_file') and self.board.current_game_state.en_passant_file:
            ep_file = self.board.current_game_state.en_passant_file - 1
            ep_rank = 4 if is_white(piece) else 3
            if row == ep_rank and abs(col - ep_file) == 1:
                ep_target = (ep_rank + 1) * 8 + ep_file if is_white(piece) else (ep_rank - 1) * 8 + ep_file
                moves.append(Move(square, ep_target, Move.EN_PASSANT_CAPTURE_FLAG))
        return moves

    def _knight_moves(self, square, piece):
        """
        Sinh ra tất cả nước đi hợp lệ cho quân mã ở vị trí 'square'.
        """
        moves = []
        row = square // 8
        col = square % 8
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            r2, c2 = row + dr, col + dc
            if 0 <= r2 < 8 and 0 <= c2 < 8:
                target = r2 * 8 + c2
                target_piece = self.board.square[target]
                if target_piece == NONE or is_white(target_piece) != is_white(piece):
                    moves.append(Move(square, target))
        return moves

    def _bishop_moves(self, square, piece):
        """
        Sinh ra tất cả nước đi hợp lệ cho quân tượng ở vị trí 'square'.
        """
        moves = []
        row = square // 8
        col = square % 8
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            r2, c2 = row, col
            while True:
                r2 += dr
                c2 += dc
                if not (0 <= r2 < 8 and 0 <= c2 < 8):
                    break
                target = r2 * 8 + c2
                target_piece = self.board.square[target]
                if target_piece == NONE:
                    moves.append(Move(square, target))
                else:
                    if is_white(target_piece) != is_white(piece):
                        moves.append(Move(square, target))
                    break
        return moves

    def _rook_moves(self, square, piece):
        """
        Sinh ra tất cả nước đi hợp lệ cho quân xe ở vị trí 'square'.
        """
        moves = []
        row = square // 8
        col = square % 8
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r2, c2 = row, col
            while True:
                r2 += dr
                c2 += dc
                if not (0 <= r2 < 8 and 0 <= c2 < 8):
                    break
                target = r2 * 8 + c2
                target_piece = self.board.square[target]
                if target_piece == NONE:
                    moves.append(Move(square, target))
                else:
                    if is_white(target_piece) != is_white(piece):
                        moves.append(Move(square, target))
                    break
        return moves

    def _queen_moves(self, square, piece):
        """
        Sinh ra tất cả nước đi hợp lệ cho quân hậu ở vị trí 'square'.
        Kết hợp nước đi của xe và tượng.
        """
        return self._rook_moves(square, piece) + self._bishop_moves(square, piece)

    def _king_moves(self, square, piece):
        """
        Sinh ra tất cả nước đi hợp lệ cho quân vua ở vị trí 'square'.
        Bao gồm di chuyển thường và nhập thành.
        """
        moves = []
        row, col = divmod(square, 8)

        # Xác định các ô bị tấn công bởi đối phương
        opponent_attacks = self._generate_opponent_attacks()

        # Các nước đi thường của vua (8 hướng)
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r2, c2 = row + dr, col + dc
                if 0 <= r2 < 8 and 0 <= c2 < 8:
                    target = r2 * 8 + c2
                    target_piece = self.board.square[target]
                    if (target_piece == NONE or is_white(target_piece) != is_white(piece)) and target not in opponent_attacks:
                        moves.append(Move(square, target))

        # Xử lý nhập thành (castling)
        if hasattr(self.board.current_game_state, 'castling_rights'):
            rights = self.board.current_game_state.castling_rights
            is_white_king = is_white(piece)
            king_row = 0 if is_white_king else 7
            king_start_col = 4

            # Kingside castling (g-side)
            if (rights & (1 if is_white_king else 4)):
                if (self.board.square[king_row * 8 + 5] == NONE and
                    self.board.square[king_row * 8 + 6] == NONE and
                    (king_row * 8 + 4) not in opponent_attacks and
                    (king_row * 8 + 5) not in opponent_attacks and
                    (king_row * 8 + 6) not in opponent_attacks):
                    moves.append(Move(square, king_row * 8 + 6, Move.CASTLE_FLAG))

            # Queenside castling (c-side)
            if (rights & (2 if is_white_king else 8)):
                if (self.board.square[king_row * 8 + 1] == NONE and
                    self.board.square[king_row * 8 + 2] == NONE and
                    self.board.square[king_row * 8 + 3] == NONE and
                    (king_row * 8 + 2) not in opponent_attacks and
                    (king_row * 8 + 3) not in opponent_attacks and
                    (king_row * 8 + 4) not in opponent_attacks):
                    moves.append(Move(square, king_row * 8 + 2, Move.CASTLE_FLAG))

        return moves

    def get_legal_moves_for_square(self, square):
        """
        Trả về danh sách các ô đích mà quân ở vị trí 'square' có thể đi hợp lệ.
        """
        piece = self.board.square[square]
        if piece == NONE:
            return []
            
        # Tạo ra tất cả các nước đi hợp lệ cho quân cờ này
        if piece_type(piece) == PAWN:
            moves = self._pawn_moves(square, piece)
        elif piece_type(piece) == KNIGHT:
            moves = self._knight_moves(square, piece)
        elif piece_type(piece) == BISHOP:
            moves = self._bishop_moves(square, piece)
        elif piece_type(piece) == ROOK:
            moves = self._rook_moves(square, piece)
        elif piece_type(piece) == QUEEN:
            moves = self._queen_moves(square, piece)
        elif piece_type(piece) == KING:
            moves = self._king_moves(square, piece)
        else:
            moves = []
            
        return [move.target_square for move in moves]

    def get_move_for_square_target(self, square, target_square):
        """
        Trả về nước đi hợp lệ cho quân ở vị trí 'square' đến ô đích 'target_square'.
        """
        # Trường hợp đặc biệt cho nhập thành
        piece = self.board.square[square]
        if piece_type(piece) == KING:
            # Nếu vua di chuyển 2 ô (nhập thành)
            if abs(target_square % 8 - square % 8) == 2:
                return Move(square, target_square, Move.CASTLE_FLAG)
        
        # Trường hợp thông thường
        for move in self.generate_legal_moves():
            if move.start_square == square and move.target_square == target_square:
                return move
        return None

    def _generate_opponent_attacks(self):
        """
        Tạo ra tập hợp tất cả các ô bị quân đối phương kiểm soát.
        """
        attacks = set()
        for sq in range(64):
            piece = self.board.square[sq]
            if piece == NONE:
                continue
            if is_white(piece) == self.board.is_white_to_move:
                continue  # chỉ tính quân địch
            row, col = divmod(sq, 8)
            piece_type_val = piece_type(piece)

            if piece_type_val == PAWN:
                dir = -1 if is_white(piece) else 1
                for dc in [-1, 1]:
                    r2, c2 = row + dir, col + dc
                    if 0 <= r2 < 8 and 0 <= c2 < 8:
                        attacks.add(r2 * 8 + c2)

            elif piece_type_val == KNIGHT:
                for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                    r2, c2 = row + dr, col + dc
                    if 0 <= r2 < 8 and 0 <= c2 < 8:
                        attacks.add(r2 * 8 + c2)

            elif piece_type_val in (BISHOP, ROOK, QUEEN):
                directions = []
                if piece_type_val in (BISHOP, QUEEN):
                    directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                if piece_type_val in (ROOK, QUEEN):
                    directions += [(-1, 0), (1, 0), (0, -1), (0, 1)]

                for dr, dc in directions:
                    r2, c2 = row, col
                    while True:
                        r2 += dr
                        c2 += dc
                        if not (0 <= r2 < 8 and 0 <= c2 < 8):
                            break
                        idx = r2 * 8 + c2
                        attacks.add(idx)
                        if self.board.square[idx] != NONE:
                            break

            elif piece_type_val == KING:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        r2, c2 = row + dr, col + dc
                        if 0 <= r2 < 8 and 0 <= c2 < 8:
                            attacks.add(r2 * 8 + c2)
        return attacks

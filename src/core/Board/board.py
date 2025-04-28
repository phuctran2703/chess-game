from collections import deque
from src.core.Board.piece import *
from src.core.Board.piece_list import PieceList
from src.core.Board.move import Move
from src.core.Board.bitboard_utility import *
from src.core.Board.magic import *
from src.core.Board.game_state import GameState
from src.core.Board.zobrist import Zobrist
from src.core.helper.board_helper import *
from src.core.helper.move_utility import *
from src.core.helper.fen_utility import *

class Board:
    WHITE_INDEX = 0
    BLACK_INDEX = 1

    def __init__(self):
        # Cấu trúc dữ liệu bàn cờ
        self.square = [NONE] * 64  # Mảng 64 ô, lưu loại quân trên mỗi ô
        self.king_square = [None, None]  # Vị trí quân vua [trắng, đen]
        self.piece_bitboards = [0] * (MAX_PIECE_INDEX + 1)  # Bitboard cho từng loại quân
        self.colour_bitboards = [0, 0]  # Bitboards cho quân [trắng, đen]
        self.all_pieces_bitboard = 0  # Bitboard tổng hợp tất cả quân

        # Quân trượt (sliders)
        self.friendly_orthogonal_sliders = 0  # Xe và hậu của phe đang đi
        self.friendly_diagonal_sliders = 0  # Tượng và hậu của phe đang đi
        self.enemy_orthogonal_sliders = 0  # Xe và hậu của phe đối phương
        self.enemy_diagonal_sliders = 0  # Tượng và hậu của phe đối phương
        
        # Thống kê quân
        self.total_piece_count_without_pawns_and_kings = 0

        # Danh sách các quân theo loại
        self.rooks = [PieceList(10), PieceList(10)]
        self.bishops = [PieceList(10), PieceList(10)]
        self.queens = [PieceList(9), PieceList(9)]
        self.knights = [PieceList(10), PieceList(10)]
        self.pawns = [PieceList(8), PieceList(8)]
        self.all_piece_lists = [None] * (MAX_PIECE_INDEX + 1)
        self._init_piece_lists()

        # Trạng thái bàn cờ
        self.is_white_to_move = True  # Đến lượt trắng hay không
        self.ply_count = 0  # Số nước đi
        self.all_game_moves = []  # Lịch sử các nước đi
        self.current_game_state = None  # Trạng thái hiện tại
        
        # Lịch sử và bộ nhớ đệm
        self.repetition_position_history = deque(maxlen=64)  # Lịch sử vị trí kiểm tra lặp
        self.game_state_history = deque(maxlen=64)  # Lịch sử trạng thái để hoàn tác
        self.cached_in_check_value = False  # Giá trị chiếu tướng đã cache
        self.has_cached_in_check_value = False  # Có giá trị cache không

    def _init_piece_lists(self):
        """Khởi tạo danh sách các quân"""
        self.all_piece_lists[WHITE_PAWN] = self.pawns[self.WHITE_INDEX]
        self.all_piece_lists[WHITE_KNIGHT] = self.knights[self.WHITE_INDEX]
        self.all_piece_lists[WHITE_BISHOP] = self.bishops[self.WHITE_INDEX]
        self.all_piece_lists[WHITE_ROOK] = self.rooks[self.WHITE_INDEX]
        self.all_piece_lists[WHITE_QUEEN] = self.queens[self.WHITE_INDEX]
        self.all_piece_lists[WHITE_KING] = PieceList(1)

        self.all_piece_lists[BLACK_PAWN] = self.pawns[self.BLACK_INDEX]
        self.all_piece_lists[BLACK_KNIGHT] = self.knights[self.BLACK_INDEX]
        self.all_piece_lists[BLACK_BISHOP] = self.bishops[self.BLACK_INDEX]
        self.all_piece_lists[BLACK_ROOK] = self.rooks[self.BLACK_INDEX]
        self.all_piece_lists[BLACK_QUEEN] = self.queens[self.BLACK_INDEX]
        self.all_piece_lists[BLACK_KING] = PieceList(1)
        
    def is_king_captured(self):
        """Kiểm tra xem quân vua có bị bắt không"""
        white_king_captured = self.all_piece_lists[WHITE_KING].count == 0
        black_king_captured = self.all_piece_lists[BLACK_KING].count == 0
        return white_king_captured, black_king_captured

    @property
    def move_colour(self):
        """Màu của bên đang đi"""
        return WHITE if self.is_white_to_move else BLACK

    @property
    def opponent_colour(self):
        """Màu của bên đối phương"""
        return BLACK if self.is_white_to_move else WHITE

    @property
    def move_colour_index(self):
        """Chỉ số màu của bên đang đi"""
        return self.WHITE_INDEX if self.is_white_to_move else self.BLACK_INDEX

    @property
    def opponent_colour_index(self):
        """Chỉ số màu của bên đối phương"""
        return self.BLACK_INDEX if self.is_white_to_move else self.WHITE_INDEX

    @property
    def fifty_move_counter(self):
        """Bộ đếm 50 nước đi"""
        return self.current_game_state.fifty_move_counter if self.current_game_state else 0

    @property
    def zobrist_key(self):
        """Khóa zobrist của trạng thái hiện tại"""
        return self.current_game_state.zobrist_key if self.current_game_state else 0

    def make_move(self, move, in_search=False):
        """Thực hiện một nước đi"""
        # Lấy thông tin cơ bản từ nước đi
        start_square = move.start_square
        target_square = move.target_square
        move_flag = move.move_flag
        is_promotion = move.is_promotion
        is_en_passant = move_flag == Move.EN_PASSANT_CAPTURE_FLAG
        
        # Quân cờ liên quan
        moved_piece = self.square[start_square]
        moved_piece_type = piece_type(moved_piece)
        captured_piece = self.square[target_square] if not is_en_passant else make_piece(PAWN, self.opponent_colour)
        captured_piece_type = piece_type(captured_piece)
        
        # Trạng thái bàn cờ
        prev_castle_state = self.current_game_state.castling_rights if self.current_game_state else 0
        new_zobrist_key = self.current_game_state.zobrist_key if self.current_game_state else 0
        new_castling_rights = prev_castle_state
        new_en_passant_file = 0
        
        # Xử lý việc bắt quân
        if captured_piece_type != NONE:
            capture_square = target_square
            if is_en_passant:
                capture_square = target_square + (-8 if self.is_white_to_move else 8)
            self.all_piece_lists[captured_piece].remove_piece_at_square(capture_square)
            self.piece_bitboards[captured_piece] = clear_square(self.piece_bitboards[captured_piece], capture_square)
            self.colour_bitboards[self.opponent_colour_index] = clear_square(self.colour_bitboards[self.opponent_colour_index], capture_square)
            self.square[capture_square] = NONE
            
        # Di chuyển quân cờ
        self.move_piece(moved_piece, start_square, target_square)
        
        # Xử lý quân vua và nhập thành
        if moved_piece_type == KING:
            self.king_square[self.move_colour_index] = target_square
            new_castling_rights &= (GameState.CLEAR_WHITE_KINGSIDE_MASK if self.is_white_to_move else GameState.CLEAR_BLACK_KINGSIDE_MASK)
            if move_flag == Move.CASTLE_FLAG:
                kingside = target_square in [62, 6]
                castling_rook_from = target_square + 1 if kingside else target_square - 2
                castling_rook_to = target_square - 1 if kingside else target_square + 1
                rook_piece = make_piece(ROOK, self.move_colour)
                self.move_piece(rook_piece, castling_rook_from, castling_rook_to)
                
        # Xử lý phong cấp tốt
        if is_promotion:
            promotion_piece_type = {
                Move.PROMOTE_TO_QUEEN_FLAG: QUEEN,
                Move.PROMOTE_TO_ROOK_FLAG: ROOK,
                Move.PROMOTE_TO_KNIGHT_FLAG: KNIGHT,
                Move.PROMOTE_TO_BISHOP_FLAG: BISHOP
            }.get(move_flag, QUEEN)
            promotion_piece = make_piece(promotion_piece_type, self.move_colour)
            self.all_piece_lists[moved_piece].remove_piece_at_square(target_square)
            self.all_piece_lists[promotion_piece].add_piece_at_square(target_square)
            self.piece_bitboards[moved_piece] = clear_square(self.piece_bitboards[moved_piece], target_square)
            self.piece_bitboards[promotion_piece] = set_square(self.piece_bitboards[promotion_piece], target_square)
            self.square[target_square] = promotion_piece
            
        # Xử lý tốt đi hai ô
        if move_flag == Move.PAWN_TWO_UP_FLAG:
            new_en_passant_file = start_square % 8 + 1
            
        # Cập nhật quyền nhập thành
        if prev_castle_state != 0:
            if target_square in [7, 0] or start_square in [7, 0]:
                if start_square == 7 or target_square == 7:
                    new_castling_rights = GameState.clear_white_kingside(new_castling_rights)
                if start_square == 0 or target_square == 0:
                    new_castling_rights = GameState.clear_white_queenside(new_castling_rights)
            if target_square in [63, 56] or start_square in [63, 56]:
                if start_square == 63 or target_square == 63:
                    new_castling_rights = GameState.clear_black_kingside(new_castling_rights)
                if start_square == 56 or target_square == 56:
                    new_castling_rights = GameState.clear_black_queenside(new_castling_rights)
                    
        # Cập nhật lượt đi và bộ đếm
        self.is_white_to_move = not self.is_white_to_move
        self.ply_count += 1
        new_fifty_move_counter = (self.current_game_state.fifty_move_counter + 1) if self.current_game_state else 0
        
        # Reset bộ đếm 50 nước nếu di chuyển tốt hoặc bắt quân
        if moved_piece_type == PAWN or captured_piece_type != NONE:
            new_fifty_move_counter = 0
            if not in_search:
                self.repetition_position_history.clear()
                
        # Cập nhật bitboards và trạng thái
        self.all_pieces_bitboard = self.colour_bitboards[self.WHITE_INDEX] | self.colour_bitboards[self.BLACK_INDEX]
        self.update_slider_bitboards()
        new_zobrist_key ^= Zobrist.side_to_move
        
        # Cập nhật trạng thái bàn cờ
        new_state = GameState(captured_piece_type, new_en_passant_file, new_castling_rights, new_fifty_move_counter, new_zobrist_key)
        self.game_state_history.append(new_state)
        self.current_game_state = new_state
        self.has_cached_in_check_value = False
        
        # Cập nhật lịch sử
        if not in_search:
            self.repetition_position_history.append(new_state.zobrist_key)
            self.all_game_moves.append(move)

    def unmake_move(self, move, in_search=False):
        """Hoàn tác một nước đi"""
        # Đổi lượt đi
        self.is_white_to_move = not self.is_white_to_move
        
        # Thông tin nước đi
        moved_from = move.start_square
        moved_to = move.target_square
        move_flag = move.move_flag
        is_promotion = move.is_promotion
        
        # Quân cờ
        moved_piece = self.square[moved_to] if not is_promotion else make_piece(PAWN, self.move_colour)
        moved_piece_type = piece_type(moved_piece)
        captured_piece_type = self.current_game_state.captured_piece_type
        
        # Loại nước đi
        undoing_en_passant = move_flag == Move.EN_PASSANT_CAPTURE_FLAG
        undoing_capture = captured_piece_type != NONE
        
        # Xử lý phong cấp
        if is_promotion:
            promoted_piece = self.square[moved_to]
            pawn_piece = make_piece(PAWN, self.move_colour)
            self.all_piece_lists[promoted_piece].remove_piece_at_square(moved_to)
            self.all_piece_lists[pawn_piece].add_piece_at_square(moved_to)
            self.piece_bitboards[promoted_piece] = clear_square(self.piece_bitboards[promoted_piece], moved_to)
            self.piece_bitboards[pawn_piece] = set_square(self.piece_bitboards[pawn_piece], moved_to)
            
        # Di chuyển quân về vị trí cũ
        self.move_piece(moved_piece, moved_to, moved_from)
        
        # Phục hồi quân bị bắt
        if undoing_capture:
            capture_square = moved_to
            if undoing_en_passant:
                capture_square = moved_to + (-8 if self.is_white_to_move else 8)
            captured_piece = make_piece(captured_piece_type, self.opponent_colour)
            self.piece_bitboards[captured_piece] = set_square(self.piece_bitboards[captured_piece], capture_square)
            self.colour_bitboards[self.opponent_colour_index] = set_square(self.colour_bitboards[self.opponent_colour_index], capture_square)
            self.all_piece_lists[captured_piece].add_piece_at_square(capture_square)
            self.square[capture_square] = captured_piece
            
        # Xử lý nhập thành
        if moved_piece_type == KING and move_flag == Move.CASTLE_FLAG:
            kingside = moved_to in [62, 6]
            rook_piece = make_piece(ROOK, self.move_colour)
            rook_square_after = moved_to - 1 if kingside else moved_to + 1
            rook_square_before = moved_to + 1 if kingside else moved_to - 2
            self.move_piece(rook_piece, rook_square_after, rook_square_before)
            
        # Cập nhật vị trí vua
        if moved_piece_type == KING:
            self.king_square[self.move_colour_index] = moved_from
            
        # Cập nhật bitboards
        self.all_pieces_bitboard = self.colour_bitboards[self.WHITE_INDEX] | self.colour_bitboards[self.BLACK_INDEX]
        self.update_slider_bitboards()
        
        # Cập nhật lịch sử
        if not in_search and self.repetition_position_history:
            self.repetition_position_history.pop()
            if self.all_game_moves:
                self.all_game_moves.pop()
                
        # Khôi phục trạng thái bàn cờ
        if self.game_state_history:
            self.game_state_history.pop()
            if self.game_state_history:
                self.current_game_state = self.game_state_history[-1]
                
        self.ply_count -= 1
        self.has_cached_in_check_value = False

    def make_null_move(self):
        """Thực hiện nước đi rỗng (không thay đổi bàn cờ, chỉ đổi lượt)"""
        self.is_white_to_move = not self.is_white_to_move
        self.ply_count += 1
        new_zobrist_key = self.current_game_state.zobrist_key ^ Zobrist.side_to_move ^ Zobrist.en_passant_file[self.current_game_state.en_passant_file]
        new_state = GameState(NONE, 0, self.current_game_state.castling_rights, self.current_game_state.fifty_move_counter + 1, new_zobrist_key)
        self.current_game_state = new_state
        self.game_state_history.append(new_state)
        self.update_slider_bitboards()
        self.has_cached_in_check_value = True
        self.cached_in_check_value = False

    def unmake_null_move(self):
        """Hoàn tác nước đi rỗng"""
        self.is_white_to_move = not self.is_white_to_move
        self.ply_count -= 1
        if self.game_state_history:
            self.game_state_history.pop()
            if self.game_state_history:
                self.current_game_state = self.game_state_history[-1]
        self.update_slider_bitboards()
        self.has_cached_in_check_value = True
        self.cached_in_check_value = False

    def is_in_check(self):
        """Kiểm tra xem vua có bị chiếu không"""
        if self.has_cached_in_check_value:
            return self.cached_in_check_value
        self.cached_in_check_value = self.calculate_in_check_state()
        self.has_cached_in_check_value = True
        return self.cached_in_check_value

    def calculate_in_check_state(self):
        """Tính toán trạng thái chiếu"""
        king_square = self.king_square[self.move_colour_index]
        blockers = self.all_pieces_bitboard
        
        # Kiểm tra chiếu từ xe và hậu
        if self.enemy_orthogonal_sliders != 0:
            rook_attacks = get_rook_attacks(king_square, blockers)
            if rook_attacks & self.enemy_orthogonal_sliders:
                return True
                
        # Kiểm tra chiếu từ tượng và hậu
        if self.enemy_diagonal_sliders != 0:
            bishop_attacks = get_bishop_attacks(king_square, blockers)
            if bishop_attacks & self.enemy_diagonal_sliders:
                return True
                
        # Kiểm tra chiếu từ mã
        enemy_knights = self.piece_bitboards[make_piece(KNIGHT, self.opponent_colour)]
        if KNIGHT_ATTACKS[king_square] & enemy_knights:
            return True
            
        # Kiểm tra chiếu từ tốt
        enemy_pawns = self.piece_bitboards[make_piece(PAWN, self.opponent_colour)]
        pawn_attack_mask = WHITE_PAWN_ATTACKS[king_square] if self.is_white_to_move else BLACK_PAWN_ATTACKS[king_square]
        if pawn_attack_mask & enemy_pawns:
            return True
            
        return False

    def load_start_position(self):
        """Tải vị trí bắt đầu chuẩn"""
        from src.core.helper.fen_utility import START_POSITION_FEN
        self.load_position(START_POSITION_FEN)

    def load_position(self, fen):
        """Tải vị trí từ chuỗi FEN"""
        from src.core.helper.fen_utility import position_from_fen
        pos_info = position_from_fen(fen)
        self.load_position_info(pos_info)

    def load_position_info(self, pos_info):
        """Tải vị trí từ thông tin vị trí"""
        self.initialize()
        
        # Cài đặt các quân cờ
        for square_index in range(64):
            piece = pos_info.squares[square_index]
            piece_type_val = piece_type(piece)
            colour_index = 0 if is_white(piece) else 1
            self.square[square_index] = piece
            
            if piece != NONE:
                self.piece_bitboards[piece] = set_square(self.piece_bitboards[piece], square_index)
                self.colour_bitboards[colour_index] = set_square(self.colour_bitboards[colour_index], square_index)
                
                if piece_type_val == KING:
                    self.king_square[colour_index] = square_index
                    self.all_piece_lists[piece].add_piece_at_square(square_index)
                else:
                    self.all_piece_lists[piece].add_piece_at_square(square_index)
                    
                if piece_type_val not in (PAWN, KING):
                    self.total_piece_count_without_pawns_and_kings += 1
                    
        # Cài đặt trạng thái bàn cờ
        self.is_white_to_move = pos_info.white_to_move
        self.all_pieces_bitboard = self.colour_bitboards[self.WHITE_INDEX] | self.colour_bitboards[self.BLACK_INDEX]
        self.update_slider_bitboards()
        
        # Cài đặt quyền nhập thành
        white_castle = (1 if getattr(pos_info, 'white_castle_kingside', False) else 0) | (2 if getattr(pos_info, 'white_castle_queenside', False) else 0)
        black_castle = (4 if getattr(pos_info, 'black_castle_kingside', False) else 0) | (8 if getattr(pos_info, 'black_castle_queenside', False) else 0)
        castling_rights = white_castle | black_castle
        
        # Cài đặt số nước đi
        self.ply_count = (getattr(pos_info, 'move_count', 1) - 1) * 2 + (0 if self.is_white_to_move else 1)
        
        # Tạo khóa Zobrist và trạng thái bàn cờ
        zobrist_key = Zobrist.calculate_zobrist_key(self)
        self.current_game_state = GameState(NONE, getattr(pos_info, 'ep_file', 0), castling_rights, getattr(pos_info, 'fifty_move_ply_count', 0), zobrist_key)
        
        # Cập nhật lịch sử
        self.repetition_position_history.append(zobrist_key)
        self.game_state_history.append(self.current_game_state)

    def __str__(self):
        """Tạo chuỗi biểu diễn bàn cờ"""
        from src.core.helper.board_helper import create_diagram
        return create_diagram(self, self.is_white_to_move)

    @staticmethod
    def create_board(fen=None):
        """Tạo bàn cờ mới từ FEN hoặc vị trí bắt đầu"""
        board = Board()
        if fen:
            board.load_position(fen)
        else:
            board.load_start_position()
        return board

    @staticmethod
    def create_board_from_source(source):
        """Tạo bàn cờ từ nguồn có sẵn"""
        board = Board()
        board.load_position_info(source.start_position_info)
        for move in source.all_game_moves:
            board.make_move(move)
        return board

    def move_piece(self, piece, start_square, target_square):
        """Di chuyển một quân cờ từ ô này sang ô khác"""
        # Cập nhật bitboards
        self.piece_bitboards[piece] = toggle_squares(self.piece_bitboards[piece], start_square, target_square)
        self.colour_bitboards[self.move_colour_index] = toggle_squares(self.colour_bitboards[self.move_colour_index], start_square, target_square)
        
        # Cập nhật danh sách quân
        piece_list = self.all_piece_lists[piece]
        if piece_list is not None:
            if piece_list.map[start_square] is not None:
                piece_list.move_piece(start_square, target_square)
            else:
                piece_list.add_piece_at_square(target_square)
        
        # Cập nhật mảng bàn cờ
        self.square[start_square] = NONE
        self.square[target_square] = piece

    def update_slider_bitboards(self):
        """Cập nhật bitboards cho quân trượt (xe, tượng, hậu)"""
        # Quân trượt của phe đang đi
        friendly_rook = make_piece(ROOK, self.move_colour)
        friendly_queen = make_piece(QUEEN, self.move_colour)
        friendly_bishop = make_piece(BISHOP, self.move_colour)
        self.friendly_orthogonal_sliders = self.piece_bitboards[friendly_rook] | self.piece_bitboards[friendly_queen]
        self.friendly_diagonal_sliders = self.piece_bitboards[friendly_bishop] | self.piece_bitboards[friendly_queen]
        
        # Quân trượt của phe đối phương
        enemy_rook = make_piece(ROOK, self.opponent_colour)
        enemy_queen = make_piece(QUEEN, self.opponent_colour)
        enemy_bishop = make_piece(BISHOP, self.opponent_colour)
        self.enemy_orthogonal_sliders = self.piece_bitboards[enemy_rook] | self.piece_bitboards[enemy_queen]
        self.enemy_diagonal_sliders = self.piece_bitboards[enemy_bishop] | self.piece_bitboards[enemy_queen]

    def initialize(self):
        """Khởi tạo bàn cờ về trạng thái ban đầu"""
        # Khởi tạo các cấu trúc dữ liệu
        self.all_game_moves = []
        self.king_square = [None, None]
        self.square = [NONE] * 64
        self.repetition_position_history = deque(maxlen=64)
        self.game_state_history = deque(maxlen=64)
        self.current_game_state = GameState(0, 0, 0, 0, 0)
        self.ply_count = 0
        
        # Khởi tạo danh sách quân
        self.knights = [PieceList(10), PieceList(10)]
        self.pawns = [PieceList(8), PieceList(8)]
        self.rooks = [PieceList(10), PieceList(10)]
        self.bishops = [PieceList(10), PieceList(10)]
        self.queens = [PieceList(9), PieceList(9)]
        self._init_piece_lists()
        
        # Khởi tạo các biến đếm và bitboards
        self.total_piece_count_without_pawns_and_kings = 0
        self.piece_bitboards = [0] * (MAX_PIECE_INDEX + 1)
        self.colour_bitboards = [0, 0]
        self.all_pieces_bitboard = 0

if __name__ == "__main__":
    board = Board()
    board.load_start_position()  # Fix: đã thêm dấu ()
    print(board)

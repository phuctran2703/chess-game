import tkinter as tk
from tkinter import messagebox
from src.core.Board.board import Board
from src.core.Board.piece import get_symbol, NONE, is_white, piece_type
from src.move_generator import MoveGenerator

class ChessGUI:
    def __init__(self, master, board: Board = None):
        self.master = master
        self.master.title("Chess Board")
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        margin = 80
        max_board_size = min(screen_width, screen_height) - margin
        self.square_size = max_board_size // 8
        self.font_size = max(16, int(self.square_size * 0.6))
        self.board = board if board else Board()
        self.board.load_start_position()
        self.move_generator = MoveGenerator(self.board)
        self.selected_square = None
        self.highlighted = []
        self.original_text = {}
        self.squares = [[None for _ in range(8)] for _ in range(8)]

        # Main frame with left (board) and right (info)
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.right_frame = tk.Frame(self.main_frame, padx=20, pady=20)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas for board
        self.canvas = tk.Canvas(self.left_frame, width=self.square_size*8, height=self.square_size*8)
        self.canvas.pack()
        self.draw_board()
        self.master.geometry(f"{self.square_size*8+220}x{self.square_size*8+20}")
        self.master.bind('<Configure>', self.on_resize)

        # Info label
        self.info_label = tk.Label(self.right_frame, text="", font=("Arial", 18), anchor="nw", justify="left")
        self.info_label.pack(anchor="nw")
        self.update_info()

    def update_info(self):
        turn = "Trắng" if self.board.is_white_to_move else "Đen"
        # Hiển thị trạng thái ván cờ, số nước đi, quân bị bắt, v.v.
        info = f"Lượt đi: {turn}\n"
        info += f"Số nước đã đi: {self.board.ply_count}\n"
        # Đếm số quân bị bắt
        from src.core.Board.piece import PAWN, KNIGHT, BISHOP, ROOK, QUEEN, is_white
        piece_names = ["Tốt", "Mã", "Tượng", "Xe", "Hậu"]
        white_start = [8, 2, 2, 2, 1]
        black_start = [8, 2, 2, 2, 1]
        white_count = [0]*5
        black_count = [0]*5
        for sq in self.board.square:
            if sq == NONE:
                continue
            t = piece_type(sq)
            idx = {PAWN:0, KNIGHT:1, BISHOP:2, ROOK:3, QUEEN:4}.get(t, None)
            if idx is not None:
                if is_white(sq):
                    white_count[idx] += 1
                else:
                    black_count[idx] += 1
        info += "Quân trắng bị bắt: " + ", ".join(f"{piece_names[i]}: {white_start[i] - white_count[i]}" for i in range(5)) + "\n"
        info += "Quân đen bị bắt: " + ", ".join(f"{piece_names[i]}: {black_start[i] - black_count[i]}" for i in range(5)) + "\n"
        self.info_label.config(text=info)

    def on_resize(self, event):
        if event.widget == self.master:
            new_size = min(event.width-200, event.height)
            new_square_size = max(16, (new_size - 20) // 8)
            if new_square_size != self.square_size:
                self.square_size = new_square_size
                self.font_size = max(16, int(self.square_size * 0.6))
                self.canvas.config(width=self.square_size*8, height=self.square_size*8)
                self.draw_board()
                self.update_board()

    def draw_board(self):
        colors = ["#f0d9b5", "#b58863"]
        self.canvas.delete("all")
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        # Vẽ số 1-8 bên trái, chữ a-h bên dưới
        for r in range(8):
            y = r * self.square_size + self.square_size // 2
            self.canvas.create_text(10, y, text=str(8 - r), font=("Arial", int(self.font_size * 0.7)), anchor="w")
        for c in range(8):
            x = c * self.square_size + self.square_size // 2
            self.canvas.create_text(x, self.square_size * 8 + 10, text=chr(ord('a') + c), font=("Arial", int(self.font_size * 0.7)), anchor="n")
        for r in range(8):
            for c in range(8):
                x1 = c * self.square_size
                y1 = r * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = colors[(r + c) % 2]
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                square_index = (7 - r) * 8 + c
                piece = self.board.square[square_index]
                symbol = get_symbol(piece) if piece != NONE else ''
                text = self.canvas.create_text(
                    (x1 + x2) // 2, (y1 + y2) // 2,
                    text=symbol,
                    font=("Arial", self.font_size)
                )
                self.squares[r][c] = (rect, text)
                self.canvas.tag_bind(rect, "<Button-1>", lambda e, row=r, col=c: self.on_square_click(row, col))
                self.canvas.tag_bind(text, "<Button-1>", lambda e, row=r, col=c: self.on_square_click(row, col))

    def on_square_click(self, row, col):
        square_index = (7 - row) * 8 + col
        piece = self.board.square[square_index]
        from src.core.Board.move import Move
        from src.core.Board.piece import PAWN, KING, is_white, piece_type
        
        if self.selected_square is None:
            # Chọn quân cờ cùng màu với lượt đi hiện tại
            if piece != NONE and ((self.board.is_white_to_move and is_white(piece)) or (not self.board.is_white_to_move and not is_white(piece))):
                self.selected_square = square_index
                legal_targets = self.get_legal_moves_for_square(square_index)
                self.highlight_legal_moves(legal_targets)
        else:
            legal_targets = self.get_legal_moves_for_square(self.selected_square)
            if square_index in legal_targets:
                start_square = self.selected_square
                target_square = square_index
                moved_piece = self.board.square[start_square]
                moved_piece_type = piece_type(moved_piece)
                
                # Lấy nước đi cụ thể từ move generator
                move = self.move_generator.get_move_for_square_target(start_square, target_square)
                
                if move:
                    # Nếu là tốt đến hàng cuối, hiện dialog chọn quân phong cấp
                    if moved_piece_type == PAWN:
                        row_to = target_square // 8
                        promotion_row = 7 if is_white(moved_piece) else 0
                        if row_to == promotion_row:
                            def on_select_promotion(promo_flag):
                                promo_move = Move(start_square, target_square, promo_flag)
                                self.board.make_move(promo_move)
                                self.selected_square = None
                                self.clear_highlight()
                                self.update_board()
                                self.update_info()
                                promo_win.destroy()
                            
                            promo_win = tk.Toplevel(self.master)
                            promo_win.title("Chọn quân phong tốt")
                            promo_win.geometry("250x80")
                            promo_win.grab_set()
                            tk.Label(promo_win, text="Chọn quân muốn phong:", font=("Arial", 14)).pack(pady=5)
                            btn_frame = tk.Frame(promo_win)
                            btn_frame.pack()
                            for name, flag in [
                                ("Hậu", Move.PROMOTE_TO_QUEEN_FLAG),
                                ("Xe", Move.PROMOTE_TO_ROOK_FLAG),
                                ("Mã", Move.PROMOTE_TO_KNIGHT_FLAG),
                                ("Tượng", Move.PROMOTE_TO_BISHOP_FLAG)
                            ]:
                                tk.Button(btn_frame, text=name, width=6, font=("Arial", 12), command=lambda f=flag: on_select_promotion(f)).pack(side=tk.LEFT, padx=5)
                            return
                    
                    # Thực hiện nước đi
                    self.board.make_move(move)
                    self.selected_square = None
                    self.clear_highlight()
                    self.update_board()
                    self.update_info()
            else:
                # Chọn quân cờ khác nếu click vào quân cùng màu
                if piece != NONE and ((self.board.is_white_to_move and is_white(piece)) or (not self.board.is_white_to_move and not is_white(piece))):
                    self.selected_square = square_index
                    self.clear_highlight()
                    legal_targets = self.get_legal_moves_for_square(square_index)
                    self.highlight_legal_moves(legal_targets)
                else:
                    self.selected_square = None
                    self.clear_highlight()

    def get_legal_moves_for_square(self, square_index):
        return self.move_generator.get_legal_moves_for_square(square_index)

    def highlight_legal_moves(self, legal_targets):
        for target in legal_targets:
            r = 7 - (target // 8)
            c = target % 8
            rect, text_id = self.squares[r][c]
            self.original_text[(r, c)] = self.canvas.itemcget(text_id, "text")
            target_piece = self.board.square[target]
            if target_piece != NONE and is_white(target_piece) != self.board.is_white_to_move:
                self.canvas.itemconfig(rect, fill="#ff4d4d")
            else:
                self.canvas.itemconfig(text_id, text="•")
            self.highlighted.append((r, c))

    def clear_highlight(self):
        colors = ["#f0d9b5", "#b58863"]
        for row, col in self.highlighted:
            rect, text_id = self.squares[row][col]
            color = colors[(row + col) % 2]
            self.canvas.itemconfig(rect, fill=color)
            if (row, col) in self.original_text:
                self.canvas.itemconfig(text_id, text=self.original_text[(row, col)])
        self.highlighted.clear()
        self.original_text.clear()

    def update_board(self):
        for r in range(8):
            for c in range(8):
                square_index = (7 - r) * 8 + c
                piece = self.board.square[square_index]
                symbol = get_symbol(piece) if piece != NONE else ''
                rect, text_id = self.squares[r][c]
                self.canvas.itemconfig(text_id, text=symbol)
        
        # Kiểm tra xem vua đã bị ăn chưa
        self.check_for_king_capture()

    def check_for_king_capture(self):
        """Kiểm tra nếu vua bị ăn và hiện thông báo người chơi thắng"""
        white_king_captured, black_king_captured = self.board.is_king_captured()
        
        if white_king_captured or black_king_captured:
            winner = "Đen" if white_king_captured else "Trắng"
            self.show_winner(winner)
    
    def show_winner(self, winner):
        """Hiển thị thông báo người thắng và dừng trò chơi"""
        messagebox.showinfo("Trò chơi kết thúc", f"Người chơi {winner} đã thắng!\nVua đã bị bắt.")
        
        # Tạo label thông báo người thắng trên bàn cờ
        winner_frame = tk.Frame(self.canvas, bg="white", bd=2, relief=tk.RAISED)
        winner_canvas = self.canvas.create_window(self.square_size*4, self.square_size*4, 
                                                window=winner_frame, width=self.square_size*6, height=self.square_size*2)
        
        winner_label = tk.Label(winner_frame, text=f"NGƯỜI CHƠI {winner.upper()} ĐÃ THẮNG!", 
                                font=("Arial", self.font_size), bg="white", fg="red")
        winner_label.pack(pady=20)
        
        # Tạo nút chơi lại
        replay_button = tk.Button(winner_frame, text="Chơi lại", font=("Arial", int(self.font_size*0.7)),
                                 command=self.restart_game)
        replay_button.pack(pady=10)
        
        # Vô hiệu hóa các thao tác trên bàn cờ
        self.disable_board()
    
    def disable_board(self):
        """Vô hiệu hóa các thao tác trên bàn cờ"""
        # Gỡ bỏ các sự kiện click trên bàn cờ
        for r in range(8):
            for c in range(8):
                rect, text_id = self.squares[r][c]
                self.canvas.tag_unbind(rect, "<Button-1>")
                self.canvas.tag_unbind(text_id, "<Button-1>")
        
        # Hủy bỏ ô đang chọn và các ô được đánh dấu
        self.selected_square = None
        self.clear_highlight()
    
    def restart_game(self):
        """Khởi động lại trò chơi"""
        # Tạo bàn cờ mới
        self.board = Board()
        self.board.load_start_position()
        self.move_generator = MoveGenerator(self.board)
        
        # Khôi phục lại giao diện
        self.selected_square = None
        self.highlighted = []
        self.original_text = {}
        self.draw_board()
        self.update_info()

    def _highlight_square(self, row, col, color="#4df542"):
        rect, _ = self.squares[row][col]
        self.canvas.itemconfig(rect, fill=color)

if __name__ == "__main__":
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

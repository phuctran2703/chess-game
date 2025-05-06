import tkinter as tk
from tkinter import messagebox
from src.core.Board.board import Board
from src.core.Board.piece import NONE, piece_type
from src.core.Board.move_generator import MoveGenerator
from src.ui.piece_images import PieceImageManager


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

        self.piece_manager = PieceImageManager(size=int(self.square_size * 0.85))
        # Keep track of image references to prevent garbage collection
        self.piece_images = {}

        # Add padding for row and column indices
        self.board_padding = 80  # Increased from 60 to 80 to have more space
        # Distance between chess square and index
        self.label_margin = 30  # Increased from 20 to 30

        # Main frame with left (board) and right (info)
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=False, padx=15
        )  # Increased from 10 to 15
        self.right_frame = tk.Frame(self.main_frame, padx=30, pady=20)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas for board
        self.canvas = tk.Canvas(
            self.left_frame,
            width=self.square_size * 8 + self.board_padding * 2,
            height=self.square_size * 8 + self.board_padding * 2,
        )
        self.canvas.pack(padx=15, pady=15)
        self.draw_board()
        # Increase window size to accommodate larger padding
        self.master.geometry(
            f"{self.square_size*8 + self.board_padding*2 + 250}x{self.square_size*8 + self.board_padding*2 + 40}"
        )
        self.master.bind("<Configure>", self.on_resize)

        self.info_label = tk.Label(
            self.right_frame, text="", font=("Arial", 18), anchor="nw", justify="left"
        )
        self.info_label.pack(anchor="nw")

        # Control buttons
        control_frame = tk.Frame(self.right_frame)
        control_frame.pack(anchor="nw", fill=tk.X, pady=10)

        self.reset_button = tk.Button(
            control_frame,
            text="Reset",
            command=self.restart_game,
            font=("Arial", 11),
            bg="#f44336",
            fg="white",
            width=12,
        )
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.exit_button = tk.Button(
            control_frame,
            text="Exit",
            command=self.exit_to_main_menu,
            font=("Arial", 11),
            bg="#607D8B",
            fg="white",
            width=12,
        )
        self.exit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.update_info()

    def update_info(self):
        turn = "White" if self.board.is_white_to_move else "Black"
        # Display board state, move count, captured pieces, etc.
        info = f"Turn: {turn}\n"
        info += f"Moves played: {self.board.ply_count}\n"
        # Count captured pieces
        from src.core.Board.piece import PAWN, KNIGHT, BISHOP, ROOK, QUEEN, is_white

        piece_names = ["Pawn", "Knight", "Bishop", "Rook", "Queen"]
        white_start = [8, 2, 2, 2, 1]
        black_start = [8, 2, 2, 2, 1]
        white_count = [0] * 5
        black_count = [0] * 5
        for sq in self.board.square:
            if sq == NONE:
                continue
            t = piece_type(sq)
            idx = {PAWN: 0, KNIGHT: 1, BISHOP: 2, ROOK: 3, QUEEN: 4}.get(t, None)
            if idx is not None:
                if is_white(sq):
                    white_count[idx] += 1
                else:
                    black_count[idx] += 1
        info += (
            "White pieces captured: "
            + ", ".join(
                f"{piece_names[i]}: {white_start[i] - white_count[i]}" for i in range(5)
            )
            + "\n"
        )
        info += (
            "Black pieces captured: "
            + ", ".join(
                f"{piece_names[i]}: {black_start[i] - black_count[i]}" for i in range(5)
            )
            + "\n"
        )
        self.info_label.config(text=info)

    def on_resize(self, event):
        if event.widget == self.master:
            # Calculate board_padding first
            current_board_padding = max(50, int(self.square_size * 0.5))

            # Calculate available size after subtracting spaces and information section
            available_width = event.width - 20  # Subtract space for information section
            available_height = event.height - 40  # Subtract top and bottom space

            # Subtract padding for letters and numbers (both sides)
            available_board_size = min(
                available_width - current_board_padding * 3,
                available_height - current_board_padding * 3,
            )

            # Calculate new size for each chess square
            new_square_size = max(16, available_board_size // 8)

            if new_square_size != self.square_size:
                self.square_size = new_square_size
                self.font_size = max(16, int(self.square_size * 0.6))

                # Adjust padding when changing size
                self.board_padding = max(50, int(self.square_size * 0.5))
                self.label_margin = max(40, int(self.square_size * 0.5))

                # Resize piece images
                self.piece_manager.resize(int(self.square_size * 0.85))

                self.canvas.config(
                    width=self.square_size * 8 + self.board_padding * 2,
                    height=self.square_size * 8 + self.board_padding * 2,
                )

                # Redraw the chess board
                self.draw_board()
                self.update_board()

    def draw_board(self):
        # Light cream and darker brown colors for the chess board
        colors = ["#f0d9b5", "#b58863"]  # Traditional wood-like colors
        # Color for row and column indices
        label_color = "#333333"
        self.canvas.delete("all")
        self.squares = [[None for _ in range(8)] for _ in range(8)]

        # Draw background for the index area
        self.canvas.create_rectangle(
            0,
            0,
            self.square_size * 8 + self.board_padding * 2,
            self.square_size * 8 + self.board_padding * 2,
            fill="#d9d9d9",
            outline="",
        )

        # Draw numbers 1-8 on the left and right
        for r in range(8):
            y = r * self.square_size + self.square_size // 2 + self.board_padding
            # Numbers on the left
            self.canvas.create_text(
                self.board_padding // 2,
                y,
                text=str(8 - r),
                font=("Arial", int(self.font_size * 0.7), "bold"),
                fill=label_color,
                anchor="center",
            )
            # Numbers on the right
            # self.canvas.create_text(self.board_padding + self.square_size*8 + self.board_padding//2, y,
            #                        text=str(8 - r),
            #                        font=("Arial", int(self.font_size * 0.7), "bold"),
            #                        fill=label_color, anchor="center")

        # Draw letters a-h on top and bottom
        for c in range(8):
            x = c * self.square_size + self.square_size // 2 + self.board_padding
            # Letters on top
            # self.canvas.create_text(x, self.board_padding // 2,
            #                        text=chr(ord('a') + c),
            #                        font=("Arial", int(self.font_size * 0.7), "bold"),
            #                        fill=label_color, anchor="center")
            # Letters on bottom
            self.canvas.create_text(
                x,
                self.board_padding + self.square_size * 8 + self.board_padding // 2,
                text=chr(ord("a") + c),
                font=("Arial", int(self.font_size * 0.7), "bold"),
                fill=label_color,
                anchor="center",
            )

        # Add board border with margin
        board_border = self.canvas.create_rectangle(
            self.board_padding - 2,
            self.board_padding - 2,
            self.board_padding + self.square_size * 8 + 2,
            self.board_padding + self.square_size * 8 + 2,
            width=2,
            outline="#555555",
        )

        # Draw chess squares and pieces
        for r in range(8):
            for c in range(8):
                x1 = c * self.square_size + self.board_padding
                y1 = r * self.square_size + self.board_padding
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = colors[(r + c) % 2]
                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=""
                )
                square_index = (7 - r) * 8 + c
                piece = self.board.square[square_index]

                # Get piece image if available
                piece_img = self.piece_manager.get_image(piece)

                # Create piece representation
                if piece != NONE:
                    if piece_img:
                        # Use image
                        self.piece_images[(r, c)] = (
                            piece_img  # Store reference to prevent garbage collection
                        )
                        piece_obj = self.canvas.create_image(
                            (x1 + x2) // 2,
                            (y1 + y2) // 2,
                            image=piece_img,
                            tags=(f"piece_{square_index}", "piece"),
                        )
                    else:
                        # Fallback to text
                        symbol, color, font = self.piece_manager.get_fallback_text(
                            piece
                        )
                        piece_obj = self.canvas.create_text(
                            (x1 + x2) // 2,
                            (y1 + y2) // 2,
                            text=symbol,
                            fill=color,
                            font=font,
                            tags=(f"piece_{square_index}", "piece"),
                        )
                else:
                    piece_obj = None

                # Store square and piece information
                self.squares[r][c] = {
                    "rect": rect,
                    "piece": piece_obj,
                    "square_index": square_index,
                }

                # Add click binding
                self.canvas.tag_bind(
                    rect,
                    "<Button-1>",
                    lambda e, si=square_index: self.on_square_click(si),
                )
                if piece_obj:
                    self.canvas.tag_bind(
                        piece_obj,
                        "<Button-1>",
                        lambda e, si=square_index: self.on_square_click(si),
                    )

    def on_square_click(self, square_index):
        piece = self.board.square[square_index]
        from src.core.Board.move import Move
        from src.core.Board.piece import PAWN, KING, is_white, piece_type

        if self.selected_square is None:
            # Select a piece of the same color as the current turn
            if piece != NONE and (
                (self.board.is_white_to_move and is_white(piece))
                or (not self.board.is_white_to_move and not is_white(piece))
            ):
                self.selected_square = square_index
                legal_moves = self.get_legal_moves_for_square(square_index)
                self.highlight_legal_moves([move.target_square for move in legal_moves])
        else:
            legal_moves = self.get_legal_moves_for_square(self.selected_square)
            target_squares = [move.target_square for move in legal_moves]

            if square_index in target_squares:
                start_square = self.selected_square
                target_square = square_index
                moved_piece = self.board.square[start_square]
                moved_piece_type = piece_type(moved_piece)

                # Find the specific move from the list of legal moves
                move = next(
                    (m for m in legal_moves if m.target_square == target_square), None
                )

                if move:
                    # If a pawn reaches the last rank, show promotion dialog
                    if moved_piece_type == PAWN:
                        row_to = target_square // 8
                        promotion_row = 7 if is_white(moved_piece) else 0
                        if row_to == promotion_row:

                            def on_select_promotion(promo_flag):
                                promo_move = Move(
                                    start_square, target_square, promo_flag
                                )
                                self.board.make_move(promo_move)
                                self.selected_square = None
                                self.clear_highlight()
                                self.update_board()
                                self.update_info()
                                promo_win.destroy()

                            promo_win = tk.Toplevel(self.master)
                            promo_win.title("Choose Promotion Piece")
                            promo_win.geometry("250x80")
                            promo_win.grab_set()
                            tk.Label(
                                promo_win,
                                text="Choose piece for promotion:",
                                font=("Arial", 14),
                            ).pack(pady=5)
                            btn_frame = tk.Frame(promo_win)
                            btn_frame.pack()
                            for name, flag in [
                                ("Queen", Move.PROMOTE_TO_QUEEN_FLAG),
                                ("Rook", Move.PROMOTE_TO_ROOK_FLAG),
                                ("Knight", Move.PROMOTE_TO_KNIGHT_FLAG),
                                ("Bishop", Move.PROMOTE_TO_BISHOP_FLAG),
                            ]:
                                tk.Button(
                                    btn_frame,
                                    text=name,
                                    width=6,
                                    font=("Arial", 12),
                                    command=lambda f=flag: on_select_promotion(f),
                                ).pack(side=tk.LEFT, padx=5)
                            return

                    # Execute the move
                    self.board.make_move(move)
                    self.selected_square = None
                    self.clear_highlight()
                    self.update_board()
                    self.update_info()
            else:
                # Select different piece if clicking on a piece of the same color
                if piece != NONE and (
                    (self.board.is_white_to_move and is_white(piece))
                    or (not self.board.is_white_to_move and not is_white(piece))
                ):
                    self.selected_square = square_index
                    self.clear_highlight()
                    legal_moves = self.get_legal_moves_for_square(square_index)
                    self.highlight_legal_moves(
                        [move.target_square for move in legal_moves]
                    )
                else:
                    self.selected_square = None
                    self.clear_selection_highlights()

    def get_legal_moves_for_square(self, square_index):
        return self.move_generator.get_legal_moves_for_square(square_index)

    def highlight_moves(self, moves):
        # Clear current highlights
        for square in self.highlighted:
            row, col = 7 - (square // 8), square % 8
            rect = self.squares[row][col]["rect"]
            color = ["#f0d9b5", "#b58863"][(row + col) % 2]
            self.canvas.itemconfig(rect, fill=color)

        # Highlight legal moves
        self.highlighted = []
        for move in moves:
            target_square = move.target_square
            row, col = 7 - (target_square // 8), target_square % 8
            rect = self.squares[row][col]["rect"]

            # Check if the move is a capture
            target_piece = self.board.square[target_square]
            if target_piece != NONE:
                # Capture move: highlight in red
                self.canvas.itemconfig(rect, fill="#f44336")
            else:
                # Regular move: highlight in blue
                self.canvas.itemconfig(rect, fill="#4fc3f7")

            self.highlighted.append(target_square)

    def highlight_selected(self, square):
        """Highlight the selected square"""
        row, col = 7 - (square // 8), square % 8
        rect = self.squares[row][col]["rect"]
        self.canvas.itemconfig(rect, fill="#8bc34a")  # Xanh lá đậm
        self.highlighted.append(square)

    def clear_selection_highlights(self):
        """Clear all highlights"""
        for square in self.highlighted:
            row, col = 7 - (square // 8), square % 8
            rect = self.squares[row][col]["rect"]
            color = ["#f0d9b5", "#b58863"][(row + col) % 2]
            self.canvas.itemconfig(rect, fill=color)

        self.highlighted = []
        self.selected_square = None
        self.original_text.clear()

    def update_board(self):
        """Update the board from current state"""
        # Clear highlights
        for square in self.highlighted:
            row, col = 7 - (square // 8), square % 8
            rect = self.squares[row][col]["rect"]
            color = ["#f0d9b5", "#b58863"][(row + col) % 2]
            self.canvas.itemconfig(rect, fill=color)
        self.highlighted = []

        # Check if the king has been captured
        self.check_for_king_capture()

        # Clear previous piece references
        self.piece_images = {}

        # No need to clear outlines anymore as we're using transparent images

        # Update the chess pieces
        for r in range(8):
            for c in range(8):
                square_index = (7 - r) * 8 + c
                piece = self.board.square[square_index]
                square = self.squares[r][c]
                old_piece_obj = square.get("piece")

                # Remove old piece representation
                if old_piece_obj:
                    self.canvas.delete(old_piece_obj)

                # Add new piece if exists
                if piece != NONE:
                    piece_img = self.piece_manager.get_image(piece)
                    if piece_img:
                        # Use image
                        self.piece_images[(r, c)] = piece_img  # Store reference
                        new_piece = self.canvas.create_image(
                            (
                                c * self.square_size
                                + self.square_size // 2
                                + self.board_padding
                            ),
                            (
                                r * self.square_size
                                + self.square_size // 2
                                + self.board_padding
                            ),
                            image=piece_img,
                            tags=(f"piece_{square_index}", "piece"),
                        )
                    else:
                        # Fallback to text
                        symbol, color, font = self.piece_manager.get_fallback_text(
                            piece
                        )

                        # Create the piece text
                        new_piece = self.canvas.create_text(
                            (
                                c * self.square_size
                                + self.square_size // 2
                                + self.board_padding
                            ),
                            (
                                r * self.square_size
                                + self.square_size // 2
                                + self.board_padding
                            ),
                            text=symbol,
                            fill=color,
                            font=font,
                            tags=(f"piece_{square_index}", "piece"),
                        )

                    # Add click binding to the new piece
                    self.canvas.tag_bind(
                        new_piece,
                        "<Button-1>",
                        lambda e, si=square_index: self.on_square_click(si),
                    )

                    # Update square information
                    square["piece"] = new_piece
                else:
                    square["piece"] = None

    def check_for_king_capture(self):
        """Check if king is captured and display winner message"""
        # Don't end the game just because a king could theoretically be captured
        # This will be called after a move is made, so we need to determine if the game should end
        
        # Check for checkmate or stalemate
        move_gen = MoveGenerator(self.board)
        legal_moves = move_gen.generate_legal_moves()
        
        if not legal_moves:
            if self.board.is_in_check():
                # If no legal moves and in check, it's checkmate
                winner = "White" if not self.board.is_white_to_move else "Black"
                messagebox.showinfo("Game Over", f"{winner} wins by checkmate!")
                self.restart_game()
            else:
                # If no legal moves and not in check, it's stalemate
                messagebox.showinfo("Game Over", "Game ends in stalemate (draw)!")
                self.restart_game()
        
        # Update turn information regardless
        self.update_info()

    def show_winner(self, winner):
        """Display winner message and stop the game"""
        messagebox.showinfo(
            "Game Over", f"Player {winner} has won!\nThe king has been captured."
        )

    def disable_board(self):
        """Disable interactions on the chess board"""
        # Remove click events on the chess board
        for r in range(8):
            for c in range(8):
                square = self.squares[r][c]
                rect = square["rect"]
                piece = square.get("piece")

                self.canvas.tag_unbind(rect, "<Button-1>")
                if piece:
                    self.canvas.tag_unbind(piece, "<Button-1>")

        # Clear the selected square and marked squares
        self.selected_square = None
        self.clear_selection_highlights()

    def restart_game(self):
        """Restart the game"""
        self.board = Board()
        self.board.load_start_position()
        self.move_generator = MoveGenerator(self.board)

        # Restore the interface
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

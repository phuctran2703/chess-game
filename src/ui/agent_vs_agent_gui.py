import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from src.core.Board.board import Board
from src.core.Board.move_generator import MoveGenerator
from src.agent.player import ChessAI
from src.agent.basic_agent import BasicAI
from src.ui.human_vs_human_gui import ChessGUI

class AgentvsAgentGUI(ChessGUI):
    """
    Chess GUI that allows two agent players to play against each other
    """
    def __init__(self, master, board=None):
        # Initialize the base ChessGUI
        super().__init__(master, board)
        
        # Agent Settings
        self.white_agent = None  # Will be set when user selects agent type
        self.black_agent = None  # Will be set when user selects agent type
        self.agent_thinking = False
        self.game_running = False
        self.game_speed = 1.0  # Seconds between moves
        self.thinking_thread = None
        self.pause_requested = False
        
        # Reorganize the main frame to include agent settings
        self.main_frame.pack_forget()
        
        # Create a new main frame layout
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left frame for board
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=15)
        
        # Right frame for info and agent controls
        self.right_frame = tk.Frame(self.main_frame, padx=20, pady=20)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas for board (reuse from parent class)
        self.canvas = tk.Canvas(self.left_frame, width=self.square_size*8 + self.board_padding*2, 
                               height=self.square_size*8 + self.board_padding*2)
        self.canvas.pack(padx=15, pady=15)
        
        # Info label
        self.info_label = tk.Label(self.right_frame, text="", font=("Arial", 14), anchor="nw", justify="left")
        self.info_label.pack(anchor="nw", fill=tk.X)
        
        # Agent Controls Frame
        self.agent_control_frame = tk.LabelFrame(self.right_frame, text="Cài đặt Agent vs Agent", font=("Arial", 12, "bold"), padx=10, pady=10)
        self.agent_control_frame.pack(anchor="nw", fill=tk.X, pady=10)
        
        # White Agent Selection
        white_frame = tk.Frame(self.agent_control_frame)
        white_frame.pack(anchor="w", fill=tk.X, pady=5)
        
        tk.Label(white_frame, text="Agent Trắng:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        self.white_agent_var = tk.StringVar(value="Alpha-Beta")
        white_agent_combo = ttk.Combobox(white_frame, textvariable=self.white_agent_var, 
                                     values=["Alpha-Beta", "Cơ bản"], width=10, state="readonly")
        white_agent_combo.pack(side=tk.LEFT, padx=5)
        
        # White Agent Depth (only for Alpha-Beta)
        self.white_depth_var = tk.IntVar(value=3)
        self.white_depth_frame = tk.Frame(white_frame)
        self.white_depth_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(self.white_depth_frame, text="Độ sâu:", font=("Arial", 11)).pack(side=tk.LEFT)
        white_depth_spinner = ttk.Spinbox(self.white_depth_frame, from_=1, to=50, 
                                         textvariable=self.white_depth_var, width=5)
        white_depth_spinner.pack(side=tk.LEFT, padx=5)
        
        # Black Agent Selection
        black_frame = tk.Frame(self.agent_control_frame)
        black_frame.pack(anchor="w", fill=tk.X, pady=5)
        
        tk.Label(black_frame, text="Agent Đen:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        self.black_agent_var = tk.StringVar(value="Alpha-Beta")
        black_agent_combo = ttk.Combobox(black_frame, textvariable=self.black_agent_var, 
                                     values=["Alpha-Beta", "Cơ bản"], width=10, state="readonly")
        black_agent_combo.pack(side=tk.LEFT, padx=5)
        
        # Black Agent Depth (only for Alpha-Beta)
        self.black_depth_var = tk.IntVar(value=3)
        self.black_depth_frame = tk.Frame(black_frame)
        self.black_depth_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(self.black_depth_frame, text="Độ sâu:", font=("Arial", 11)).pack(side=tk.LEFT)
        black_depth_spinner = ttk.Spinbox(self.black_depth_frame, from_=1, to=50, 
                                         textvariable=self.black_depth_var, width=5)
        black_depth_spinner.pack(side=tk.LEFT, padx=5)
        
        # Game speed control
        speed_frame = tk.Frame(self.agent_control_frame)
        speed_frame.pack(anchor="w", fill=tk.X, pady=5)
        
        tk.Label(speed_frame, text="Tốc độ (giây/nước):", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_spinner = ttk.Spinbox(speed_frame, from_=0.1, to=5.0, increment=0.1,
                                   textvariable=self.speed_var, width=5)
        speed_spinner.pack(side=tk.LEFT, padx=5)
        
        # Button Frame
        button_frame = tk.Frame(self.agent_control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Start/Stop button
        self.start_button_var = tk.StringVar(value="Bắt đầu")
        self.start_button = tk.Button(button_frame, textvariable=self.start_button_var, 
                                    command=self.toggle_game, font=("Arial", 11),
                                    bg="#4CAF50", fg="white", width=12)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        self.reset_button = tk.Button(button_frame, text="Khởi tạo lại", command=self.reset_game,
                                    font=("Arial", 11), bg="#f44336", fg="white", width=12)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Pause/Resume button (initially disabled)
        self.pause_button_var = tk.StringVar(value="Tạm dừng")
        self.pause_button = tk.Button(button_frame, textvariable=self.pause_button_var,
                                    command=self.toggle_pause, font=("Arial", 11),
                                    bg="#2196F3", fg="white", width=12, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        # Exit button - New
        self.exit_button = tk.Button(button_frame, text="Thoát", command=self.exit_to_main_menu,
                                   font=("Arial", 11), bg="#607D8B", fg="white", width=12)
        self.exit_button.pack(side=tk.LEFT, padx=5)
        
        # Game log
        log_frame = tk.LabelFrame(self.right_frame, text="Nhật ký trận đấu", font=("Arial", 12, "bold"), padx=10, pady=10)
        log_frame.pack(anchor="nw", fill=tk.BOTH, expand=True, pady=10)
        
        self.game_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=40, height=15, font=("Consolas", 10))
        self.game_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Sẵn sàng. Chọn cài đặt Agent và nhấn 'Bắt đầu'")
        self.status_bar = tk.Label(self.right_frame, textvariable=self.status_var, 
                                 font=("Arial", 10), bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        # Connect combo box events
        white_agent_combo.bind("<<ComboboxSelected>>", self.on_white_agent_change)
        black_agent_combo.bind("<<ComboboxSelected>>", self.on_black_agent_change)
        
        # Draw the board
        self.draw_board()
        self.update_info()
        
        # Increase window size to accommodate the controls
        self.master.geometry(f"{self.square_size*8 + self.board_padding*2 + 450}x{self.square_size*8 + self.board_padding*2 + 40}")
        
        # Hook up to master's closing event to stop agent thread safely
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Add welcome message to log
        self.add_to_game_log("Chào mừng đến với chế độ Agent vs Agent!")
        self.add_to_game_log("Chọn loại Agent và độ sâu tìm kiếm cho từng bên, sau đó nhấn nút 'Bắt đầu'")
    
    def on_close(self):
        """Safely close the application by stopping any agent threads"""
        self.game_running = False
        if self.thinking_thread and self.thinking_thread.is_alive():
            self.thinking_thread.join(timeout=1.0)
        self.master.destroy()
    
    def on_white_agent_change(self, event=None):
        """Handle change in White Agent selection"""
        agent_type = self.white_agent_var.get()
        if agent_type == "Alpha-Beta":
            self.white_depth_frame.pack(side=tk.LEFT, padx=10)
        else:
            self.white_depth_frame.pack_forget()
    
    def on_black_agent_change(self, event=None):
        """Handle change in Black Agent selection"""
        agent_type = self.black_agent_var.get()
        if agent_type == "Alpha-Beta":
            self.black_depth_frame.pack(side=tk.LEFT, padx=10)
        else:
            self.black_depth_frame.pack_forget()
    
    def add_to_game_log(self, message):
        """Add a message to the game log with timestamp"""
        timestamp = time.strftime('%H:%M:%S')
        self.game_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.game_log.see(tk.END)
    
    def toggle_game(self):
        """Start or stop the Agent vs Agent game"""
        if not self.game_running:
            # Start the game
            self.start_game()
        else:
            # Stop the game
            self.stop_game()
    
    def toggle_pause(self):
        """Pause or resume the Agent vs Agent game"""
        if not self.pause_requested:
            self.pause_requested = True
            self.pause_button_var.set("Tiếp tục")
            self.status_var.set("Đã tạm dừng. Nhấn 'Tiếp tục' để tiếp tục trận đấu.")
            self.add_to_game_log("Trận đấu đã tạm dừng.")
        else:
            self.pause_requested = False
            self.pause_button_var.set("Tạm dừng")
            self.status_var.set("Trận đấu đang tiếp tục...")
            self.add_to_game_log("Trận đấu tiếp tục.")
    
    def start_game(self):
        """Initialize and start a new Agent vs Agent game"""
        # Create agent players based on settings
        self.create_agent_players()
        
        if not self.white_agent or not self.black_agent:
            messagebox.showerror("Lỗi", "Không thể khởi tạo Agent. Vui lòng kiểm tra lại cài đặt.")
            return
        
        # Reset the board if it's not a fresh game
        if self.board.ply_count > 0:
            self.reset_game(start_new=False)
        
        # Update UI
        self.game_running = True
        self.pause_requested = False
        self.start_button_var.set("Dừng lại")
        self.pause_button.config(state=tk.NORMAL)
        self.pause_button_var.set("Tạm dừng")
        
        # Start the game thread
        self.thinking_thread = threading.Thread(target=self.run_game)
        self.thinking_thread.daemon = True
        self.thinking_thread.start()
        
        self.add_to_game_log("Trận đấu Agent vs Agent đã bắt đầu!")
        self.status_var.set("Đang chạy trận đấu Agent vs Agent...")
    
    def stop_game(self):
        """Stop the current Agent vs Agent game"""
        self.game_running = False
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        self.status_var.set("Trận đấu đã dừng. Nhấn 'Bắt đầu' để khởi động trận đấu mới.")
        self.add_to_game_log("Trận đấu đã dừng lại.")
    
    def reset_game(self, start_new=True):
        """Reset the game board to the starting position"""
        # Stop any running game
        self.game_running = False
        
        # Reset the board
        self.board = Board()
        self.board.load_start_position()
        self.move_generator = MoveGenerator(self.board)
        
        # Reset UI
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        self.pause_button_var.set("Tạm dừng")
        self.selected_square = None
        self.clear_highlight()
        self.draw_board()
        self.update_board()
        self.update_info()
        
        if start_new:
            self.add_to_game_log("Trận đấu đã được khởi tạo lại.")
            self.status_var.set("Trận đấu đã được khởi tạo lại. Nhấn 'Bắt đầu' để bắt đầu trận đấu mới.")
    
    def create_agent_players(self):
        """Create agent players based on user settings"""
        # Create White Agent
        white_agent_type = self.white_agent_var.get()
        if white_agent_type == "Alpha-Beta":
            white_depth = self.white_depth_var.get()
            self.white_agent = ChessAI(depth=white_depth)
            self.add_to_game_log(f"Agent Trắng: Alpha-Beta (độ sâu {white_depth})")
        else:
            self.white_agent = BasicAI()
            self.add_to_game_log("Agent Trắng: Cơ bản (chọn nước đi ngẫu nhiên)")
        
        # Create Black Agent
        black_agent_type = self.black_agent_var.get()
        if black_agent_type == "Alpha-Beta":
            black_depth = self.black_depth_var.get()
            self.black_agent = ChessAI(depth=black_depth)
            self.add_to_game_log(f"Agent Đen: Alpha-Beta (độ sâu {black_depth})")
        else:
            self.black_agent = BasicAI()
            self.add_to_game_log("Agent Đen: Cơ bản (chọn nước đi ngẫu nhiên)")
    
    def run_game(self):
        """Run the Agent vs Agent game loop in a separate thread"""
        move_count = 0
        max_moves = 200  # Prevent infinite games
        
        try:
            while self.game_running and move_count < max_moves:
                # Check if game is paused
                while self.pause_requested and self.game_running:
                    time.sleep(0.1)
                
                if not self.game_running:
                    break
                
                # Choose the current agent
                current_agent = self.white_agent if self.board.is_white_to_move else self.black_agent
                side_name = "Trắng" if self.board.is_white_to_move else "Đen"
                
                # Update status
                status_text = f"Agent {side_name} đang suy nghĩ..."
                self.master.after(0, lambda t=status_text: self.status_var.set(t))
                
                # Get agent's move
                start_time = time.time()
                move = current_agent.choose_move(self.board)
                elapsed = time.time() - start_time
                
                # Check if game stopped while agent was thinking
                if not self.game_running:
                    break
                
                # Check for game end
                if move is None:
                    self.master.after(0, lambda s=side_name: self.game_over_no_moves(s))
                    break
                
                # Format the move for display
                move_str = self.format_move(move)
                
                # Add thinking time to log
                log_text = f"Agent {side_name} chọn nước đi {move_str} (thời gian suy nghĩ: {elapsed:.2f}s)"
                self.master.after(0, lambda t=log_text: self.add_to_game_log(t))
                
                # Make a copy of the move for highlighting (to avoid lambda issues)
                move_copy = move
                
                # Highlight the move on the board
                self.master.after(0, lambda m=move_copy: self.highlight_move(m))
                
                # Wait for the specified game speed
                delay = max(0, self.speed_var.get() - elapsed)
                if delay > 0:
                    time.sleep(delay)
                
                # Make the move on a separate thread to avoid UI freezing
                def update_move_on_ui(m):
                    self.board.make_move(m)
                    self.update_board()
                    self.update_info()
                    
                    # Check for game end (on UI thread)
                    game_ended = self.check_for_game_end()
                    return game_ended
                
                # Execute the move on the UI thread
                move_final = move  # Create a final reference for the move
                game_ended = False
                
                # Use a custom event to wait for the UI thread to complete the operation
                done_event = threading.Event()
                
                def ui_operation():
                    nonlocal game_ended
                    game_ended = update_move_on_ui(move_final)
                    done_event.set()
                
                self.master.after(0, ui_operation)
                done_event.wait()  # Wait for UI thread to complete
                
                # Increment move counter
                move_count += 1
                
                # Check if game ended
                if game_ended:
                    break
            
            if move_count >= max_moves and self.game_running:
                self.master.after(0, self.game_over_move_limit)
        
        except Exception as e:
            import traceback
            error_message = f"{str(e)}\n{traceback.format_exc()}"
            self.master.after(0, lambda err=error_message: self.handle_game_error(err))
    
    def handle_game_error(self, error_message):
        """Handle any errors that occur during the game"""
        self.game_running = False
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        self.status_var.set(f"Lỗi: {error_message}")
        self.add_to_game_log(f"Trận đấu gặp lỗi: {error_message}")
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi trong trận đấu: {error_message}")
    
    def highlight_move(self, move):
        """Highlight a move on the board"""
        if not move:
            return
        
        # Clear any previous highlights
        self.clear_highlight()
        
        # Highlight the from square
        from_square = move.start_square
        from_row = 7 - (from_square // 8)
        from_col = from_square % 8
        self._highlight_square(from_row, from_col, "#4286f4")  # Blue
        
        # Highlight the to square
        to_square = move.target_square
        to_row = 7 - (to_square // 8)
        to_col = to_square % 8
        self._highlight_square(to_row, to_col, "#42f474")  # Green
        
        # Add to highlighted list to be cleared later
        self.highlighted.append((from_row, from_col))
        self.highlighted.append((to_row, to_col))
    
    def format_move(self, move):
        """Format a move object into readable text"""
        if not move:
            return "--"
        
        # Get coordinates
        from_file = chr(ord('a') + (move.start_square % 8))
        from_rank = str(1 + (move.start_square // 8))
        to_file = chr(ord('a') + (move.target_square % 8))
        to_rank = str(1 + (move.target_square // 8))
        
        # Basic move notation
        move_str = f"{from_file}{from_rank}-{to_file}{to_rank}"
        
        # Add promotion information if applicable
        from src.core.Board.move import Move
        if move.is_promotion:
            promotion_type = ""
            if move.move_flag == Move.PROMOTE_TO_QUEEN_FLAG:
                promotion_type = "=Q"
            elif move.move_flag == Move.PROMOTE_TO_ROOK_FLAG:
                promotion_type = "=R"
            elif move.move_flag == Move.PROMOTE_TO_BISHOP_FLAG:
                promotion_type = "=B"
            elif move.move_flag == Move.PROMOTE_TO_KNIGHT_FLAG:
                promotion_type = "=N"
            move_str += promotion_type
            
        return move_str
    
    def check_for_game_end(self):
        """Check if the game has ended (checkmate, stalemate, etc.)"""
        move_gen = MoveGenerator(self.board)
        legal_moves = move_gen.generate_legal_moves()
        
        # Lưu trạng thái ban đầu của game_running
        was_running = self.game_running
        
        if not legal_moves:
            if self.board.is_in_check():
                winner = "Trắng" if not self.board.is_white_to_move else "Đen"
                # Đặt game_running thành False trước khi hiển thị hộp thoại
                self.game_running = False
                # Cập nhật UI trước, sau đó mới hiển thị thông báo
                self.status_var.set(f"Chiếu hết! Agent {winner} thắng.")
                self.add_to_game_log(f"Chiếu hết! Agent {winner} thắng trận đấu.")
                # Gửi thông điệp dừng tới luồng game
                if was_running:
                    # Hiển thị thông báo và sau đó reset game
                    messagebox.showinfo("Trận đấu kết thúc", f"Chiếu hết! Agent {winner} thắng trận đấu.")
                    self.reset_game()
            else:
                # Đặt game_running thành False trước khi hiển thị hộp thoại
                self.game_running = False
                # Cập nhật UI trước, sau đó mới hiển thị thông báo
                self.status_var.set("Bế tắc! Trận đấu hòa.")
                self.add_to_game_log("Bế tắc! Trận đấu hòa.")
                # Hiển thị thông báo và sau đó reset game
                if was_running:
                    messagebox.showinfo("Trận đấu kết thúc", "Bế tắc! Trận đấu hòa.")
                    self.reset_game()
            return True
        elif self.board.fifty_move_counter >= 100:
            # Đặt game_running thành False trước khi hiển thị hộp thoại
            self.game_running = False
            # Cập nhật UI trước, sau đó mới hiển thị thông báo
            self.status_var.set("Luật 50 nước đi! Trận đấu hòa.")
            self.add_to_game_log("Luật 50 nước đi! Trận đấu hòa.")
            # Hiển thị thông báo và sau đó reset game
            if was_running:
                messagebox.showinfo("Trận đấu kết thúc", "Luật 50 nước đi! Trận đấu hòa.")
                self.reset_game()
            return True
        
        # Check for repetition
        rep_count = 0
        for zobrist in self.board.repetition_position_history:
            if zobrist == self.board.current_game_state.zobrist_key:
                rep_count += 1
        
        if rep_count >= 50: 
            # Đặt game_running thành False trước khi hiển thị hộp thoại
            self.game_running = False
            # Cập nhật UI trước, sau đó mới hiển thị thông báo
            self.status_var.set("Lặp lại vị trí 50 lần! Trận đấu hòa.")
            self.add_to_game_log("Lặp lại vị trí 50 lần! Trận đấu hòa.")
            # Hiển thị thông báo và sau đó reset game
            if was_running:
                messagebox.showinfo("Trận đấu kết thúc", "Lặp lại vị trí 50 lần! Trận đấu hòa.")
                self.reset_game()
            return True
        
        return False
    
    def game_over_no_moves(self, side):
        """Handle game over when a side has no legal moves"""
        self.game_running = False
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        
        if self.board.is_in_check():
            winner = "Trắng" if not self.board.is_white_to_move else "Đen"
            self.status_var.set(f"Chiếu hết! Agent {winner} thắng.")
            self.add_to_game_log(f"Chiếu hết! Agent {winner} thắng trận đấu.")
            messagebox.showinfo("Trận đấu kết thúc", f"Chiếu hết! Agent {winner} thắng trận đấu.")
        else:
            self.status_var.set("Bế tắc! Trận đấu hòa.")
            self.add_to_game_log("Bế tắc! Trận đấu hòa.")
            messagebox.showinfo("Trận đấu kết thúc", "Bế tắc! Trận đấu hòa.")
    
    def game_over_checkmate(self, winner):
        """Handle checkmate"""
        self.game_running = False
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        self.status_var.set(f"Chiếu hết! Agent {winner} thắng.")
        self.add_to_game_log(f"Chiếu hết! Agent {winner} thắng trận đấu.")
        messagebox.showinfo("Trận đấu kết thúc", f"Chiếu hết! Agent {winner} thắng trận đấu.")
    
    def game_over_stalemate(self):
        """Handle stalemate"""
        self.game_running = False
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        self.status_var.set("Bế tắc! Trận đấu hòa.")
        self.add_to_game_log("Bế tắc! Trận đấu hòa.")
        messagebox.showinfo("Trận đấu kết thúc", "Bế tắc! Trận đấu hòa.")
    
    def game_over_fifty_move_rule(self):
        """Handle fifty move rule"""
        self.game_running = False
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        self.status_var.set("Luật 50 nước đi! Trận đấu hòa.")
        self.add_to_game_log("Luật 50 nước đi! Trận đấu hòa.")
        messagebox.showinfo("Trận đấu kết thúc", "Luật 50 nước đi! Trận đấu hòa.")
    
    def game_over_repetition(self):
        """Handle three-fold repetition"""
        self.game_running = False
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        self.status_var.set("Lặp lại vị trí 3 lần! Trận đấu hòa.")
        self.add_to_game_log("Lặp lại vị trí 3 lần! Trận đấu hòa.")
        messagebox.showinfo("Trận đấu kết thúc", "Lặp lại vị trí 3 lần! Trận đấu hòa.")
    
    def game_over_move_limit(self):
        """Handle game over due to move limit"""
        self.game_running = False
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        self.status_var.set("Trận đấu kết thúc do đạt giới hạn số nước đi.")
        self.add_to_game_log("Trận đấu kết thúc do đạt giới hạn số nước đi.")
        messagebox.showinfo("Trận đấu kết thúc", "Trận đấu kết thúc do đạt giới hạn số nước đi.")
    
    def announce_checkmate(self, winner):
        """Hiển thị thông báo chiếu hết"""
        # Đảm bảo nút nhấn ở trạng thái phù hợp
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        # Hiển thị hộp thoại thông báo và khởi tạo lại trò chơi khi nhấn OK
        messagebox.showinfo("Trận đấu kết thúc", f"Chiếu hết! Agent {winner} thắng trận đấu.")
        # Reset the game after dialog closes
        self.reset_game()
    
    def announce_stalemate(self):
        """Hiển thị thông báo bế tắc"""
        # Đảm bảo nút nhấn ở trạng thái phù hợp
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        # Hiển thị hộp thoại thông báo và khởi tạo lại trò chơi khi nhấn OK
        messagebox.showinfo("Trận đấu kết thúc", "Bế tắc! Trận đấu hòa.")
        # Reset the game after dialog closes
        self.reset_game()
    
    def announce_fifty_move_rule(self):
        """Hiển thị thông báo luật 50 nước đi"""
        # Đảm bảo nút nhấn ở trạng thái phù hợp
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        # Hiển thị hộp thoại thông báo và khởi tạo lại trò chơi khi nhấn OK
        messagebox.showinfo("Trận đấu kết thúc", "Luật 50 nước đi! Trận đấu hòa.")
        # Reset the game after dialog closes
        self.reset_game()
    
    def announce_repetition(self):
        """Hiển thị thông báo lặp lại vị trí 3 lần"""
        # Đảm bảo nút nhấn ở trạng thái phù hợp
        self.start_button_var.set("Bắt đầu")
        self.pause_button.config(state=tk.DISABLED)
        # Hiển thị hộp thoại thông báo và khởi tạo lại trò chơi khi nhấn OK
        messagebox.showinfo("Trận đấu kết thúc", "Lặp lại vị trí 3 lần! Trận đấu hòa.")
        # Reset the game after dialog closes
        self.reset_game()
    
    def exit_to_main_menu(self):
        """Exit to main menu to select a different game mode"""
        # Stop any running game
        self.game_running = False
        if self.thinking_thread and self.thinking_thread.is_alive():
            self.thinking_thread.join(timeout=0.5)
            
        # Close the current window and return to main menu
        self.master.destroy()
        
        # Import here to avoid circular imports
        from src.main import main
        # Start the main menu
        main()
        
    def _highlight_square(self, row, col, color="#4df542"):
        """Highlight a square with a specific color"""
        # Use the updated dictionary structure for squares
        square = self.squares[row][col]
        rect = square['rect']
        self.canvas.itemconfig(rect, fill=color)

def run_agent_vs_agent():
    """Run the Agent vs Agent GUI"""
    root = tk.Tk()
    root.title("Chess - Agent vs Agent")
    app = AgentvsAgentGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_agent_vs_agent()
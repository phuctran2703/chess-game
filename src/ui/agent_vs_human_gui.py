import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import datetime
from src.core.Board.move_generator import MoveGenerator
from src.agent.player import ChessAI
from src.ui.human_vs_human_gui import ChessGUI


class AIVisualizerGUI(ChessGUI):
    """
    Enhanced Chess GUI that visualizes the AI's thinking process
    """

    def __init__(self, master, board=None):
        super().__init__(master, board)

        # AI Settings
        self.ai = ChessAI(depth=3)  # Initialize AI with depth 3
        self.ai_thinking = False
        self.ai_enabled = True
        self.ai_player = 1  # 0 for white, 1 for black
        self.thinking_thread = None
        self.ai_move_queue = []
        self.ai_analysis_steps = []

        # Reorganize the main frame to include AI visualization
        self.main_frame.pack_forget()

        # Create a new main frame layout
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Left frame for board
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=15)

        # Right frame for info and AI visualization
        self.right_frame = tk.Frame(self.main_frame, padx=20, pady=20)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas for board (reuse from parent class)
        self.canvas = tk.Canvas(
            self.left_frame,
            width=self.square_size * 8 + self.board_padding * 2,
            height=self.square_size * 8 + self.board_padding * 2,
        )
        self.canvas.pack(padx=15, pady=15)

        self.info_label = tk.Label(
            self.right_frame, text="", font=("Arial", 14), anchor="nw", justify="left"
        )
        self.info_label.pack(anchor="nw", fill=tk.X)

        # AI Controls Frame
        self.ai_control_frame = tk.LabelFrame(
            self.right_frame,
            text="AI Controls",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10,
        )
        self.ai_control_frame.pack(anchor="nw", fill=tk.X, pady=10)

        # AI Player Selection
        player_frame = tk.Frame(self.ai_control_frame)
        player_frame.pack(anchor="w", fill=tk.X, pady=5)

        tk.Label(player_frame, text="AI plays as:", font=("Arial", 11)).pack(
            side=tk.LEFT, padx=5
        )
        self.ai_player_var = tk.StringVar(value="Black")
        ai_player_combo = ttk.Combobox(
            player_frame,
            textvariable=self.ai_player_var,
            values=["White", "Black"],
            width=8,
            state="readonly",
        )
        ai_player_combo.pack(side=tk.LEFT, padx=5)
        ai_player_combo.bind("<<ComboboxSelected>>", self.on_ai_player_change)

        # AI Depth Selection
        depth_frame = tk.Frame(self.ai_control_frame)
        depth_frame.pack(anchor="w", fill=tk.X, pady=5)

        tk.Label(depth_frame, text="Search depth:", font=("Arial", 11)).pack(
            side=tk.LEFT, padx=5
        )
        self.ai_depth_var = tk.IntVar(value=3)
        depth_spinner = ttk.Spinbox(
            depth_frame, from_=1, to=10, textvariable=self.ai_depth_var, width=5
        )
        depth_spinner.pack(side=tk.LEFT, padx=5)
        depth_spinner.bind("<<Increment>>", lambda e: self.on_depth_change())
        depth_spinner.bind("<<Decrement>>", lambda e: self.on_depth_change())

        # Time Limit Selection
        time_frame = tk.Frame(self.ai_control_frame)
        time_frame.pack(anchor="w", fill=tk.X, pady=5)

        tk.Label(time_frame, text="Time limit (seconds):", font=("Arial", 11)).pack(
            side=tk.LEFT, padx=5
        )
        self.ai_time_var = tk.IntVar(value=0)  # 0 means no limit
        time_spinner = ttk.Spinbox(
            time_frame, from_=0, to=60, textvariable=self.ai_time_var, width=5
        )
        time_spinner.pack(side=tk.LEFT, padx=5)
        time_spinner.bind("<<Increment>>", lambda e: self.on_time_limit_change())
        time_spinner.bind("<<Decrement>>", lambda e: self.on_time_limit_change())
        tk.Label(time_frame, text="(0 = no limit)", font=("Arial", 9)).pack(
            side=tk.LEFT, padx=5
        )

        # Enable/Disable AI button
        button_frame = tk.Frame(self.ai_control_frame)
        button_frame.pack(anchor="w", fill=tk.X, pady=5)

        self.ai_button_var = tk.StringVar(value="Disable AI")
        self.ai_button = tk.Button(
            button_frame,
            textvariable=self.ai_button_var,
            font=("Arial", 11),
            command=self.toggle_ai,
            bg="#f44336",
            fg="white",
            width=10,
        )
        self.ai_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(
            button_frame,
            text="Reset",
            font=("Arial", 11),
            command=self.restart_game,
            bg="#FF9800",
            fg="white",
            width=10,
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.exit_button = tk.Button(
            button_frame,
            text="Exit",
            font=("Arial", 11),
            command=self.exit_to_main_menu,
            bg="#607D8B",
            fg="white",
            width=10,
        )
        self.exit_button.pack(side=tk.LEFT, padx=5)

        # Thinking visualization frame
        self.thinking_frame = tk.LabelFrame(
            self.right_frame,
            text="AI Thinking Process",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10,
        )
        self.thinking_frame.pack(anchor="nw", fill=tk.BOTH, expand=True, pady=10)

        # Status indicator
        status_frame = tk.Frame(self.thinking_frame)
        status_frame.pack(anchor="w", fill=tk.X, pady=5)

        tk.Label(status_frame, text="Status:", font=("Arial", 11)).pack(
            side=tk.LEFT, padx=5
        )
        self.status_var = tk.StringVar(value="Waiting...")
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 11, "bold"),
            fg="blue",
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Progress indicator
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.thinking_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)

        # Move evaluation display
        eval_frame = tk.Frame(self.thinking_frame)
        eval_frame.pack(anchor="w", fill=tk.X, pady=5)

        tk.Label(eval_frame, text="Current evaluation:", font=("Arial", 11)).pack(
            side=tk.LEFT, padx=5
        )
        self.evaluation_var = tk.StringVar(value="0.0")
        self.evaluation_label = tk.Label(
            eval_frame, textvariable=self.evaluation_var, font=("Arial", 11, "bold")
        )
        self.evaluation_label.pack(side=tk.LEFT, padx=5)

        # Best move display
        best_move_frame = tk.Frame(self.thinking_frame)
        best_move_frame.pack(anchor="w", fill=tk.X, pady=5)

        tk.Label(best_move_frame, text="Best move:", font=("Arial", 11)).pack(
            side=tk.LEFT, padx=5
        )
        self.best_move_var = tk.StringVar(value="--")
        self.best_move_label = tk.Label(
            best_move_frame,
            textvariable=self.best_move_var,
            font=("Arial", 11, "bold"),
            fg="green",
        )
        self.best_move_label.pack(side=tk.LEFT, padx=5)

        # Thinking log
        tk.Label(
            self.thinking_frame, text="Thinking log:", font=("Arial", 11), anchor="w"
        ).pack(anchor="w", padx=5, pady=5)
        self.thinking_log = scrolledtext.ScrolledText(
            self.thinking_frame,
            wrap=tk.WORD,
            width=40,
            height=10,
            font=("Consolas", 10),
        )
        self.thinking_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Draw the board
        self.draw_board()
        self.update_info()

        # Increase window size to accommodate the visualization panels
        self.master.geometry(
            f"{self.square_size*8 + self.board_padding*2 + 450}x{self.square_size*8 + self.board_padding*2 + 40}"
        )

        # Hook up to master's closing event to stop AI thread safely
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        # Check if it's AI's turn to start
        self.check_ai_turn()

    def on_close(self):
        """Safely close the application by stopping any AI threads"""
        self.ai_enabled = False
        if self.thinking_thread and self.thinking_thread.is_alive():
            self.thinking_thread.join(timeout=1.0)
        self.master.destroy()

    def toggle_ai(self):
        """Toggle AI on/off"""
        self.ai_enabled = not self.ai_enabled
        if self.ai_enabled:
            self.ai_button_var.set("Disable AI")
            self.ai_button.config(bg="#f44336")
            self.status_var.set("AI enabled")
            self.check_ai_turn()
        else:
            self.ai_button_var.set("Enable AI")
            self.ai_button.config(bg="#4CAF50")
            self.status_var.set("AI disabled")

    def on_ai_player_change(self, event=None):
        """Handle change in AI player selection"""
        selected = self.ai_player_var.get()
        if selected == "White":
            self.ai_player = 0
        else:
            self.ai_player = 1
        self.check_ai_turn()

    def on_depth_change(self, event=None):
        """Handle change in AI search depth"""
        depth = self.ai_depth_var.get()
        self.ai.set_depth(depth)
        self.add_to_thinking_log(f"Search depth changed to {depth}")

    def on_time_limit_change(self, event=None):
        """Handle change in AI time limit"""
        time_limit = self.ai_time_var.get()
        time_limit_str = f"{time_limit} seconds" if time_limit > 0 else "no limit"
        self.add_to_thinking_log(f"Time limit changed to {time_limit_str}")

    def add_to_thinking_log(self, message):
        """Add message to thinking log with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.thinking_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.thinking_log.see(tk.END)  # Auto-scroll to the end

    def _highlight_square(self, row, col, color="#4df542"):
        """Highlight a square with a specific color"""
        # Use the updated dictionary structure for squares
        square = self.squares[row][col]
        rect = square["rect"]
        self.canvas.itemconfig(rect, fill=color)

    def on_square_click(self, square_index):
        """Handle square clicks"""
        # Disable clicks if AI is thinking
        if self.ai_thinking:
            return

        # Get row and column from square index
        row, col = divmod(square_index, 8)

        # Process the click using the parent class method
        super().on_square_click(square_index)

        # Check if it's AI's turn after human move
        self.check_ai_turn()

    def update_info(self):
        # Update the info label with current game state
        super().update_info()

    def on_close(self):
        """Safely close the application by stopping any AI threads"""
        self.ai_enabled = False
        if self.thinking_thread and self.thinking_thread.is_alive():
            self.thinking_thread.join(timeout=1.0)
        self.master.destroy()

    def toggle_ai(self):
        """Toggle AI on/off"""
        self.ai_enabled = not self.ai_enabled
        if self.ai_enabled:
            self.ai_button_var.set("Disable AI")
            self.ai_button.config(bg="#f44336")
            self.status_var.set("AI enabled")
            self.check_ai_turn()
        else:
            self.ai_button_var.set("Enable AI")
            self.ai_button.config(bg="#4CAF50")
            self.status_var.set("AI disabled")

    def on_ai_player_change(self, event=None):
        """Handle change in AI player selection"""
        selected = self.ai_player_var.get()
        if selected == "White":
            self.ai_player = 0
        else:
            self.ai_player = 1
        self.check_ai_turn()

    def on_depth_change(self, event=None):
        """Handle change in AI search depth"""
        depth = self.ai_depth_var.get()
        self.ai.set_depth(depth)
        self.add_to_thinking_log(f"Search depth changed to {depth}")

    def on_time_limit_change(self, event=None):
        """Handle change in AI time limit"""
        time_limit = self.ai_time_var.get()
        time_limit_str = f"{time_limit} seconds" if time_limit > 0 else "no limit"
        self.add_to_thinking_log(f"Time limit changed to {time_limit_str}")

    def add_to_thinking_log(self, message):
        """Add a message to the thinking log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        self.thinking_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.thinking_log.see(tk.END)

    def on_square_click(self, square_index):
        """Handle square clicks"""
        row, col = 7 - (square_index // 8), square_index % 8
        # If AI is thinking, ignore clicks
        if self.ai_thinking:
            return

        # Check if it's human's turn
        current_side = 0 if self.board.is_white_to_move else 1
        if current_side == self.ai_player and self.ai_enabled:
            self.add_to_thinking_log("Not your turn!")
            return

        # Process the move normally
        super().on_square_click(row, col)

        # After human's move, check if it's AI's turn
        self.check_ai_turn()

    def check_ai_turn(self):
        """Check if it's AI's turn to move and start thinking if so"""
        current_side = 0 if self.board.is_white_to_move else 1
        if current_side == self.ai_player and self.ai_enabled and not self.ai_thinking:
            self.start_ai_thinking()

    def start_ai_thinking(self):
        """Start the AI thinking process in a separate thread"""
        self.ai_thinking = True
        self.status_var.set("AI is thinking...")
        self.progress_var.set(0)
        self.evaluation_var.set("...")
        self.best_move_var.set("...")
        self.add_to_thinking_log("AI starts thinking...")

        # Create and start the thinking thread
        self.thinking_thread = threading.Thread(target=self.ai_think_and_move)
        self.thinking_thread.daemon = True
        self.thinking_thread.start()

    def ai_think_and_move(self):
        """AI thinking thread function that updates the visualization"""
        # Create a custom AI agent with visualization callbacks
        time_limit = self.ai_time_var.get()
        time_limit = None if time_limit == 0 else time_limit

        custom_ai = VisualizationAlphaBetaAgent(
            max_depth=self.ai_depth_var.get(),
            time_limit=time_limit,
            update_callback=self.update_thinking_visualization,
        )

        start_time = time.time()

        # Get AI's move
        move = custom_ai.choose_move(self.board)

        # Ensure we display for at least a short time
        elapsed = time.time() - start_time
        if elapsed < 0.5:
            time.sleep(0.5 - elapsed)

        # Update visualization one last time
        self.master.after(0, lambda: self.update_final_visualization(custom_ai, move))

        # Schedule the AI move to be made on the main thread
        self.master.after(500, lambda: self.make_ai_move(move))

    def update_thinking_visualization(
        self, depth, current_depth, move, score, nodes, elapsed
    ):
        """Update the visualization with current thinking information"""
        # Calculate progress
        progress = (current_depth / depth) * 100

        # Schedule GUI updates on the main thread
        self.master.after(
            0,
            lambda: self._update_visualization_gui(
                progress, move, score, nodes, elapsed
            ),
        )

    def _update_visualization_gui(self, progress, move, score, nodes, elapsed):
        """Update GUI elements with thinking data (called on main thread)"""
        self.progress_var.set(progress)

        # Format evaluation score
        if score is not None:
            score_str = (
                f"{score/100:.2f}"
                if abs(score) < 10000
                else ("Mate" if score > 0 else "-Mate")
            )
            self.evaluation_var.set(score_str)

        # Format best move
        if move is not None:
            # Highlight the move on the board temporarily
            self.highlight_considered_move(move)
            move_str = self.format_move(move)
            self.best_move_var.set(move_str)

        # Update log with detailed information
        if move is not None:
            self.add_to_thinking_log(
                f"Depth: {int(progress/100*self.ai_depth_var.get())} | "
                f"Move: {self.format_move(move)} | "
                f"Score: {self.evaluation_var.get()} | "
                f"Nodes: {nodes} | "
                f"Time: {elapsed:.1f}s"
            )

    def update_final_visualization(self, ai_agent, final_move):
        """Update visualization with final decision"""
        self.progress_var.set(100)
        if final_move:
            final_move_str = self.format_move(final_move)
            self.best_move_var.set(final_move_str)
            self.status_var.set("Move selected")
            self.add_to_thinking_log(f"AI selected move: {final_move_str}")
        else:
            self.status_var.set("No move found")
            self.add_to_thinking_log("AI couldn't find a valid move!")

    def make_ai_move(self, move):
        """Make the AI's move on the board"""
        if not move:
            self.ai_thinking = False
            self.status_var.set("Waiting...")
            return

        self.board.make_move(move)
        self.clear_highlight()
        self.update_board()
        self.update_info()

        # Reset AI thinking flag
        self.ai_thinking = False
        self.status_var.set("Completed")

        # Check for game end
        self.check_for_game_end()

    def check_for_game_end(self):
        """Check if the game has ended (checkmate, stalemate, etc.)"""
        move_gen = MoveGenerator(self.board)
        legal_moves = move_gen.generate_legal_moves()

        if not legal_moves:
            if self.board.is_in_check():
                winner = "White" if not self.board.is_white_to_move else "Black"
                self.show_winner(winner, "checkmate")
            else:
                self.show_stalemate()
        elif self.board.fifty_move_counter >= 100:
            self.show_draw("fifty-move rule")
        else:
            # Continue game - check if it's AI's turn again
            self.check_ai_turn()

    def show_winner(self, winner, reason="wins"):
        """Override to include AI status"""
        super().show_winner(winner)
        self.status_var.set(f"Game over - {winner} {reason}")
        self.add_to_thinking_log(f"Game over - {winner} {reason}")

    def show_stalemate(self):
        """Show stalemate dialog"""
        messagebox.showinfo("Game Over", "Draw by stalemate!")
        self.status_var.set("Game over - Draw by stalemate")
        self.add_to_thinking_log("Game over - Draw by stalemate")
        self.disable_board()

    def show_draw(self, reason):
        """Show draw dialog"""
        messagebox.showinfo("Game Over", f"Draw by {reason}!")
        self.status_var.set(f"Game over - Draw by {reason}")
        self.add_to_thinking_log(f"Game over - Draw by {reason}")
        self.disable_board()

    def format_move(self, move):
        """Format a move object into readable text"""
        if not move:
            return "--"

        from_sq = move.from_square
        to_sq = move.to_square
        from_col, from_row = from_sq % 8, from_sq // 8
        to_col, to_row = to_sq % 8, to_sq // 8

        col_names = "abcdefgh"
        row_names = "87654321"

        from_name = col_names[from_col] + row_names[from_row]
        to_name = col_names[to_col] + row_names[to_row]

        return f"{from_name}->{to_name}"

    def exit_to_main_menu(self):
        """Exit to main menu"""
        self.ai_enabled = False
        if self.thinking_thread and self.thinking_thread.is_alive():
            self.thinking_thread.join(timeout=0.5)

        # Close the current window
        self.master.destroy()

        # Import to avoid circular imports
        from src.main import main

        # Start the main menu
        main()


class VisualizationAlphaBetaAgent:
    """
    Modified Alpha-Beta agent that provides visualization updates
    """

    def __init__(self, max_depth=4, time_limit=None, update_callback=None):
        from src.agent.alpha_beta import AlphaBetaAgent

        self.agent = AlphaBetaAgent(max_depth=max_depth, time_limit=time_limit)
        self.update_callback = update_callback
        self.nodes_evaluated = 0
        self.current_best_move = None
        self.current_score = 0
        self.start_time = 0

    def choose_move(self, board):
        """Choose the best move with visualization updates"""
        self.start_time = time.time()
        self.nodes_evaluated = 0

        # Override the alpha_beta method to include visualization
        original_alpha_beta = self.agent._alpha_beta

        def alpha_beta_with_visualization(board, depth, alpha, beta, color_factor):
            """Wrapped alpha-beta method with visualization updates"""
            result = original_alpha_beta(board, depth, alpha, beta, color_factor)
            self.nodes_evaluated = self.agent.nodes_evaluated
            return result

        # Replace the method temporarily
        self.agent._alpha_beta = alpha_beta_with_visualization

        # Override the choose_move method to capture intermediate results
        original_choose_move = self.agent.choose_move

        def choose_move_with_visualization(board):
            """Wrapped choose_move method with visualization updates"""
            # Get all legal moves
            from src.core.Board.move_generator import MoveGenerator

            move_generator = MoveGenerator(board)
            legal_moves = move_generator.generate_legal_moves()

            if not legal_moves:
                return None

            import random

            random.shuffle(legal_moves)

            # Best move found and its score
            best_move = None
            best_score = -float("inf")

            # Alpha-beta bounds
            alpha = -float("inf")
            beta = float("inf")

            # Color factor (1 for white, -1 for black)
            color_factor = 1 if board.is_white_to_move else -1

            # Iterative deepening
            for current_depth in range(1, self.agent.max_depth + 1):
                # Search each move
                for move in legal_moves:
                    board.make_move(move, in_search=True)

                    # Search from this position
                    score = -self.agent._alpha_beta(
                        board, current_depth - 1, -beta, -alpha, -color_factor
                    )

                    board.unmake_move(move, in_search=True)

                    # Update best move if found a better one
                    if score > best_score:
                        best_score = score
                        best_move = move
                        self.current_best_move = move
                        self.current_score = score

                        # Call the visualization callback
                        if self.update_callback:
                            elapsed = time.time() - self.start_time
                            self.update_callback(
                                self.agent.max_depth,
                                current_depth,
                                move,
                                score,
                                self.nodes_evaluated,
                                elapsed,
                            )

                    # Update alpha
                    alpha = max(alpha, score)

                # Update visualization after each depth is completed
                if self.update_callback:
                    elapsed = time.time() - self.start_time
                    self.update_callback(
                        self.agent.max_depth,
                        current_depth,
                        best_move,
                        best_score,
                        self.nodes_evaluated,
                        elapsed,
                    )

            return best_move

        # Replace the method temporarily
        self.agent.choose_move = choose_move_with_visualization

        # Call the modified choose_move
        result = self.agent.choose_move(board)

        # Restore the original methods
        self.agent._alpha_beta = original_alpha_beta
        self.agent.choose_move = original_choose_move

        return result


def run_ai_visualizer():
    """Run the AI Visualizer GUI"""
    root = tk.Tk()
    root.title("Chess AI Visualizer")
    app = AIVisualizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_ai_visualizer()

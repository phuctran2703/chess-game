from src.core.Board.move_generator import MoveGenerator
from src.agent.evaluation import evaluate_board
import random
import time
import sys


class AlphaBetaAgent:
    """
    Chess agent using Alpha-Beta Pruning + Negamax algorithm
    """

    def __init__(self, max_depth=4, time_limit=None):
        """
        Initialize the Alpha-Beta agent

        Parameters:
        - max_depth: Maximum search depth
        - time_limit: Maximum time in seconds to spend searching
        """
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.start_time = 0
        self.nodes_evaluated = 0
        self.transposition_table = {}  # Cache for positions already evaluated

    def choose_move(self, board):
        """
        Choose the best move for the current position using Alpha-Beta pruning

        Parameters:
        - board: Current board state

        Returns:
        - best_move: The best move found
        """
        self.start_time = time.time()
        self.nodes_evaluated = 0
        self.transposition_table = {}

        move_generator = MoveGenerator(board)

        legal_moves = move_generator.generate_legal_moves()

        if not legal_moves:
            return None

        # For randomness in equal positions, shuffle moves before searching
        random.shuffle(legal_moves)

        # Best move found and its score
        best_move = None
        best_score = -sys.maxsize

        # Alpha-beta bounds
        alpha = -sys.maxsize
        beta = sys.maxsize

        # Color factor (1 for white, -1 for black)
        color_factor = 1 if board.is_white_to_move else -1
        self.original_color = color_factor

        # Iterative deepening
        for current_depth in range(1, self.max_depth + 1):
            if self.time_limit and time.time() - self.start_time > self.time_limit:
                break

            # Search each move
            for move in legal_moves:
                # Try to make the move - if it returns False, skip it
                move_result = board.make_move(move, in_search=True)
                if move_result is False:
                    # This move was rejected (likely a king capture) - skip it
                    continue

                # Search from this position
                score = -self._alpha_beta(
                    board, current_depth - 1, -beta, -alpha, -color_factor
                )

                board.unmake_move(move, in_search=True)

                # Check if time limit exceeded
                if self.time_limit and time.time() - self.start_time > self.time_limit:
                    break

                # Update best move if found a better one
                if score > best_score:
                    best_score = score
                    best_move = move

                # Update alpha
                alpha = max(alpha, score)

            print(
                f"Depth {current_depth} completed. Best move: {best_move} with score: {best_score}"
            )

            # Time limit exceeded
            if self.time_limit and time.time() - self.start_time > self.time_limit:
                break

        print(f"Nodes evaluated: {self.nodes_evaluated}")
        print(f"Time spent: {time.time() - self.start_time:.2f} seconds")

        return best_move

    def _alpha_beta(self, board, depth, alpha, beta, color_factor):
        """
        Alpha-Beta pruning search algorithm

        Parameters:
        - board: Current board state
        - depth: Current search depth
        - alpha: Alpha value for pruning
        - beta: Beta value for pruning
        - color_factor: 1 for white perspective, -1 for black perspective

        Returns:
        - score: The best score found from this position
        """
        # Check if time limit exceeded
        if self.time_limit and time.time() - self.start_time > self.time_limit:
            return 0

        # Generate a hash key for the board position
        position_key = self._get_position_key(board)

        # Check transposition table
        if (
            position_key in self.transposition_table
            and self.transposition_table[position_key]["depth"] >= depth
        ):
            return self.transposition_table[position_key]["score"]

        # Leaf node (terminal position or max depth reached)
        if depth == 0:
            self.nodes_evaluated += 1
            evaluate_score = color_factor * (evaluate_board(board) - self.original_color*board.fifty_move_counter*10)
            return evaluate_score

        move_generator = MoveGenerator(board)
        legal_moves = move_generator.generate_legal_moves()

        # No legal moves - check for checkmate or stalemate
        if not legal_moves:
            if board.is_in_check():
                # Checkmate (worst possible score, adjusted for search depth for quicker mates)
                return -1000000 + (self.max_depth - depth)
            else:
                # Stalemate (draw)
                return 0

        # Initialize best score
        best_score = -sys.maxsize

        # Search all moves
        for move in legal_moves:
            # Try to make the move - if it returns False, skip it
            move_result = board.make_move(move, in_search=True)
            if move_result is False:
                # This move was rejected (likely a king capture) - skip it
                continue

            # Recursively search
            score = -self._alpha_beta(board, depth - 1, -beta, -alpha, -color_factor)

            board.unmake_move(move, in_search=True)

            # Check if time limit exceeded
            if self.time_limit and time.time() - self.start_time > self.time_limit:
                return 0

            best_score = max(best_score, score)

            # Alpha-beta pruning
            alpha = max(alpha, score)
            if alpha >= beta:
                break

        self.transposition_table[position_key] = {"score": best_score, "depth": depth}

        return best_score

    def _get_position_key(self, board):
        """Generate a unique key for the board position for transposition table"""
        if hasattr(board, "zobrist_key"):
            return board.zobrist_key
        else:
            # Fallback to a simpler hash if zobrist not available
            return hash(tuple(board.square) + (board.is_white_to_move,))

    def set_depth(self, depth):
        """Set the maximum search depth"""
        if 1 <= depth <= 10:
            self.max_depth = depth

    def set_time_limit(self, seconds):
        """Set the maximum time limit for search in seconds"""
        self.time_limit = seconds

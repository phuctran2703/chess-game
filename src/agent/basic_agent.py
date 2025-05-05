import random
from src.core.Board.move_generator import MoveGenerator


class BasicAI:
    """
    A simple AI that follows chess rules but makes random moves
    without any evaluation or search
    """

    def __init__(self):
        """Initialize the basic AI"""
        pass

    def choose_move(self, board):
        """
        Choose a random legal move

        Parameters:
        - board: Current board state

        Returns:
        - A random legal move
        """
        move_generator = MoveGenerator(board)

        legal_moves = move_generator.generate_legal_moves()

        # Return a random move, or None if no legal moves
        if legal_moves:
            return random.choice(legal_moves)
        return None

import random
from src.core.Board.move_generator import MoveGenerator
from src.agent.skill_level import SkillLevel


class BasicAI:
    """
    A simple AI that follows chess rules but makes random moves
    without any evaluation or search
    """

    def __init__(self, skill_level=None):
        """
        Initialize the basic AI

        Parameters:
        - skill_level: Optional explicit skill level (default: None, will use level 1)
        """
        # Basic AI is always level 1 (lowest skill)
        self.skill_level = SkillLevel(1) if skill_level is None else SkillLevel(skill_level)

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

    def set_skill_level(self, level):
        """
        Set the skill level

        Parameters:
        - level: Skill level (1-10)
        """
        self.skill_level = SkillLevel(level)

    def get_skill_level(self):
        """
        Get the current skill level

        Returns:
        - SkillLevel object representing the agent's skill level
        """
        return self.skill_level

    # These methods are added for compatibility with ChessAI interface
    def set_depth(self, depth):
        """
        Dummy method for compatibility with ChessAI
        BasicAI doesn't use depth, but this allows uniform interface
        """
        pass

    def set_time_limit(self, seconds):
        """
        Dummy method for compatibility with ChessAI
        BasicAI doesn't use time limits, but this allows uniform interface
        """
        pass

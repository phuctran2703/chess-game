from src.agent.alpha_beta import AlphaBetaAgent
from src.agent.skill_level import SkillLevel

class ChessAI:
    """
    Chess AI player that uses Alpha-Beta pruning to choose moves
    """
    def __init__(self, depth=4, time_limit=None, skill_level=None):
        """
        Initialize the Chess AI player

        Parameters:
        - depth: Maximum search depth (default: 4)
        - time_limit: Maximum time in seconds to think (default: None)
        - skill_level: Optional explicit skill level (1-10)
        """
        self.agent = AlphaBetaAgent(max_depth=depth, time_limit=time_limit)

        # Set skill level based on depth if not explicitly provided
        if skill_level is not None:
            self.skill_level = SkillLevel(skill_level)
        else:
            # Map depth to approximate skill level
            if depth == 1:
                self.skill_level = SkillLevel(3)
            elif depth == 2:
                self.skill_level = SkillLevel(5)
            elif depth == 3:
                self.skill_level = SkillLevel(7)
            elif depth == 4:
                self.skill_level = SkillLevel(9)
            else:  # depth >= 5
                self.skill_level = SkillLevel(10)

    def choose_move(self, board):
        """
        Choose the best move for the current board position

        Parameters:
        - board: Current board state

        Returns:
        - move: The best move according to Alpha-Beta pruning
        """
        return self.agent.choose_move(board)

    def set_depth(self, depth):
        """Set the maximum search depth"""
        self.agent.set_depth(depth)

        # Update skill level to match new depth
        if depth == 1:
            self.skill_level = SkillLevel(3)
        elif depth == 2:
            self.skill_level = SkillLevel(5)
        elif depth == 3:
            self.skill_level = SkillLevel(7)
        elif depth == 4:
            self.skill_level = SkillLevel(9)
        else:  # depth >= 5
            self.skill_level = SkillLevel(10)

    def set_time_limit(self, seconds):
        """Set the maximum time limit for search in seconds"""
        self.agent.set_time_limit(seconds)

    def set_skill_level(self, level):
        """
        Set the skill level directly

        Parameters:
        - level: Skill level (1-10)
        """
        self.skill_level = SkillLevel(level)

        # Adjust depth to match the skill level
        if level <= 3:
            self.set_depth(1)
        elif level <= 5:
            self.set_depth(2)
        elif level <= 7:
            self.set_depth(3)
        elif level <= 9:
            self.set_depth(4)
        else:  # level 10
            self.set_depth(5)

    def get_skill_level(self):
        """
        Get the current skill level

        Returns:
        - SkillLevel object representing the agent's skill level
        """
        return self.skill_level
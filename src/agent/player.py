from src.agent.alpha_beta import AlphaBetaAgent

class ChessAI:
    """
    Chess AI player that uses Alpha-Beta pruning to choose moves
    """
    def __init__(self, depth=4, time_limit=None):
        """
        Initialize the Chess AI player
        
        Parameters:
        - depth: Maximum search depth (default: 4)
        - time_limit: Maximum time in seconds to think (default: None)
        """
        self.agent = AlphaBetaAgent(max_depth=depth, time_limit=time_limit)
        
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
        
    def set_time_limit(self, seconds):
        """Set the maximum time limit for search in seconds"""
        self.agent.set_time_limit(seconds)
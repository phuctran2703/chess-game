"""
Skill Assessment Module for Chess Agents

This module provides functionality to assess the playing skill level of chess agents.
Skill levels are categorized as:
- Poor (levels 1-3)
- Average (levels 4-7)
- Good (levels 8-10)

The assessment is based on multiple factors:
1. Search depth (for alpha-beta agents)
2. Performance against reference agents
3. Decision quality analysis
4. Tournament results
"""

import random
from src.core.Board.board import Board
from src.core.Board.move_generator import MoveGenerator
from src.agent.skill_level import SkillLevel
from src.agent.evaluation import evaluate_board

# Import these here to avoid circular imports
from src.agent.player import ChessAI
from src.agent.basic_agent import BasicAI


class SkillAssessor:
    """
    Class for assessing the skill level of chess agents
    """

    def __init__(self):
        """Initialize the skill assessor"""
        self.reference_agents = {
            1: BasicAI(),  # Level 1: Random move agent
            3: ChessAI(depth=1),  # Level 3: Alpha-Beta depth 1
            5: ChessAI(depth=2),  # Level 5: Alpha-Beta depth 2
            7: ChessAI(depth=3),  # Level 7: Alpha-Beta depth 3
            9: ChessAI(depth=4),  # Level 9: Alpha-Beta depth 4
            10: ChessAI(depth=5),  # Level 10: Alpha-Beta depth 5
        }

    def assess_agent(self, agent, num_games=10, time_per_move=1.0):
        """
        Assess an agent's skill level

        Parameters:
        - agent: The chess agent to assess
        - num_games: Number of test games to play
        - time_per_move: Time limit per move in seconds

        Returns:
        - SkillLevel object representing the assessed skill level
        """
        base_level = self._assess_agent_configuration(agent)

        # Refine assessment through test games if requested
        if num_games > 0:
            performance_level = self._assess_through_games(
                agent, num_games, time_per_move
            )

            # Combine base assessment with performance assessment
            # Giving more weight to actual performance
            final_level = round((base_level + 2 * performance_level) / 3)
        else:
            final_level = base_level

        return SkillLevel(final_level)

    def _assess_agent_configuration(self, agent):
        """
        Assess an agent based on its type and configuration

        Parameters:
        - agent: The chess agent to assess

        Returns:
        - Base skill level (1-10)
        """
        # Basic random move agent is level 1
        if isinstance(agent, BasicAI):
            return 1

        # Alpha-Beta agent's level depends on search depth
        if isinstance(agent, ChessAI):
            if hasattr(agent, "agent") and hasattr(agent.agent, "max_depth"):
                depth = agent.agent.max_depth
                # Map depth to skill level:
                # Depth 1 -> Level 3
                # Depth 2 -> Level 5
                # Depth 3 -> Level 7
                # Depth 4 -> Level 9
                # Depth 5+ -> Level 10
                if depth == 1:
                    return 3
                elif depth == 2:
                    return 5
                elif depth == 3:
                    return 7
                elif depth == 4:
                    return 9
                elif depth >= 5:
                    return 10

        # Default to level 1 if agent type is unknown
        return 1

    def _assess_through_games(self, agent, num_games, time_per_move):
        """
        Assess an agent by playing test games against reference agents

        Parameters:
        - agent: The chess agent to assess
        - num_games: Number of test games to play
        - time_per_move: Time limit per move in seconds

        Returns:
        - Performance-based skill level (1-10)
        """
        # Start with mid-level reference agent (level 5)
        current_opponent_level = 5
        wins = 0

        # Play games against reference agents, adjusting opponent level
        # based on performance
        for game in range(num_games):
            opponent = self.reference_agents[current_opponent_level]

            # Randomly assign colors
            if random.random() < 0.5:
                white_agent, black_agent = agent, opponent
                agent_is_white = True
            else:
                white_agent, black_agent = opponent, agent
                agent_is_white = False

            result = self._play_test_game(white_agent, black_agent, time_per_move)

            # Update wins and adjust opponent level
            if (result == 1 and agent_is_white) or (
                result == -1 and not agent_is_white
            ):
                wins += 1
                # If agent won, increase opponent level (if not already at max)
                if current_opponent_level < 10:
                    current_opponent_level = min(10, current_opponent_level + 2)
            else:
                # If agent lost or drew, decrease opponent level (if not already at min)
                if current_opponent_level > 1:
                    current_opponent_level = max(1, current_opponent_level - 1)

        win_rate = wins / num_games

        # Calculate performance level based on win rate and final opponent level
        # Win rate contributes 40%, final opponent level contributes 60%
        performance_level = round(0.4 * (win_rate * 10) + 0.6 * current_opponent_level)

        # Ensure level is within valid range
        return max(1, min(10, performance_level))

    def _play_test_game(self, white_agent, black_agent, time_per_move, max_moves=100):
        """
        Play a test game between two agents

        Parameters:
        - white_agent: Agent playing white
        - black_agent: Agent playing black
        - time_per_move: Time limit per move in seconds
        - max_moves: Maximum number of moves before declaring a draw

        Returns:
        - 1 if white wins, -1 if black wins, 0 for draw
        """
        board = Board()
        move_count = 0

        while move_count < max_moves:
            current_agent = white_agent if board.is_white_to_move else black_agent

            # Set time limit if agent supports it
            if hasattr(current_agent, "set_time_limit"):
                current_agent.set_time_limit(time_per_move)

            # Get agent's move
            move = current_agent.choose_move(board)

            # If no legal moves, game is over
            if move is None:
                move_gen = MoveGenerator(board)
                legal_moves = move_gen.generate_legal_moves()

                if not legal_moves:
                    if board.is_in_check():
                        # Checkmate
                        return -1 if board.is_white_to_move else 1
                    else:
                        # Stalemate
                        return 0
                else:
                    # Agent failed to find a move despite legal moves existing
                    return -1 if board.is_white_to_move else 1

            board.make_move(move)
            move_count += 1

            # Check for insufficient material (simplified)
            if self._has_insufficient_material(board):
                return 0

        # If max moves reached, evaluate position to determine result
        score = evaluate_board(board)
        if abs(score) < 200:  # Within 2 pawns of material
            return 0  # Draw
        return 1 if score > 0 else -1

    def _has_insufficient_material(self, board):
        """
        Check if the position has insufficient material for checkmate

        Parameters:
        - board: Current board state

        Returns:
        - True if insufficient material, False otherwise
        """
        # Count total pieces
        total_pieces = 0
        for square in range(64):
            if board.square[square] != 0:  # 0 is empty square
                total_pieces += 1

        # Only kings left
        if total_pieces <= 2:
            return True

        # King and knight or king and bishop vs king is insufficient
        if (
            total_pieces <= 3
            and (
                board.all_piece_lists[2].count
                + board.all_piece_lists[8].count  # Knights
                + board.all_piece_lists[3].count
                + board.all_piece_lists[9].count  # Bishops
            )
            <= 1
        ):
            return True

        return False

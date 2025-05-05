from src.core.Board.piece import *
from src.core.Board.move import Move
from src.core.Board.bitboard_utility import (
    KNIGHT_ATTACKS,
    KING_MOVES,
    WHITE_PAWN_ATTACKS,
    BLACK_PAWN_ATTACKS,
    contains_square,
)


class MoveGenerator:
    def __init__(self, board):
        """
        Initialize MoveGenerator with a board object.
        """
        self.board = board

    def generate_legal_moves(self):
        """
        Generate all legal moves for the active side based on the current state of the board.
        Returns a list of Move objects that don't leave the king in check.
        """
        pseudo_legal_moves = []
        for square in range(64):
            piece = self.board.square[square]
            if piece == NONE:
                continue

            # Check if the piece belongs to the active side
            if (self.board.is_white_to_move and not is_white(piece)) or (
                not self.board.is_white_to_move and is_white(piece)
            ):
                continue

            piece_type_val = piece_type(piece)
            if piece_type_val == PAWN:
                pseudo_legal_moves.extend(self._pawn_moves(square, piece))
            elif piece_type_val == KNIGHT:
                pseudo_legal_moves.extend(self._knight_moves(square, piece))
            elif piece_type_val == BISHOP:
                pseudo_legal_moves.extend(self._bishop_moves(square, piece))
            elif piece_type_val == ROOK:
                pseudo_legal_moves.extend(self._rook_moves(square, piece))
            elif piece_type_val == QUEEN:
                pseudo_legal_moves.extend(self._queen_moves(square, piece))
            elif piece_type_val == KING:
                pseudo_legal_moves.extend(self._king_moves(square, piece))

        # Filter out moves that would leave the king in check
        # Using a simplified approach that doesn't involve making/unmaking moves
        legal_moves = []
        king_square = self.board.king_square[self.board.move_colour_index]
        king_piece = self.board.square[king_square]
        
        for move in pseudo_legal_moves:
            # Special handling for king moves
            if piece_type(self.board.square[move.start_square]) == KING:
                # For king moves, we've already verified they don't move into check in _king_moves
                legal_moves.append(move)
                continue
                
            # For non-king moves, we need to check if they would expose the king to check
            # Make a simplified test of the move without using make_move/unmake_move
            is_legal = True
            
            # Save original board state we need to modify
            original_square_start = self.board.square[move.start_square]
            original_square_target = self.board.square[move.target_square]
            
            # Simulate the move
            self.board.square[move.target_square] = original_square_start
            self.board.square[move.start_square] = NONE
            
            # Check if king is under attack after the move
            opponent_attacks = self._generate_opponent_attacks()
            if king_square in opponent_attacks:
                is_legal = False
                
            # Restore the board state
            self.board.square[move.start_square] = original_square_start
            self.board.square[move.target_square] = original_square_target
            
            if is_legal:
                legal_moves.append(move)

        return legal_moves

    def _pawn_moves(self, square, piece):
        """
        Generate all legal moves for a pawn at position 'square'.
        Includes straight movement, diagonal captures, promotion, and en passant captures.
        """
        moves = []
        direction = 8 if is_white(piece) else -8
        start_rank = 1 if is_white(piece) else 6
        promotion_rank = 6 if is_white(piece) else 1
        row = square // 8
        col = square % 8

        # Move forward one square
        target = square + direction
        if 0 <= target < 64 and self.board.square[target] == NONE:
            # Promotion
            if row == promotion_rank:
                promotion_flags = [
                    Move.PROMOTE_TO_QUEEN_FLAG,
                    Move.PROMOTE_TO_ROOK_FLAG,
                    Move.PROMOTE_TO_BISHOP_FLAG,
                    Move.PROMOTE_TO_KNIGHT_FLAG,
                ]
                for flag in promotion_flags:
                    moves.append(Move(square, target, flag))
            else:
                moves.append(Move(square, target))

                # Move forward two squares from starting position
                if row == start_rank:
                    target2 = square + 2 * direction
                    if self.board.square[target2] == NONE:
                        moves.append(Move(square, target2, Move.PAWN_TWO_UP_FLAG))

        # Diagonal attacks
        pawn_attacks = (
            WHITE_PAWN_ATTACKS[square]
            if is_white(piece)
            else BLACK_PAWN_ATTACKS[square]
        )
        for attack_target in range(64):
            if contains_square(pawn_attacks, attack_target):
                target_piece = self.board.square[attack_target]
                if target_piece != NONE and is_white(target_piece) != is_white(piece):
                    # Promotion
                    if row == promotion_rank:
                        promotion_flags = [
                            Move.PROMOTE_TO_QUEEN_FLAG,
                            Move.PROMOTE_TO_ROOK_FLAG,
                            Move.PROMOTE_TO_BISHOP_FLAG,
                            Move.PROMOTE_TO_KNIGHT_FLAG,
                        ]
                        for flag in promotion_flags:
                            moves.append(Move(square, attack_target, flag))
                    else:
                        moves.append(Move(square, attack_target))

        # En passant capture
        if (
            hasattr(self.board.current_game_state, "en_passant_file")
            and self.board.current_game_state.en_passant_file
        ):
            ep_file = self.board.current_game_state.en_passant_file - 1
            ep_rank = 4 if is_white(piece) else 3
            if row == ep_rank and abs(col - ep_file) == 1:
                ep_target = (
                    (ep_rank + 1) * 8 + ep_file
                    if is_white(piece)
                    else (ep_rank - 1) * 8 + ep_file
                )
                moves.append(Move(square, ep_target, Move.EN_PASSANT_CAPTURE_FLAG))

        return moves

    def _knight_moves(self, square, piece):
        """
        Generate all legal moves for a knight at position 'square'.
        Uses pre-calculated KNIGHT_ATTACKS table.
        """
        moves = []
        knight_attacks = KNIGHT_ATTACKS[square]

        for target in range(64):
            if contains_square(knight_attacks, target):
                target_piece = self.board.square[target]
                if target_piece == NONE or is_white(target_piece) != is_white(piece):
                    moves.append(Move(square, target))

        return moves

    def _bishop_moves(self, square, piece):
        """
        Generate all legal moves for a bishop at position 'square'.
        """
        moves = []
        row = square // 8
        col = square % 8

        # Check 4 diagonal directions
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            r, c = row, col
            while True:
                r += dr
                c += dc
                if not (0 <= r < 8 and 0 <= c < 8):
                    break

                target = r * 8 + c
                target_piece = self.board.square[target]

                if target_piece == NONE:
                    moves.append(Move(square, target))
                else:
                    if is_white(target_piece) != is_white(piece):
                        moves.append(Move(square, target))
                    break

        return moves

    def _rook_moves(self, square, piece):
        """
        Generate all legal moves for a rook at position 'square'.
        """
        moves = []
        row = square // 8
        col = square % 8

        # Check 4 orthogonal directions
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = row, col
            while True:
                r += dr
                c += dc
                if not (0 <= r < 8 and 0 <= c < 8):
                    break

                target = r * 8 + c
                target_piece = self.board.square[target]

                if target_piece == NONE:
                    moves.append(Move(square, target))
                else:
                    if is_white(target_piece) != is_white(piece):
                        moves.append(Move(square, target))
                    break

        return moves

    def _queen_moves(self, square, piece):
        """
        Generate all legal moves for a queen at position 'square'.
        Combines the moves of rook and bishop.
        """
        return self._rook_moves(square, piece) + self._bishop_moves(square, piece)

    def _king_moves(self, square, piece):
        """
        Generate all legal moves for a king at position 'square'.
        Includes regular moves and castling.
        """
        moves = []

        # Determine squares under attack by opponent
        opponent_attacks = self._generate_opponent_attacks()
        king_moves = KING_MOVES[square]

        # Regular king moves (8 directions)
        for target in range(64):
            if contains_square(king_moves, target):
                target_piece = self.board.square[target]
                if (
                    target_piece == NONE or is_white(target_piece) != is_white(piece)
                ) and target not in opponent_attacks:
                    moves.append(Move(square, target))

        # Handle castling
        if hasattr(self.board.current_game_state, "castling_rights"):
            rights = self.board.current_game_state.castling_rights
            is_white_king = is_white(piece)
            king_row = 0 if is_white_king else 7

            # Kingside castling (g-file)
            kingside_mask = 1 if is_white_king else 4
            if rights & kingside_mask:
                if (
                    self.board.square[king_row * 8 + 5] == NONE
                    and self.board.square[king_row * 8 + 6] == NONE
                    and (king_row * 8 + 4) not in opponent_attacks
                    and (king_row * 8 + 5) not in opponent_attacks
                    and (king_row * 8 + 6) not in opponent_attacks
                ):
                    moves.append(Move(square, king_row * 8 + 6, Move.CASTLE_FLAG))

            # Queenside castling (c-file)
            queenside_mask = 2 if is_white_king else 8
            if rights & queenside_mask:
                if (
                    self.board.square[king_row * 8 + 1] == NONE
                    and self.board.square[king_row * 8 + 2] == NONE
                    and self.board.square[king_row * 8 + 3] == NONE
                    and (king_row * 8 + 2) not in opponent_attacks
                    and (king_row * 8 + 3) not in opponent_attacks
                    and (king_row * 8 + 4) not in opponent_attacks
                ):
                    moves.append(Move(square, king_row * 8 + 2, Move.CASTLE_FLAG))

        return moves

    def get_legal_moves_for_square(self, square):
        """
        Returns a list of legal moves (Move objects) that the piece at position 'square' can make.
        Filters out moves that would leave the king in check.
        """
        piece = self.board.square[square]
        if piece == NONE:
            return []

        # Only generate moves for pieces of the active side
        if (self.board.is_white_to_move and not is_white(piece)) or (
            not self.board.is_white_to_move and is_white(piece)
        ):
            return []

        # Generate all pseudo-legal moves for this piece
        pseudo_legal_moves = []
        if piece_type(piece) == PAWN:
            pseudo_legal_moves = self._pawn_moves(square, piece)
        elif piece_type(piece) == KNIGHT:
            pseudo_legal_moves = self._knight_moves(square, piece)
        elif piece_type(piece) == BISHOP:
            pseudo_legal_moves = self._bishop_moves(square, piece)
        elif piece_type(piece) == ROOK:
            pseudo_legal_moves = self._rook_moves(square, piece)
        elif piece_type(piece) == QUEEN:
            pseudo_legal_moves = self._queen_moves(square, piece)
        elif piece_type(piece) == KING:
            pseudo_legal_moves = self._king_moves(square, piece)

        # Filter out moves that would leave the king in check
        # Using a simplified approach that doesn't involve making/unmaking moves
        legal_moves = []
        king_square = self.board.king_square[self.board.move_colour_index]
        
        for move in pseudo_legal_moves:
            # Special handling for king moves
            if piece_type(self.board.square[move.start_square]) == KING:
                # For king moves, we've already verified they don't move into check in _king_moves
                legal_moves.append(move)
                continue
                
            # For non-king moves, we need to check if they would expose the king to check
            # Make a simplified test of the move without using make_move/unmake_move
            is_legal = True
            
            # Save original board state we need to modify
            original_square_start = self.board.square[move.start_square]
            original_square_target = self.board.square[move.target_square]
            
            # Simulate the move
            self.board.square[move.target_square] = original_square_start
            self.board.square[move.start_square] = NONE
            
            # Check if king is under attack after the move
            opponent_attacks = self._generate_opponent_attacks()
            if king_square in opponent_attacks:
                is_legal = False
                
            # Restore the board state
            self.board.square[move.start_square] = original_square_start
            self.board.square[move.target_square] = original_square_target
            
            if is_legal:
                legal_moves.append(move)

        return legal_moves

    def _generate_opponent_attacks(self):
        """
        Generate a set of all squares controlled by opponent pieces.
        """
        attacks = set()
        for sq in range(64):
            piece = self.board.square[sq]
            if piece == NONE or is_white(piece) == self.board.is_white_to_move:
                continue  # only consider opponent pieces

            piece_type_val = piece_type(piece)

            if piece_type_val == PAWN:
                # Use pre-calculated attack tables
                pawn_attacks = (
                    WHITE_PAWN_ATTACKS[sq]
                    if is_white(piece)
                    else BLACK_PAWN_ATTACKS[sq]
                )
                for i in range(64):
                    if contains_square(pawn_attacks, i):
                        attacks.add(i)

            elif piece_type_val == KNIGHT:
                # Use pre-calculated attack tables
                knight_attacks = KNIGHT_ATTACKS[sq]
                for i in range(64):
                    if contains_square(knight_attacks, i):
                        attacks.add(i)

            elif piece_type_val in (BISHOP, ROOK, QUEEN):
                row, col = divmod(sq, 8)
                directions = []

                if piece_type_val in (BISHOP, QUEEN):
                    directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

                if piece_type_val in (ROOK, QUEEN):
                    directions += [(-1, 0), (1, 0), (0, -1), (0, 1)]

                for dr, dc in directions:
                    r, c = row, col
                    while True:
                        r += dr
                        c += dc
                        if not (0 <= r < 8 and 0 <= c < 8):
                            break

                        idx = r * 8 + c
                        attacks.add(idx)

                        if self.board.square[idx] != NONE:
                            break

            elif piece_type_val == KING:
                # Use pre-calculated attack tables
                king_moves = KING_MOVES[sq]
                for i in range(64):
                    if contains_square(king_moves, i):
                        attacks.add(i)

        return attacks

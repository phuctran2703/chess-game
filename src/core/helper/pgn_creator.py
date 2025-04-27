from src.core.helper.board_helper import *
from src.core.Board.piece import *

def create_pgn(moves, result=None, start_fen=None, white_name="", black_name=""):
    # TODO: Import Board, MoveUtility, GameResult, FenUtility for full logic
    start_fen = (start_fen or "").replace("\n", "").replace("\r", "")
    pgn = []
    # board = Board()
    # board.load_position(start_fen)
    if white_name:
        pgn.append(f'[White "{white_name}"]')
    if black_name:
        pgn.append(f'[Black "{black_name}"]')
    # if start_fen and start_fen != FenUtility.START_POSITION_FEN:
    #     pgn.append(f'[FEN "{start_fen}"]')
    if result not in (None, "NotStarted", "InProgress"):
        pgn.append(f'[Result "{result}"]')
    for ply_count, move in enumerate(moves):
        # move_string = MoveUtility.get_move_name_san(move, board)
        move_string = str(move)  # Placeholder
        # board.make_move(move)
        if ply_count % 2 == 0:
            pgn.append(f'{(ply_count // 2) + 1}. {move_string}')
        else:
            pgn[-1] += f' {move_string}'
    return '\n'.join(pgn)

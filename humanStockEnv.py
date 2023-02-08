import chess
from stockfish import Stockfish

board = chess.Board()

stockfish = Stockfish(path="stockfish_15.1/stockfish.exe", depth=15)
stockfish.set_fen_position(board.fen())

def botMove():
    bmove = stockfish.get_best_move_time(1000)
    stockfish.make_moves_from_current_position([bmove])
    return bmove
def agentMove(m):
    if chess.Move.from_uci(move) in board.legal_moves:
        pass
    else:
        pass

while True:
    move = input("Move: ")
    cont = True
    if chess.Move.from_uci(move) in board.legal_moves:
        pass
    else:
        while cont:
            move = input("Move: ")
            if chess.Move.from_uci(move) in board.legal_moves:
                cont = False
            else:
                print("invalid move")
    board.push_uci(move)
    print(board)
    stockfish.make_moves_from_current_position([move])
    bmove = stockfish.get_best_move_time(1000)
    stockfish.make_moves_from_current_position([bmove])
    board.push_san(bmove)
    print(board)



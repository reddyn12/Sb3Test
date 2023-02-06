# SHOUTOUT https://www.youtube.com/watch?v=iEaU__JdI7c

from stockfish import Stockfish
import chess

board = chess.Board()
print(board)
board.push_san("d4")
print(board)
stockfish = Stockfish(path="stockfish_15.1/stockfish.exe", depth=25)

stockfish.update_engine_parameters({"Hash":32768, "UCI_Elo":3000, "Threads":10})

stockfish.set_fen_position(board.fen())
print(stockfish.get_evaluation())
m=stockfish.get_best_move()
print(m)
board.push_san(m)
stockfish.set_fen_position(board.fen())
print(stockfish.get_evaluation())
m=stockfish.get_best_move()
print(m)


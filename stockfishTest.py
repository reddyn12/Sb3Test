from stockfish import Stockfish

stockfish = Stockfish(path="stockfish_15.1/stockfish.exe", depth=25)

stockfish.update_engine_parameters({"Hash":32768, "UCI_Elo":3000, "Threads":10})

import io
import gym
from gym import spaces
import chess
import chess.svg
import sys
import time
import matplotlib.pyplot as plt
import svg.path
import re


# b =  chess.Board()
# for i in (b.generate_legal_moves()):
#     print(i)
# print(chess.svg.board(b, size=350))
# time.sleep(100)
def makeActions():
    ans = []
    tiles = []
    for i in ["a","b","c","d","e","f","g","h"]:
        for j in ["1","2","3","4","5","6","7","8"]:
            tiles.append(i+j)
    #can make WAY better gen, reduce min 25% of action space
    for i in tiles:
        for j in tiles:
            if i!=j:
                ans.append(i+j)
    

    return ans
class ChessEnv(gym.Env):

    metadata = {"render.modes": ["human"]}
    def __init__(self, fen=None):
        super(ChessEnv, self).__init__()
        self.board = chess.Board(fen=fen) if fen else chess.Board()
        
        pass

    def reset(self, fen=None):
        self.board = chess.Board(fen=fen) if fen else chess.Board()
        pass
    # chess.svg??
    def render(self):
        pass


    # push uci for now for discrete action space... need to thnik if I want pgn or uci for final pipeline
    def step(self, action):
        obs = None
        reward = None
        done = None
        info = None
        try:
            self.board.push_uci(action)
        except Exception as e:
            done = True
            reward = -10000

        
        return obs, reward, done, info
import gym
from gym import spaces
import chess
import chess.svg
import sys
import time
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import http.server
import socketserver
import webbrowser
import threading
import requests
import numpy as np
from stockfish import Stockfish


class HTMLServer:
    def __init__(self, port=8000, board=chess.Board()):
        self.board = board
        self.port = port
        self.html_content = self.strBuild(chess.svg.board(board))
        self.httpd = None
        self.driver = None
    def strBuild(self, s):
        ans = """
        <html>
          <head>
            <title>My HTML Page</title>
            <script>
              function refresh() {
                window.location.reload();
              }
            </script>
          </head>
          <body>
            """+s+"""
          </body>
        </html>
        """

        return ans
    class HTTPRequestHandlerWithContent(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.server.html_content.encode())
        

    def start(self):
        self.httpd = socketserver.TCPServer(("", self.port), self.HTTPRequestHandlerWithContent)
        self.httpd.html_content = self.html_content
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.start()
        options = Options()
        options.add_argument("disable-infobars")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(f"http://localhost:{self.port}")
        self.driver.execute_script("document.body.style.pointerEvents = 'none';")
        # webbrowser.open_new_tab(f"http://localhost:{self.port}")
    
    def stop(self):
        
        self.driver.quit()
        self.driver.stop_client()
        self.httpd.shutdown()
    def update(self, board):
        self.board = board
        self.httpd.html_content = self.strBuild(board) #._repr_svg() works too
        # self.driver.refresh()



def display_board(board):
    board_svg = chess.svg.board(board=board)
    with open("board.svg", "w") as f:
        f.write(board_svg)
    print("Chess board displayed!")


# b =  chess.Board()
# for i in (b.generate_legal_moves()):
#     print(i)
# print(chess.svg.board(b, size=350))
# time.sleep(100)

def makeActions():
    moves = []
    for i in range(-2,3):
        for j in range(-2,3):
            if i==0 and j==0:
                pass
            else:
                moves.append((i,j))
    
    for i in range(-7,8):
        if i ==0:
            pass
        else:
            if (0,i) in moves:
                pass
            else:
                moves.append((0,i))
            if (i,0) in moves:
                pass
            else:
                moves.append((i,0))
    for i in range(-7,8):
        for j in range(-7,8):
            if abs(i)==abs(j):
                if i==0:
                    pass
                else:
                    if (i,j) in moves:
                        pass
                    else:
                        moves.append((i,j))
    print(len(moves))
    f = ["a","b","c","d","e","f","g","h"]
    f1 = {"a":1,"b":2,"c":3,"d":4,"e":5,"f":6,"g":7,"h":8}
    f2 = {1:"a",2:"b",3:"c",4:"d",5:"e",6:"f",7:"g",8:"h"}
    n = ["1","2","3","4","5","6","7","8"]
    n1 = [1,2,3,4,5,6,7,8]
    ans = []
    ansDict = {}
    tiles = []
    for i in f:
        for j in n:
            tiles.append(i+j)
    for pos in tiles:
        tempMoves = []
        xcurr = f1[pos[0]]
        ycurr = int(pos[1])
        for move in moves:
            xtemp = xcurr + move[0]
            ytemp = ycurr + move[1]
            if xtemp>=1 and xtemp<=8 and ytemp>=1 and ytemp<=8:
                stemp = f2[xtemp] + str(ytemp)
                stemp = pos+stemp
                if stemp in tempMoves:
                    print("wonder how this slipped through")
                else:
                    tempMoves.append(stemp)
        ans = ans + tempMoves
    # print(len(ans))
    for i,j in enumerate(ans):
        ansDict[j] = i

    return ans, ansDict


def makeActionsOLD():
    ans = []
    ansDict = {}
    tiles = []
    for i in ["a","b","c","d","e","f","g","h"]:
        for j in ["1","2","3","4","5","6","7","8"]:
            tiles.append(i+j)
    #can make WAY better gen, reduce min 25% of action space
    for i in tiles:
        for j in tiles:
            if i!=j:
                ans.append(i+j)
    for i,j in enumerate(ans):
        ansDict[j] = i
    
    return np.array(ans), ansDict
class ChessEnv(gym.Env):

    metadata = {"render.modes": ["human"]}
    def __init__(self, fen=None, white=True):
        super(ChessEnv, self).__init__()
        self.board = chess.Board(fen=fen) if fen else chess.Board()
        self.html_server = HTMLServer(board=self.board)
        self.html_server.start()
        self.stockfish = Stockfish(path="stockfish_15.1/stockfish.exe", depth=15)
        self.stockfish.update_engine_parameters({"Hash":32768, "UCI_Elo":3000, "Threads":8})
        self.stockfish.set_fen_position(self.board.fen())
        if white:
            self.white=True
            self.black=False
        else:
            self.black=True
            self.white=False
        self.moves, self.movesDict = makeActions()
        spaceBuild = []
        for i in range(64):
            spaceBuild.append(13)
       
        self.observation_space = spaces.MultiDiscrete(spaceBuild)
        
        self.action_space = spaces.Discrete(len(self.moves))
        self.stepcnt=0
        self.stockfishThink = 10
        self.stepsBeyondTerm = None

    def reset(self, fen=None):
        self.board = chess.Board(fen=fen) if fen else chess.Board()
        self.html_server.update(chess.svg.board(board=self.board))
        self.stepcnt=0
        return fenArr(self.board.fen())
        
    # chess.svg??
    def render(self):
        self.html_server.driver.refresh()


    # push uci for now for discrete action space... need to thnik if I want pgn or uci for final pipeline
    def step(self, action):
        self.stepcnt = self.stepcnt +1
        #print("new step",self.stepcnt)
        obs = fenArr(self.board.fen())
        done = False
        info = {}
        reward = 1
        # stockfish white
        if self.white:
            
            
            self.board.push_san(self.stockfishMove())
         

            if self.board.is_checkmate():
                reward = -10000
                done = True
                obs = fenArr(self.board.fen())
                return obs, reward, done, info
            elif self.board.is_check():
                reward = -5000
                done = True
                obs = fenArr(self.board.fen())
                return obs, reward, done, info
            
            m = chess.Move.from_uci(self.moves[action])
            # mm=self.board.legal_moves.__iter__()
            # m = next(mm)
            if m in self.board.legal_moves:

                self.board.push(m)
                reward = 100+reward
            else:
                done = True
                reward = -100000
                return obs, reward, done, info
            if self.board.is_checkmate():
                reward = 10000+reward
                done = True
                obs = fenArr(self.board.fen())
                return obs, reward, done, info
            elif self.board.is_check():
                reward = 5000+reward
                done = True
                obs = fenArr(self.board.fen())
                return obs, reward, done, info
            else:
                temp = self.board.pop()
                if self.board.is_capture(temp):
                    reward = 500+reward
                self.board.push(temp)


        if self.black:
            if self.board.is_checkmate():
                reward = -10000
                done = True
                obs = fenArr(self.board.fen())
                return obs, reward, done, info
            elif self.board.is_check():
                reward = -5000
                done = True
                obs = fenArr(self.board.fen())
                return obs, reward, done, info
            
            
            m = chess.Move.from_uci(self.moves[action])
            if m in self.board.legal_moves:

                self.board.push(m)
                reward = 100+reward
            else:
                done = True
                reward = -100000
                return obs, reward, done, info
            
            if self.board.is_checkmate():
                reward = 10000+reward
                done = True
                obs = fenArr(self.board.fen())
                return obs, reward, done, info
            elif self.board.is_check():
                reward = 5000+reward
                done = True
                obs = fenArr(self.board.fen())
                return obs, reward, done, info
            else:
                temp = self.board.pop()
                if self.board.is_capture(temp):
                    reward = 500+reward
                self.board.push(temp)
            
            self.board.push_san(self.stockfishMove())
        obs=fenArr(self.board.fen())
        return obs, reward, done, info
            
    def stockfishMove(self):
        self.stockfish.set_fen_position(self.board.fen())
        return self.stockfish.get_best_move(self.stockfishThink)

    def stepOLD(self, action):
        obs = None
        #low reward for time, trying to be on the attack
        reward = 10
        done = False
        info = {}


        # add stockfish code for its best move

        if self.board.is_checkmate():
            reward = -10000
            done = True
            obs = fenArr(self.board.fen())
            return obs, reward, done, info
        #not a valid moves
        try:
            self.board.push_uci(action)
        except Exception as e:
            done = True
            reward = -10000
            return obs, reward, done, info

        if self.board.is_checkmate():
            reward = 10000
            done = True
        elif self.board.is_check():
            reward = 5000
        else:
            temp = self.board.pop()
            if self.board.is_capture(temp):
                reward = 500
            self.board.push_uci(action)
        obs = fenArr(self.board.fen())



        #thats how cartpole does it......
        info = {}

        
        return obs, reward, done, info
pieces = {" ":0, "p":1, "r":2, "b":3, "n":4, "q":5, "k":6, "P":7, "R":8, "B":9, "N":10, "Q":11, "K":12} 
def fenArr(fen:str):
    lines = fen.split(" ")
    lines = lines[0]
    lines = lines.split("/")
    ans = []
    
    for i in lines:
        for c in i:
            if c in ["1","2","3","4","5","6","7","8"]:
                for x in range(int(c)):
                    ans.append(0)
            else:
                ans.append(pieces[c])
    # print(ans)
    # print(len(ans))
    return np.array(ans)

import enum
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
        self.httpd.html_content = self.strBuild(chess.svg.board(board))
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
    
    return ans, ansDict
class ChessEnv(gym.Env):

    metadata = {"render.modes": ["human"]}
    def __init__(self, fen=None):
        super(ChessEnv, self).__init__()
        self.board = chess.Board(fen=fen) if fen else chess.Board()
        self.html_server = HTMLServer(board=self.board)
        self.html_server.start()
        
        pass

    def reset(self, fen=None):
        self.board = chess.Board(fen=fen) if fen else chess.Board()
        self.html_server.update(chess.svg.board(board=self.board))
        pass
    # chess.svg??
    def render(self):
        self.html_server.driver.refresh()


    # push uci for now for discrete action space... need to thnik if I want pgn or uci for final pipeline
    def step(self, action):
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
                reward = 1000
            self.board.push_uci(action)
        obs = fenArr(self.board.fen())



        #thats how cartpole does it......
        info = {}

        
        return obs, reward, done, info
pieces = {"p":1, "r":2, "b":3, "n":4, "q":5, "k":6, "P":7, "R":8, "B":9, "N":10, "Q":11, "K":12} 
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
    return ans

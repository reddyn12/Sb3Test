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
    def __init__(self, port=8000):
        self.port = port
        self.html_content = self.strBuild(chess.svg.board(chess.Board()))
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
    def update(self, new_html_content):
        self.httpd.html_content = self.strBuild(new_html_content)
        self.driver.refresh()



def display_board(board):
    board_svg = chess.svg.board(board=board)
    with open("board.svg", "w") as f:
        f.write(board_svg)
    print("Chess board displayed!")


# Example usage:
board = chess.Board()
board.push_san("b4")
# display_board(board)
board_svg = chess.svg.board(board=board)
html_server = HTMLServer()
html_server.start()
time.sleep(1)

html_server.update(board_svg)
time.sleep(2)
board.push_san("e6")
board_svg = chess.svg.board(board=board)
html_server.update(board_svg)
time.sleep(2)

board.push_san("c3")
board_svg = chess.svg.board(board=board)
html_server.update(board_svg)
time.sleep(2)

board.push_san("b6")
board_svg = chess.svg.board(board=board)
html_server.update(board_svg)
time.sleep(2)

board.push_san("c4")
board_svg = chess.svg.board(board=board)
html_server.update(board_svg)
time.sleep(2)

board.push_san("a5")
board_svg = chess.svg.board(board=board)
html_server.update(board_svg)
time.sleep(2)
html_server.stop()

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
        self.html_server = HTMLServer()
        self.html_server.start()
        
        pass

    def reset(self, fen=None):
        self.board = chess.Board(fen=fen) if fen else chess.Board()
        self.html_server.update(chess.svg.board(board=board))
        pass
    # chess.svg??
    def render(self):
        self.html_server.driver.refresh()


    # push uci for now for discrete action space... need to thnik if I want pgn or uci for final pipeline
    def step(self, action):
        obs = None
        reward = None
        done = None
        info = None
        #not a valid moves
        try:
            self.board.push_uci(action)
        except Exception as e:
            done = True
            reward = -10000

        
        return obs, reward, done, info
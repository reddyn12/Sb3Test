# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello():
#     b = open("board.svg","r")
#     t = b.read()
#     return t

# if __name__ == "__main__":
#     app.run()


from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('update_string')
def update_string(message):
    emit('new_string', message, broadcast=True)

@app.route("/")
def index():
    return '''
        <html>
        <head>
            <script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/2.3.0/socket.io.js"></script>
            <script>
                var socket = io.connect('http://' + document.domain + ':' + location.port);
                socket.on('connect', function() {
                    socket.emit('update_string', {data: 'Hello World'});
                });
                socket.on('new_string', function(data) {
                    document.body.innerHTML = data.data;
                });
            </script>
        </head>
        <body>
        </body>
        </html>
    '''

if __name__ == "__main__":
    socketio.run(app)
from flask import Flask, render_template
from flask_socketio import SocketIO
from src.security.crypto import CryptoManager
from src.routes.message_routes import MessageRoutes
from src.routes.handshake_routes import HandshakeRoutes
from src.config import PORT, DEBUG
import argparse

# configura o parser de argumentos
parser = argparse.ArgumentParser(description='cliente de chat')
parser.add_argument('--usuario', type=str, default='anônimo', help='nome do usuário')
args = parser.parse_args()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# inicializa o gerenciador de criptografia
crypto_manager = CryptoManager()
crypto_manager.generate_keys()

# inicializa as rotas
message_routes = MessageRoutes(socketio, crypto_manager, usuario=args.usuario)
handshake_routes = HandshakeRoutes(crypto_manager)

@app.route('/')
def index():
    print(f"acesso à página inicial detectado - usuário: {args.usuario}")
    return render_template('index.html', usuario=args.usuario)

@socketio.on('connect')
def handle_connect():
    print(f"cliente conectado via websocket - usuário: {args.usuario}")
    if not crypto_manager.handshake_done:
        handshake_routes.initial_handshake()

@app.route('/handshake', methods=['POST'])
def handshake():
    return handshake_routes.handle_handshake()

@app.route('/enviar_mensagem', methods=['POST'])
def enviar_mensagem():
    return message_routes.send_message()

@app.route('/send_message', methods=['POST'])
def receive_message():
    return message_routes.receive_message()

if __name__ == '__main__':
    print(f"iniciando servidor para usuário: {args.usuario}")
    socketio.run(app, port=PORT, debug=DEBUG) 
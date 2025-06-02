from flask import jsonify, request
import requests
from ..config import REQUEST_TIMEOUT
from datetime import datetime

class MessageRoutes:
    def __init__(self, socketio, crypto_manager, usuario='anônimo'):
        self.socketio = socketio
        self.crypto = crypto_manager
        self.usuario = usuario

    def send_message(self):
        dados = request.get_json()
        mensagem = dados['mensagem']
        
        # criptografa a mensagem usando RSA
        mensagem_criptografada = self.crypto.encrypt_message(mensagem)
        mac = self.crypto.create_mac(mensagem)
        
        # emite para o frontend do remetente (mensagem original)
        self.socketio.emit('mensagem', {
            'texto': mensagem,
            'tipo': 'enviada',
            'usuario': self.usuario,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
        target_url = 'http://127.0.0.1:5001/receive_message'

        try:
            response = requests.post(
                target_url,
                json={
                    'mensagem': mensagem_criptografada,  # envia mensagem criptografada
                    'mac': mac,
                    'usuario': self.usuario
                },
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                return jsonify({'status': 'ok'})
            else:
                print(f"erro: falha ao enviar mensagem para {target_url}. status: {response.status_code}, resposta: {response.text}")
                self.socketio.emit('mensagem_erro', {'texto': mensagem, 'erro': 'falha ao encaminhar para o outro servidor'})
                return jsonify({'erro': 'falha ao enviar mensagem para outro servidor'}), response.status_code
        except requests.exceptions.Timeout:
            print(f"erro: timeout ao enviar mensagem para {target_url}")
            self.socketio.emit('mensagem_erro', {'texto': mensagem, 'erro': 'timeout ao encaminhar mensagem'})
            return jsonify({'erro': 'timeout ao conectar ao outro servidor'}), 408
        except requests.exceptions.RequestException as e:
            print(f"erro: exceção ao enviar mensagem para {target_url}: {e}")
            self.socketio.emit('mensagem_erro', {'texto': mensagem, 'erro': f'erro de rede: {e}'})
            return jsonify({'erro': f'falha ao conectar ao outro servidor: {e}'}), 500

    def receive_message(self):
        dados = request.get_json()
        mensagem_criptografada = dados['mensagem']
        mac_recebido = dados['mac']
        usuario = dados.get('usuario', 'anônimo')

        try:
            # descriptografa a mensagem usando RSA
            mensagem = self.crypto.decrypt_message(mensagem_criptografada)
            
            if not self.crypto.verify_mac(mensagem, mac_recebido):
                print("erro: mac inválido recebido.")
                return jsonify({'erro': 'mensagem inválida'}), 400

            self.socketio.emit('mensagem', {
                'texto': mensagem,
                'tipo': 'recebida',
                'usuario': usuario,
                'timestamp': datetime.now().strftime('%H:%M')
            })

            return jsonify({'status': 'ok'})
        except Exception as e:
            print(f"erro: exceção em receive_message: {str(e)}")
            return jsonify({'erro': str(e)}), 400 
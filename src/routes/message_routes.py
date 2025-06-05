from flask import jsonify, request
import requests
from ..config import REQUEST_TIMEOUT, DESTINATION_PORT
from datetime import datetime

class MessageRoutes:
    def __init__(self, socketio, crypto_manager, usuario='anônimo'):
        self.socketio = socketio
        self.crypto = crypto_manager
        self.usuario = usuario

    def send_message(self):
        dados = request.get_json()
        mensagem = dados['mensagem']
        
        try:
            # verifica se o handshake foi feito
            if not self.crypto.handshake_done:
                print("erro: handshake não realizado")
                self.socketio.emit('mensagem_erro', {'texto': mensagem, 'erro': 'handshake não realizado'})
                return jsonify({'erro': 'handshake não realizado'}), 400
                
            # verifica se temos a chave pública do outro lado
            if not self.crypto.other_public_key or not self.crypto.other_n_modulus:
                print("erro: chave pública do outro lado não configurada")
                self.socketio.emit('mensagem_erro', {'texto': mensagem, 'erro': 'chave pública não configurada'})
                return jsonify({'erro': 'chave pública não configurada'}), 400
            
            # criptografa a mensagem usando rsa
            mensagem_criptografada = self.crypto.encrypt_message(mensagem)
            
            # cria assinatura digital da mensagem
            assinatura = self.crypto.sign_message(mensagem)
            
            # emite para o frontend do remetente (mensagem original)
            self.socketio.emit('mensagem', {
                'texto': mensagem,
                'tipo': 'enviada',
                'usuario': self.usuario,
                'timestamp': datetime.now().strftime('%H:%M')
            })
            
            target_url = f'http://127.0.0.1:{DESTINATION_PORT}/receive_message'

            response = requests.post(
                target_url,
                json={
                    'mensagem': mensagem_criptografada,  # envia mensagem criptografada
                    'assinatura': assinatura,  # envia assinatura digital
                    'usuario': self.usuario
                },
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                return jsonify({'status': 'ok'})
            else:
                self.socketio.emit('mensagem_erro', {'texto': mensagem, 'erro': 'falha ao encaminhar para o outro servidor'})
                return jsonify({'erro': 'falha ao enviar mensagem para outro servidor'}), response.status_code
        except Exception as e:
            print(f"erro ao processar mensagem: {str(e)}")
            self.socketio.emit('mensagem_erro', {'texto': mensagem, 'erro': f'erro ao processar mensagem: {str(e)}'})
            return jsonify({'erro': str(e)}), 500

    def receive_message(self):
        dados = request.get_json()
        mensagem_criptografada = dados['mensagem']
        assinatura = dados['assinatura']
        usuario = dados.get('usuario', 'anônimo')

        try:
            # verifica se o handshake foi feito
            if not self.crypto.handshake_done:
                print("erro: handshake não realizado")
                return jsonify({'erro': 'handshake não realizado'}), 400
                
            # verifica se temos a chave pública do outro lado
            if not self.crypto.other_public_key or not self.crypto.other_n_modulus:
                print("erro: chave pública do outro lado não configurada")
                return jsonify({'erro': 'chave pública não configurada'}), 400
            
            # descriptografa a mensagem usando rsa
            mensagem = self.crypto.decrypt_message(mensagem_criptografada)
            
            # verifica a assinatura digital
            if not self.crypto.verify_signature(mensagem, assinatura):
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
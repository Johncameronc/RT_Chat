from flask import jsonify, request
import time
import requests
from ..config import MAX_HANDSHAKE_ATTEMPTS, HANDSHAKE_RETRY_DELAY

class HandshakeRoutes:
    def __init__(self, crypto_manager):
        self.crypto = crypto_manager

    def initial_handshake(self):
        if self.crypto.handshake_done:
            print("handshake já foi realizado anteriormente")
            return
            
        print("iniciando tentativa de handshake...")
        tentativa = 0
        
        while tentativa < MAX_HANDSHAKE_ATTEMPTS:
            try:
                print(f"tentativa {tentativa + 1} de handshake...")
                # garante que a chave pública está em formato pem
                public_key = self.crypto.get_public_key_bytes()
                
                response = requests.post(
                    'http://127.0.0.1:5001/handshake',
                    json={
                        'public_key': public_key
                    }
                )
                
                if response.status_code == 200:
                    dados = response.json()
                    # decodifica a chave pública recebida
                    self.crypto.set_other_public_key(dados['public_key'])
                    print("handshake realizado com sucesso!")
                    self.crypto.handshake_done = True
                    return
                else:
                    print(f"tentativa {tentativa + 1}: erro ao fazer handshake:", response.json().get('erro', 'erro desconhecido'))
            except Exception as e:
                print(f"tentativa {tentativa + 1}: erro ao fazer handshake:", str(e))
            
            tentativa += 1
            if tentativa < MAX_HANDSHAKE_ATTEMPTS:
                print("tentando novamente em 1 segundo...")
                time.sleep(HANDSHAKE_RETRY_DELAY)
        
        print("não foi possível fazer o handshake após várias tentativas")

    def handle_handshake(self):
        dados = request.get_json()
        
        if not dados or 'public_key' not in dados:
            return jsonify({'erro': 'dados incompletos'}), 400
            
        try:
            # decodifica a chave pública recebida
            self.crypto.set_other_public_key(dados['public_key'])
            
            # envia a resposta com a chave pública codificada
            return jsonify({
                'public_key': self.crypto.get_public_key_bytes()
            })
        except Exception as e:
            print(f"erro no handle_handshake: {str(e)}")
            return jsonify({'erro': str(e)}), 400 
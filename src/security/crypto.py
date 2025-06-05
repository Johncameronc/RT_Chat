from ..security.rsa import generate_keys, encrypt, decrypt, sign_message, verify_signature
import base64

class CryptoManager:
    def __init__(self):
        self.public_key = None
        self.private_key = None
        self.n_modulus = None
        self.other_public_key = None
        self.other_n_modulus = None
        self.handshake_done = False

    def generate_keys(self):
        # gera chaves rsa
        self.public_key, self.private_key, self.n_modulus = generate_keys()

    def encrypt_message(self, message):
        try:
            # criptografa a mensagem usando rsa
            message_bytes = message.encode('utf-8')
            encrypted_values = encrypt(message_bytes, self.other_public_key, self.other_n_modulus)
            
            # converte cada valor para string e junta com vírgula
            encrypted_str = ','.join(str(v) for v in encrypted_values)
            
            # converte para base64 para transmissão
            return base64.b64encode(encrypted_str.encode('utf-8')).decode('utf-8')
        except Exception as e:
            print(f"erro ao criptografar mensagem: {str(e)}")
            raise

    def decrypt_message(self, encrypted_message):
        try:
            # decodifica da base64
            encrypted_str = base64.b64decode(encrypted_message).decode('utf-8')
            
            # converte a string de volta para lista de inteiros
            encrypted_values = [int(v) for v in encrypted_str.split(',')]
            
            # descriptografa usando rsa
            decrypted_bytes = decrypt(encrypted_values, self.private_key, self.n_modulus)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            print(f"erro ao descriptografar mensagem: {str(e)}")
            raise

    def sign_message(self, message):
        try:
            # cria assinatura digital usando rsa
            signature_int = sign_message(message, self.private_key, self.n_modulus)
            # converte para string e depois para base64 para transmissão
            signature_str = str(signature_int)
            return base64.b64encode(signature_str.encode('utf-8')).decode('utf-8')
        except Exception as e:
            print(f"erro ao assinar mensagem: {str(e)}")
            raise

    def verify_signature(self, message, signature):
        try:
            # decodifica da base64
            signature_str = base64.b64decode(signature).decode('utf-8')
            # converte de volta para inteiro
            signature_int = int(signature_str)
            # verifica a assinatura usando rsa
            return verify_signature(message, signature_int, self.other_public_key, self.other_n_modulus)
        except Exception as e:
            print(f"erro ao verificar assinatura: {str(e)}")
            return False

    def get_public_key_bytes(self):
        try:
            # retorna chave pública e módulo n como string
            return f"{self.public_key}:{self.n_modulus}"
        except Exception as e:
            print(f"erro ao obter chave pública: {str(e)}")
            raise

    def set_other_public_key(self, public_key_str):
        try:
            # separa chave pública e módulo n
            public_key_str, n_modulus_str = public_key_str.split(':')
            self.other_public_key = int(public_key_str)
            self.other_n_modulus = int(n_modulus_str)
        except Exception as e:
            print(f"erro ao definir chave pública: {str(e)}")
            raise 
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
import os
from ..config import KEY_SIZE, PUBLIC_EXPONENT

class CryptoManager:
    def __init__(self):
        self.private_key = None
        self.other_public_key = None
        self.handshake_done = False

    def generate_keys(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=PUBLIC_EXPONENT,
            key_size=KEY_SIZE
        )

    def encrypt_message(self, message):
        try:
            # criptografa a mensagem usando a chave pública do destinatário
            encrypted_message = self.other_public_key.encrypt(
                message.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return base64.b64encode(encrypted_message).decode('utf-8')
        except Exception as e:
            print(f"erro ao criptografar mensagem: {str(e)}")
            raise

    def decrypt_message(self, encrypted_message):
        try:
            # decodifica a mensagem criptografada
            encrypted_bytes = base64.b64decode(encrypted_message)
            # descriptografa usando a chave privada
            decrypted_message = self.private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted_message.decode('utf-8')
        except Exception as e:
            print(f"erro ao descriptografar mensagem: {str(e)}")
            raise

    def sign_message(self, message):
        try:
            # cria assinatura digital usando a chave privada
            signature = self.private_key.sign(
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            print(f"erro ao assinar mensagem: {str(e)}")
            raise

    def verify_signature(self, message, signature):
        try:
            # verifica a assinatura usando a chave pública do remetente
            signature_bytes = base64.b64decode(signature)
            self.other_public_key.verify(
                signature_bytes,
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"erro ao verificar assinatura: {str(e)}")
            return False

    def get_public_key_bytes(self):
        try:
            return self.private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
        except Exception as e:
            print(f"erro ao obter chave pública: {str(e)}")
            raise

    def set_other_public_key(self, public_key_bytes):
        try:
            if isinstance(public_key_bytes, str):
                public_key_bytes = public_key_bytes.encode('utf-8')
            self.other_public_key = serialization.load_pem_public_key(public_key_bytes)
        except Exception as e:
            print(f"erro ao definir chave pública: {str(e)}")
            raise 
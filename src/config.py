import os

# configurações do servidor
HOST = '127.0.0.1'
PORT = 5000
DEBUG = True

# configurações de segurança
KEY_SIZE = 2048
PUBLIC_EXPONENT = 65537
SHARED_KEY_SIZE = 32

# configurações de timeout
REQUEST_TIMEOUT = 5
MAX_HANDSHAKE_ATTEMPTS = 5
HANDSHAKE_RETRY_DELAY = 1 
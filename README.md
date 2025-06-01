# Real Time Chat

Uma aplicação de chat peer-to-peer baseada em Python, com mensagens em tempo real e foco em segurança através de handshake criptográfico, criptografia de mensagens e autenticação de mensagens. Este projeto utiliza Flask e Flask-SocketIO para o servidor web e comunicação WebSocket.

## Funcionalidades

* **Mensagens em Tempo Real:** Troca instantânea de mensagens entre dois clientes conectados usando WebSockets (Flask-SocketIO).
* **Comunicação tipo P2P:** Projetado para comunicação direta entre duas instâncias da aplicação.
* **Identificação de Usuário:** Usuários podem especificar um nome de usuário via argumento de linha de comando.
* **Handshake Seguro:** Utiliza criptografia assimétrica RSA para a troca inicial de uma chave secreta compartilhada.
* **Criptografia de Mensagens (Confidencialidade):** As mensagens são criptografadas usando RSA com a chave pública do destinatário antes da transmissão.
* **Autenticação de Mensagens (Integridade e Autenticidade):** Emprega HMAC-SHA256 para garantir a integridade e autenticidade da mensagem original (texto plano) usando a chave secreta compartilhada.
* **Geração Dinâmica de Chaves:** Pares de chaves RSA e chaves compartilhadas são gerados em memória para cada sessão.
* **Interface Web Moderna:** Uma interface de usuário simples e limpa para o chat (detalhes em `templates/index.html`).

## Estrutura do Projeto

```
.
├── src/
│   ├── security/
│   │   └── crypto.py           # Lida com operações criptográficas (RSA, HMAC)
│   ├── routes/
│   │   ├── handshake_routes.py # Gerencia a lógica do handshake seguro
│   │   └── message_routes.py   # Gerencia o envio e recebimento de mensagens
│   └── config.py               # Configuração (portas, parâmetros cripto)
├── client.py                   # Aplicação Flask principal, manipulação de WebSocket
├── keys_manager.py             # Script utilitário para gerar e salvar chaves RSA
├── requirements.txt            # Dependências Python
├── templates/
│   └── index.html              # Template HTML para a interface do chat
└── .env                        # Armazena chaves se geradas pelo keys_manager.py
```

## Pré-requisitos

* Python 3.7+
* pip (instalador de pacotes Python)

## Configuração e Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd <nome-do-repositorio>
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    # No Windows
    # venv\Scripts\activate
    # No macOS/Linux
    # source venv/bin/activate
    ```

3.  **Instale as dependências:**
    Seu arquivo `requirements.txt` deve estar na raiz do projeto com o seguinte conteúdo:
    ```txt
    flask==3.0.2
    cryptography==42.0.5
    python-dotenv==1.0.1
    requests==2.31.0
    PyJWT==2.8.0
    flask-socketio==5.3.6
    ```
    Então execute:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuração (`src/config.py`):**
    Certifique-se de ter um arquivo `src/config.py`. Este arquivo deve definir configurações como a porta para a instância atual do servidor e parâmetros criptográficos. Por exemplo:
    ```python
    # src/config.py
    HOST = '127.0.0.1'
    PORT = 5001 # Porta para ESTA instância do servidor (ex: Cliente A)
    # Nota: O outro cliente (Cliente B) deve rodar na porta 5000
    # conforme URLs fixas em handshake_routes.py e message_routes.py

    DEBUG = True
    KEY_SIZE = 2048
    PUBLIC_EXPONENT = 65537
    SHARED_KEY_SIZE = 32
    MAX_HANDSHAKE_ATTEMPTS = 5
    HANDSHAKE_RETRY_DELAY = 1 # segundos
    REQUEST_TIMEOUT = 5 # segundos
    ```
    *Importante:* A implementação atual em `handshake_routes.py` e `message_routes.py` fixa a URL de destino para o *outro* cliente como `http://127.0.0.1:5000` (em `message_routes.py`) ou `http://127.0.0.1:5001` (em `handshake_routes.py`, assumindo que o iniciador do handshake não está na 5000). Isso significa que uma de suas instâncias de chat **deve** ser configurada para rodar na porta esperada pela outra. Ajuste as URLs fixas ou torne-as configuráveis para maior flexibilidade.

## Como Executar

Esta aplicação é projetada para que duas instâncias se comuniquem.

**Instância 1 (Cliente A - Exemplo: Rodando na Porta 5000):**

1.  Modifique `src/config.py` para definir `PORT = 5000`.
2.  Ajuste a `target_url` em `src/routes/message_routes.py` da *outra instância* (Cliente A) para `http://127.0.0.1:5001/send_message`.
3.  Ajuste a URL de handshake em `src/routes/handshake_routes.py` da *outra instância* (Cliente A) para `http://127.0.0.1:5001/handshake`.
4.  Abra um terminal, navegue até a raiz do projeto e execute:
    ```bash
    python client.py --usuario "UserA"
    ```
    (Substitua "UserA" pelo nome de usuário desejado).

**Instância 2 (Cliente B - Exemplo: Rodando na Porta 5001):**

1.  Modifique `src/config.py` para definir `PORT = 5001`.
2.  Ajuste a `target_url` em `src/routes/message_routes.py` desta instância (Cliente A) para `http://127.0.0.1:5000/send_message` (para enviar ao Cliente A).
3.  Ajuste a URL de handshake em `src/routes/handshake_routes.py` desta instância (Cliente A) para `http://127.0.0.1:5000/handshake` (para iniciar com o Cliente A).
4.  Abra um *segundo* terminal, navegue até a raiz do projeto e execute:
    ```bash
    python client.py --usuario "UserB"
    ```
    (Substitua "UserB" pelo nome de usuário desejado).

**Operação:**

* A instância que você designar como iniciadora (ex: Cliente A) tentará iniciar um handshake com a outra instância (ex: Cliente B na porta 5001) quando um usuário se conectar à sua interface web.
* Uma vez que o handshake seja bem-sucedido, ambos os usuários podem abrir `http://127.0.0.1:<PORTA_DE_SUA_INSTANCIA>` (ex: `http://127.0.0.1:500)` para UserA e `http://127.0.0.1:5001` para UserB) em seus navegadores para começar a conversar.
* As mensagens enviadas por UserA serão roteadas através de seu backend para o backend de UserB, e vice-versa.

## Tecnologias Utilizadas

* **Python:** Linguagem de programação principal.
* **Flask:** Micro framework web para lidar com requisições HTTP.
* **Flask-SocketIO:** Para comunicação bidirecional em tempo real usando WebSockets.
* **Cryptography:** Biblioteca Python para operações criptográficas (RSA, HMAC).
* **Requests:** Para fazer requisições HTTP entre instâncias do servidor.
* **HTML, CSS, JavaScript:** Para a interface do chat no frontend.

## Aspectos de Segurança

* **Troca de Chaves RSA:** Criptografia assimétrica (RSA) é usada durante o handshake inicial para estabelecer de forma segura uma chave secreta compartilhada entre os dois clientes.
* **Criptografia de Mensagens (Confidencialidade):** As mensagens são criptografadas usando a chave pública RSA do destinatário (com padding OAEP) antes de serem transmitidas. Isso garante que apenas o destinatário com a chave privada correspondente possa ler o conteúdo da mensagem.
* **HMAC (Hash-based Message Authentication Code):** A chave secreta compartilhada é então usada com HMAC-SHA256 para gerar um MAC para cada mensagem original (texto plano). Este MAC é enviado junto com a mensagem criptografada. Ao receber, a mensagem é descriptografada e o MAC é verificado contra o texto plano resultante. Isso garante:
    * **Integridade:** A mensagem original não foi adulterada durante o trânsito.
    * **Autenticidade:** A mensagem genuinamente originou-se da outra parte que também conhece a chave secreta compartilhada.
* **Chaves Efêmeras:** Por padrão, as chaves criptográficas são geradas em memória para cada sessão, aumentando a segurança por não depender de chaves armazenadas persistentemente que poderiam ser comprometidas.

**⚠️ Nota Importante sobre Criptografia RSA Direta de Mensagens:**
A criptografia RSA, como implementada diretamente para as mensagens neste projeto, tem uma **limitação significativa no tamanho dos dados** que pode criptografar (aproximadamente 190 bytes com uma chave de 2048 bits e padding OAEP/SHA256). Mensagens de chat frequentemente excedem este limite, o que causaria falhas.

Para uma aplicação de chat robusta e prática, a abordagem recomendada é a **criptografia híbrida**:
1.  Gere uma chave simétrica aleatória e temporária (ex: AES) para cada mensagem.
2.  Criptografe a mensagem de chat usando esta chave simétrica temporária.
3.  Criptografe a chave simétrica temporária usando a chave pública RSA do destinatário.
4.  Envie a [chave simétrica criptografada com RSA] + [mensagem criptografada com a chave simétrica].
Esta abordagem combina a eficiência da criptografia simétrica para dados longos com a segurança da criptografia assimétrica para a troca de chaves.

---

*Este README foi gerado com base nos arquivos de projeto fornecidos. Pode ser necessário ajustar as configurações de porta ou a descrição da comunicação entre clientes se sua configuração diferir das suposições feitas (particularmente em relação às portas de destino fixas).*

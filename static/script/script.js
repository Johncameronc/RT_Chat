const socket = io();
const mensagensDiv = document.getElementById('mensagens');
const formulario = document.getElementById('formulario');
const inputMensagem = document.getElementById('mensagem');

// função para salvar mensagens no localStorage
function salvarMensagens(mensagens) {
    localStorage.setItem('chat_mensagens', JSON.stringify(mensagens));
}

// função para carregar mensagens do localStorage
function carregarMensagens() {
    const mensagens = JSON.parse(localStorage.getItem('chat_mensagens') || '[]');
    mensagens.forEach(dados => {
        const divMensagemPrincipal = document.createElement('div');
        divMensagemPrincipal.className = `mensagem ${dados.tipo}`;

        if (dados.usuario && dados.usuario.trim() !== "") {
            const usuarioSpan = document.createElement('span');
            usuarioSpan.className = 'sender';
            usuarioSpan.textContent = dados.usuario;
            divMensagemPrincipal.appendChild(usuarioSpan);
        }

        const messageBodyDiv = document.createElement('div');
        messageBodyDiv.className = 'message-body';

        const textSpan = document.createElement('span');
        textSpan.className = 'text';
        textSpan.textContent = dados.texto;
        messageBodyDiv.appendChild(textSpan);

        if (dados.timestamp) {
            const timestampSpan = document.createElement('span');
            timestampSpan.className = 'timestamp';
            timestampSpan.textContent = dados.timestamp;
            messageBodyDiv.appendChild(timestampSpan);
        }
        
        divMensagemPrincipal.appendChild(messageBodyDiv);
        mensagensDiv.appendChild(divMensagemPrincipal);
    });
    mensagensDiv.scrollTop = mensagensDiv.scrollHeight;
}

// carrega mensagens ao iniciar
carregarMensagens();

socket.on('mensagem', function(dados) {
    const divMensagemPrincipal = document.createElement('div');
    divMensagemPrincipal.className = `mensagem ${dados.tipo}`;
    divMensagemPrincipal.classList.add('new-message-animation');

    if (dados.usuario && dados.usuario.trim() !== "") {
        const usuarioSpan = document.createElement('span');
        usuarioSpan.className = 'sender';
        usuarioSpan.textContent = dados.usuario;
        divMensagemPrincipal.appendChild(usuarioSpan);
    }

    const messageBodyDiv = document.createElement('div');
    messageBodyDiv.className = 'message-body';

    const textSpan = document.createElement('span');
    textSpan.className = 'text';
    textSpan.textContent = dados.texto;
    messageBodyDiv.appendChild(textSpan);

    if (dados.timestamp) {
        const timestampSpan = document.createElement('span');
        timestampSpan.className = 'timestamp';
        timestampSpan.textContent = dados.timestamp;
        messageBodyDiv.appendChild(timestampSpan);
    }
    
    divMensagemPrincipal.appendChild(messageBodyDiv);
    mensagensDiv.appendChild(divMensagemPrincipal);
    mensagensDiv.scrollTop = mensagensDiv.scrollHeight;

    // salva mensagens no localStorage
    const mensagens = JSON.parse(localStorage.getItem('chat_mensagens') || '[]');
    mensagens.push(dados);
    salvarMensagens(mensagens);
});

// Enviar mensagem (código existente)
formulario.onsubmit = function(e) {
    e.preventDefault();
    const texto = inputMensagem.value.trim();
    if (texto) {
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mensagem: texto }) 
        })
        .catch(error => console.error('Erro ao enviar mensagem:', error));
        
        inputMensagem.value = '';
        inputMensagem.focus();
    }
}; 
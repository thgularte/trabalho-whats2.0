async function login() {
    const clientId = document.getElementById('client_id').value;
    const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: clientId })
    });
    const result = await response.json();
    if (result.success) {
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('chat-section').style.display = 'block';
    } else {
        alert('Login falhou');
    }
}

async function sendMessage() {
    const recipientId = document.getElementById('recipient_id').value;
    const message = document.getElementById('message').value;
    const response = await fetch('/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recipient_id: recipientId, message: message })
    });
    const result = await response.json();
    if (result.success) {
        alert('Mensagem enviada');
    } else {
        alert('Falha ao enviar mensagem');
    }
}

async function createGroup() {
    const members = document.getElementById('group_members').value.split(',').map(id => id.trim());
    const response = await fetch('/create_group', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ members: members })
    });
    const result = await response.json();
    if (result.success) {
        alert('Grupo criado com sucesso');
    } else {
        alert('Falha ao criar grupo');
    }
}

async function sendGroupMessage() {
    const groupId = document.getElementById('group_id').value;
    const message = document.getElementById('group_message').value;
    const response = await fetch('/send_group_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ group_id: groupId, message: message })
    });
    const result = await response.json();
    if (result.success) {
        alert('Mensagem enviada para o grupo');
    } else {
        alert('Falha ao enviar mensagem para o grupo');
    }
}

"""
Funções do cliente
- Registra-se 
- Se conectar
- Enviar mensagem 
- Criar grupo

Todas as funções do cliente, 
enviam um código pro servidor para que ele saiba qual função deve executar

"""

import socket

class Cliente:
    def __init__(self, host='localhost', port=8888):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)

    def registra_usuario(self):
        message = '01'
        self.client_socket.send(message.encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        print(f"Registro completado: {response}")

    def acessar_conta(self, client_id):
        message = '03' + client_id
        self.client_socket.send(message.encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        print(f"Conexão completada: {response}")

    def enviar_mensagem(self, src_id, dst_id, timestamp, data):
        message = f'05{src_id}{dst_id}{timestamp}{data}'
        self.client_socket.send(message.encode('utf-8'))
        print("Mensagem enviada.")

    def criar_grupo(self, criador_id, timestamp, members):
        message = f'10{criador_id}{timestamp}{"".join(members)}'
        self.client_socket.send(message.encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        print(f"Grupo criado: {response}")

    def enviar_mensagem_grupo(self, group_id, src_id, timestamp, data):
        message = f'11{group_id}{src_id}{timestamp}{data}'
        self.client_socket.send(message.encode('utf-8'))
        print("Mensagem de grupo enviada.")

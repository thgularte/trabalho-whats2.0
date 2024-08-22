import socket
import threading
import time
from datetime import datetime

class Servidor:
    def __init__(self, host='localhost', port=8888):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = {}
        self.mensagens_pendentes = {}  
        print("Servidor iniciado e aguardando conexões...")

    def iniciar(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Conectado com {addr}")
            threading.Thread(target=self.gerenciar_cliente, args=(client_socket,), daemon=True).start()

    def gerenciar_cliente(self, client_socket):
        while True:
            try:
                mensagem = client_socket.recv(1024).decode('utf-8')
                if not mensagem:
                    break
                self.processar_mensagem(mensagem, client_socket)
            except (socket.error, ConnectionError) as e:
                print(f"Erro de conexão: {e}")
                break
        client_socket.close()

    def processar_mensagem(self, mensagem, client_socket):
        tipo_mensagem = mensagem[:2]
        if tipo_mensagem == '01':  # Registro de usuário
            self.registrar_usuario(client_socket)
        elif tipo_mensagem == '03':  # Acesso à conta
            client_id = mensagem[2:]
            self.acessar_conta(client_socket, client_id)
        elif tipo_mensagem == '05':  # Enviar mensagem
            src_id = mensagem[2:15]
            dst_id = mensagem[15:28]
            timestamp = int(mensagem[28:38])
            data = mensagem[38:]
            self.enviar_mensagem(src_id, dst_id, timestamp, data)
        elif tipo_mensagem == '10':  # Criar grupo
            criador_id = mensagem[2:15]
            timestamp = int(mensagem[15:25])
            membros = mensagem[25:]
            self.criar_grupo(criador_id, timestamp, membros)
        elif tipo_mensagem == '11':  # Enviar mensagem de grupo
            group_id = mensagem[2:15]
            src_id = mensagem[15:28]
            timestamp = int(mensagem[28:38])
            data = mensagem[38:]
            self.enviar_mensagem_grupo(group_id, src_id, timestamp, data)
        else:
            print(f"Tipo de mensagem desconhecido: {tipo_mensagem}")

    def registrar_usuario(self, client_socket):
        response = 'Registro concluído com sucesso.'
        client_socket.send(f'01{response}'.encode('utf-8'))

    def acessar_conta(self, client_socket, client_id):
        if client_id not in self.clients:
            self.clients[client_id] = client_socket
            response = 'Acesso concedido.'
        else:
            response = 'ID já em uso.'
        client_socket.send(f'03{response}'.encode('utf-8'))

    def enviar_mensagem(self, src_id, dst_id, timestamp, data):
        mensagem = f'05{src_id}{dst_id}{timestamp}{data}'
        if dst_id in self.clients:
            dst_socket = self.clients[dst_id]
            try:
                dst_socket.send(mensagem.encode('utf-8'))
            except (socket.error, ConnectionError):
                # Se houver um erro ao enviar a mensagem, salve como pendente
                self.salvar_mensagem_pendente(dst_id, mensagem)
        else:
            # Se o destinatário não estiver conectado, salve a mensagem como pendente
            self.salvar_mensagem_pendente(dst_id, mensagem)

    def salvar_mensagem_pendente(self, client_id, mensagem):
        if client_id not in self.mensagens_pendentes:
            self.mensagens_pendentes[client_id] = []
        self.mensagens_pendentes[client_id].append(mensagem)

    def enviar_mensagem_pendente(self, mensagem, client_socket):
        try:
            client_socket.send(mensagem.encode('utf-8'))
        except (socket.error, ConnectionError):
            print("erro")
            pass  # Trate o erro de envio conforme necessário

    def criar_grupo(self, criador_id, timestamp, membros):
        group_id = f'GRP{int(time.time())}'
        response = f'{group_id}{timestamp}'
        client_socket = self.clients.get(criador_id)
        if client_socket:
            client_socket.send(f'10{response}'.encode('utf-8'))
        print(f'Grupo criado: {group_id}')

    def enviar_mensagem_grupo(self, group_id, src_id, timestamp, data):
        message = f'11{group_id}{src_id}{timestamp}{data}'
        # Aqui você deve ter uma lógica para enviar a mensagem para todos os membros do grupo
        print("Mensagem de grupo enviada.")

if __name__ == "__main__":
    servidor = Servidor()
    servidor.iniciar()

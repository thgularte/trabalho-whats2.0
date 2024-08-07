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
import threading

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
        if response.startswith('03'):
            src_id = response[2:15]
            dst_id = response[15:28]
            timestamp = response[28:38]
            data = response[38:219]
            self.interface_usuario(src_id, dst_id,timestamp,data)

    def interface_usuario(self,src_id, dst_id,timestamp,data):
        threading.Thread(target=self.receber_mensagens(src_id, dst_id,timestamp,data), daemon=True).start()
        while True:
            print("\nOpções:")
            print("1. Enviar mensagem")
            print("2. Sair")
            opcao = input("Opção: ")

            if opcao == '1':
                dst_id = input("Digite o ID do destinatário: ")
                mensagem = input("Digite a mensagem: ")
                self.enviar_mensagem(dst_id, mensagem)
            elif opcao == '2':
                print("Desconectando...")
                self.client_socket.close()
                break
            else:
                print("Opção inválida. Tente novamente.")

    def receber_mensagens(self, src_id,dst_id,timestamp,data):
        message = f'06{src_id}{dst_id}{timestamp}{data}'
        self.client_socket.send(message.encode('utf-8'))
        print("Tem mensagem recebida")

        
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

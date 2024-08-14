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
import time

class Cliente:
    def __init__(self, host='localhost', port=8888):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)

    def registra_usuario(self):
        message = '01'
        self.client_socket.send(message.encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        print(f"Registro completado: {response[2:]}")

    def acessar_conta(self, client_id):
        message = '03' + client_id
        self.client_socket.send(message.encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        if response.startswith('03'):
            threading.Thread(target=self.receber_mensagens, daemon=True).start()
            self.interface_usuario(client_id)

    def interface_usuario(self,client_id):
        while True:
            print("\nOpções:")
            print("1 - Enviar mensagem")
            print("2 - Mandar mensagem em grupo")
            print("3 - Criar um grupo")
            print("4 - Sair")
            opcao = input("Opção: ")

            if opcao == '1':
                dst_id = input("Digite o ID do destinatário: ")
                mensagem = input("Digite a mensagem: ")
                timestamp = time.time()
                self.enviar_mensagem(client_id, dst_id, timestamp, mensagem)
            elif opcao == '2':
                grupo_dst = input("Digite o id do grupo: ")
                mensagem = input("Digite a mensagem: ")
                self.enviar_mensagem_grupo(self, grupo_dst, client_id, timestamp, mensagem)
            elif opcao == '3': 
                opc = True
                membros = []
                print("Adicione os membros do grupo um por um. Digite 'sair' para terminar.")
                while opc: 
                    membro = input("Digite o id do membro: ")
                    if membro.lower() == 'sair':
                        opc = False
                    else:
                        membros.append(membro)
                self.criar_grupo(client_id, timestamp, membros)

            elif opcao == '4':
                print("Desconectando...")
                self.client_socket.close()
                break
            else:
                print("Opção inválida. Tente novamente.")
    
    def enviar_mensagem(self, src_id, dst_id, timestamp, data):
        message = f'05{src_id}{dst_id}{timestamp}{data}'
        self.client_socket.send(message.encode('utf-8'))
        print("Mensagem enviada.")

    def criar_grupo(self, criador_id, timestamp, members):
        message = f'10{criador_id}{timestamp}{"".join(members)}'
        self.client_socket.send(message.encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        print(f"Grupo criado: {response[2:]}")

    def enviar_mensagem_grupo(self, group_id, src_id, timestamp, data):
        message = f'11{group_id}{src_id}{timestamp}{data}'
        self.client_socket.send(message.encode('utf-8'))
        print("Mensagem de grupo enviada.")
        
    def receber_mensagens(self):
        while True:
            try:
                mensagem = self.client_socket.recv(1024).decode('utf-8')
                if mensagem.startswith('06'):
                    self.exibir_mensagem(mensagem)
                elif mensagem.startswith('08'):
                    print(mensagem[2:])
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                break

    def exibir_mensagem(self, mensagem):
        src_id = mensagem[2:15]
        dst_id = mensagem[15:28]
        timestamp = mensagem[28:38]
        data = mensagem[38:]
        print(f"\nNova mensagem de {src_id} para {dst_id} às {timestamp}: {data}")

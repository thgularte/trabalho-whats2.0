"""
Funções do cliente
- Registra-se 
- Se conectar
- Enviar mensagem 
- Criar grupo

Todas as funções do cliente, 
enviam um código pro servidor para que ele saiba qual função deve executar

"""

from datetime import datetime
import socket
import threading
import time

class Cliente:
    def __init__(self, host='localhost', port=8888):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)
        self.conectado = True

    def registra_usuario(self):
        message = '01'
        try:
            self.client_socket.send(message.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')
            print(f"Registro completado: {response[2:]}")
        except (socket.error, ConnectionError) as e:
            print(f"Erro ao registrar usuário: {e}")
            self.desconectar()

    def acessar_conta(self, client_id):
        message = '03' + client_id
        try:
            self.client_socket.send(message.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')
            if response.startswith('03'):
                threading.Thread(target=self.receber_mensagens, daemon=True).start()
                self.interface_usuario(client_id)
        except (socket.error, ConnectionError) as e:
            print(f"Erro ao acessar conta: {e}")
            self.desconectar()

    def interface_usuario(self, client_id):
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
                timestamp = int(time.time())
                self.enviar_mensagem(client_id, dst_id, timestamp, mensagem)
            elif opcao == '2':
                grupo_dst = input("Digite o id do grupo: ")
                mensagem = input("Digite a mensagem: ")
                self.enviar_mensagem_grupo(grupo_dst, client_id, timestamp, mensagem)
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
                self.desconectar()
                break
            else:
                print("Opção inválida. Tente novamente.")
    
    def enviar_mensagem(self, src_id, dst_id, timestamp, data):
        message = f'05{src_id}{dst_id}{timestamp}{data}'
        try:
            self.client_socket.send(message.encode('utf-8'))
            print("Mensagem enviada.")
        except (socket.error, ConnectionError) as e:
            print(f"Erro ao enviar mensagem: {e}")
            self.desconectar()

    def criar_grupo(self, criador_id, timestamp, members):
        message = f'10{criador_id}{timestamp}{"".join(members)}'
        try:
            self.client_socket.send(message.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')
            print(f"Grupo criado: {response[2:]}")
        except (socket.error, ConnectionError) as e:
            print(f"Erro ao criar grupo: {e}")
            self.desconectar()

    def enviar_mensagem_grupo(self, group_id, src_id, timestamp, data):
        message = f'11{group_id}{src_id}{timestamp}{data}'
        try:
            self.client_socket.send(message.encode('utf-8'))
            print("Mensagem de grupo enviada.")
        except (socket.error, ConnectionError) as e:
            print(f"Erro ao enviar mensagem de grupo: {e}")
            self.desconectar()
        
    def receber_mensagens(self):
        while self.conectado:
            try:
                mensagem = self.client_socket.recv(1024).decode('utf-8')
                if not mensagem:
                    raise ConnectionError("Conexão perdida.")
                if mensagem.startswith('06'):
                    self.exibir_mensagem(mensagem)
                elif mensagem.startswith('09'):
                    dst = mensagem[2:15]
                    timestamp = int(mensagem[15:25])  # Converte o timestamp para inteiro
                    data_formatada = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')
                    print(f"Usuário {dst} visualizou sua mensagem enviada as {data_formatada}.")

            except (socket.error, ConnectionError) as e:
                print(f"Erro ao receber mensagem: {e}")
                self.desconectar()
                break

    def exibir_mensagem(self, mensagem):
        src_id = mensagem[2:15]
        dst_id = mensagem[15:28]
        timestamp = int(mensagem[28:38])
        data = mensagem[38:]
        data_formatada = datetime.fromtimestamp(int(timestamp)).strftime('%d/%m/%Y %H:%M:%S')
        print(f"\n\n\nNova mensagem de {src_id} para {dst_id} às {data_formatada}. \n => {data}")

    def desconectar(self):
        self.conectado = False
        try:
            self.client_socket.close()
            print("Desconectado com sucesso.")
        except (socket.error, ConnectionError) as e:
            print(f"Erro ao desconectar: {e}")
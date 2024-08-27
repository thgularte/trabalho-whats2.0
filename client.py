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
import sqlite3
import threading
import time

#Classe com as funcionalidades do cliente
#Para lidar com as resposta do servidor todos os clientes conectados ficam
#esperando sempre alguma resposta do servidor para poder lidar com ela
class Cliente:
    def __init__(self, host='localhost', port=8888):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)
        self.conectado = True
        self.receber_mensagens_thread_started = False
        threading.Thread(target=self.receber_mensagens, daemon=True).start()

    #Função que lida com a interface pro usuario selecionar o que quer fazer
    def interface_usuario(self, client_id):
        while True:
            print("\nOpções:")
            print("1 - Enviar mensagem")
            print("2 - Mandar mensagem em grupo")
            print("3 - Criar um grupo")
            print("4 - Sair")
            print('5 - Contatos')
            print('6 - Adicionar contato')
            opcao = input("Opção: ")
            timestamp = int(time.time())
            if opcao == '1':
                dst_id = input("Digite o ID do destinatário: ")
                mensagem = input("Digite a mensagem: ")
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
            elif opcao == '5':
                self.listar_contatos(client_id)
            elif opcao == '6':
                id_contato = input('Digite o numero do contato: ')
                self.add_contato(client_id, id_contato)
            else:
                print("Opção inválida. Tente novamente.")

    def acessar_conta(self, client_id):
        message = '03' + client_id
        try:
            self.client_socket.send(message.encode('utf-8'))
            print(f' -=-=-= Usuário {client_id} conectado =-=-=-')
            self.interface_usuario(client_id)
        except (socket.error, ConnectionError) as e:
            print(f"Erro ao acessar conta: {e}")
            self.desconectar()

    #Função que faz o cliente ficar escutando o servidor
    def receber_mensagens(self):
        while self.conectado:
            try:
                mensagem = self.client_socket.recv(1024).decode('utf-8')
                if not mensagem:
                    raise ConnectionError("Conexão perdida.")
                self.processar_mensagem(mensagem)
            except (socket.error, ConnectionError) as e:
                print(f"Erro ao receber mensagem: {e}")
                self.desconectar()
                break

    #Função que lida com as respostas do servidor
    def processar_mensagem(self, mensagem):
        if mensagem.startswith('02'):
            print(f'Usuário cadastrado seu ID: {mensagem[2:]}')
        elif mensagem.startswith('06'):
            print(f'\n -= Você recebeu uma nova mensagem. =- ')
            self.exibir_mensagem(mensagem)
        elif mensagem.startswith('07'):
            print('Sua mensagem foi entregue para o destinátario.')
        elif mensagem.startswith('09'):
            dst = mensagem[2:15]
            timestamp = int(mensagem[15:25])
            data_formatada = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')
            print(f" -= Usuário {dst} visualizou sua mensagem às {data_formatada}. =- ")
        elif mensagem.startswith('11'):
            group_id = mensagem[2:15]
            group_timestamp = int(mensagem[15:25])
            formatted_time = datetime.fromtimestamp(group_timestamp).strftime('%d/%m/%Y %H:%M:%S')
            print(f'\nGrupo criado: {group_id} às {formatted_time}')
        elif mensagem.startswith('13'):
            print('\nMensagem enviada no grupo.')
        elif mensagem.startswith('14'):
            print(f'\nVocê foi adicionado ao grupo: {mensagem[2:15]}')

    def registra_usuario(self):
        message = '01'
        try:
            self.client_socket.send(message.encode('utf-8'))
        except (socket.error, ConnectionError) as e:
            print(f"Erro ao registrar usuário: {e}")
            self.desconectar()

    def enviar_mensagem(self, src_id, dst_id, timestamp, data):
        message = f'05{src_id}{dst_id}{timestamp}{data}'
        try:
            self.client_socket.send(message.encode('utf-8'))
            print(f"Mensagem enviada.")
        except (socket.error, ConnectionError) as e:
            print(f"Erro ao enviar mensagem: {e}")
            self.desconectar()

    def criar_grupo(self, criador_id, timestamp, members):
        # Monta a mensagem para criar o grupo
        message = f'10{criador_id}{timestamp}{"".join(members)}'
        try:            
            self.client_socket.send(message.encode('utf-8'))

        except (socket.error, ConnectionError) as e:
            print(f"Erro ao criar grupo: {e}")
            self.desconectar()


    def enviar_mensagem_grupo(self, group_id, src_id, timestamp, data):
        message = f'12{group_id}{src_id}{timestamp}{data}'
        try:
            self.client_socket.send(message.encode('utf-8'))
        except (socket.error, ConnectionError) as e:
            print(f"Erro ao enviar mensagem de grupo: {e}")
            self.desconectar()
        
   #Função exibir as msgs pro cliente
    def exibir_mensagem(self, mensagem):
        src_id = mensagem[2:15]
        dst_id = mensagem[15:28]
        timestamp = int(mensagem[28:38])
        data = mensagem[38:]
        data_formatada = datetime.fromtimestamp(int(timestamp)).strftime('%d/%m/%Y %H:%M:%S')
        print(f"\n\n\nNova mensagem de {src_id} para {dst_id} às {data_formatada}. \n => {data}")

    def listar_contatos(self, client_id, db_name='mensagens.db'):
        if len(client_id) != 13:
            raise ValueError("O ID do cliente deve ter exatamente 13 caracteres.")
        
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        try:
            # Executa a consulta para listar todos os contatos do cliente
            cursor.execute('''
                SELECT contato_id
                FROM contatos
                WHERE cliente_id = ?
            ''', (client_id,))
            
            # Obtém todos os resultados da consulta
            contatos = cursor.fetchall()
            
            # Formata os resultados como uma lista de IDs de contatos
            contatos_lista = [contato[0] for contato in contatos]
            print(contatos_lista)

        except Exception as e:
            print(f"Erro ao listar contatos: {e}")
            return []

        finally:
            conn.close()
    
    def add_contato(self, client_id, id_contato,db_name='mensagens.db'):
        if len(client_id) != 13 or len(id_contato) != 13:
            raise ValueError("Os IDs dos clientes devem ter exatamente 13 caracteres.")
    
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        try:
            # Insere o contato na tabela contatos
            cursor.execute('''
                INSERT INTO contatos (cliente_id, contato_id)
                VALUES (?, ?)
            ''', (client_id, id_contato))
            
            conn.commit()
            print(f"Contato {id_contato} adicionado com sucesso para o cliente {client_id}.")
            
        except sqlite3.IntegrityError as e:
            print(f"Erro de integridade ao adicionar contato: {e}")
        except Exception as e:
            print(f"Erro ao adicionar contato: {e}")
        finally:
            conn.close()

    def desconectar(self):
        self.conectado = False
        try:
            self.client_socket.close()
            print("Desconectado com sucesso.")
        except (socket.error, ConnectionError) as e:
            print(f"Erro ao desconectar: {e}")
import socket
import threading
import sqlite3
from datetime import datetime
from database import criar_banco_de_dados

class Servidor:
    def __init__(self, host='localhost', port=8888):
        self.server_address = (host, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientes = {}
        criar_banco_de_dados()
        self.start()

    def start(self):
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(5)
        print(f"Servidor rodando em {self.server_address[0]}:{self.server_address[1]}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.gerenciar_cliente, args=(client_socket,))
            client_thread.start()

    def gerenciar_cliente(self, client_socket):
        with client_socket:
            while True:
                try:
                    mensagem = client_socket.recv(1024).decode('utf-8')
                    if not mensagem:
                        raise ConnectionError("Conexão perdida.")
                    self.processar_mensagem(mensagem, client_socket)
                except (socket.error, ConnectionError) as e:
                    print(f"Erro no cliente: {e}")
                    break

    def processar_mensagem(self, mensagem, client_socket):
        tipo_mensagem = mensagem[:2]
        
        if tipo_mensagem == '01':
            self.registrar_usuario(client_socket)
        
        elif tipo_mensagem == '03':
            if len(mensagem) >= 15:  # Verifica se a mensagem tem o comprimento esperado
                client_id = mensagem[2:15]
                self.acessar_conta(client_socket, client_id)
            else:
                print(f"Erro: mensagem 03 com comprimento inesperado: {mensagem}")
        
        elif tipo_mensagem == '05':
            if len(mensagem) >= 38:  # Verifica se a mensagem tem o comprimento esperado
                src_id = mensagem[2:15]
                dst_id = mensagem[15:28]
                try:
                    timestamp = int(mensagem[28:38])
                    data = mensagem[38:]
                    self.enviar_mensagem(client_socket, src_id, dst_id, timestamp, data)
                except ValueError:
                    print(f"Erro: timestamp inválido na mensagem 05: {mensagem}")
            else:
                print(f"Erro: mensagem 05 com comprimento inesperado: {mensagem}")
        
        elif tipo_mensagem == '10':
            if len(mensagem) >= 25:  # Verifica se a mensagem tem o comprimento esperado
                criador_id = mensagem[2:15]
                try:
                    timestamp = int(mensagem[15:25])
                    members = mensagem[25:]
                    self.criar_grupo(client_socket, criador_id, timestamp, members)
                except ValueError:
                    print(f"Erro: timestamp inválido na mensagem 10: {mensagem}")
            else:
                print(f"Erro: mensagem 10 com comprimento inesperado: {mensagem}")
        
        elif tipo_mensagem == '11':
            if len(mensagem) >= 38:  # Verifica se a mensagem tem o comprimento esperado
                group_id = mensagem[2:15]
                src_id = mensagem[15:28]
                try:
                    timestamp = int(mensagem[28:38])
                    data = mensagem[38:]
                    self.enviar_mensagem_grupo(client_socket, group_id, src_id, timestamp, data)
                except ValueError:
                    print(f"Erro: timestamp inválido na mensagem 11: {mensagem}")
            else:
                print(f"Erro: mensagem 11 com comprimento inesperado: {mensagem}")
        
        else:
            print(f"Erro: tipo de mensagem desconhecido: {tipo_mensagem}")
    

    def receber_mensagens(self):
        while self.conectado:
            try:
                mensagem = self.client_socket.recv(1024).decode('utf-8')
                if not mensagem:
                    raise ConnectionError("Conexão perdida.")
                if mensagem.startswith('06'):
                    self.exibir_mensagem(mensagem)
                    # Enviar confirmação de leitura para o remetente
                    src_id = mensagem[2:15]
                    dst_id = mensagem[15:28]
                    timestamp = int(mensagem[28:38])
                    self.enviar_confirmacao_leitura(src_id, dst_id, timestamp)
                elif mensagem.startswith('09'):
                    dst = mensagem[2:15]
                    timestamp = int(mensagem[15:25])
                    data_formatada = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')
                    print(f"Usuário {dst} visualizou sua mensagem enviada às {data_formatada}.")
            except (socket.error, ConnectionError) as e:
                print(f"Erro ao receber mensagem: {e}")
                self.desconectar()
                break



    def registrar_usuario(self, client_socket):
        client_id = str(datetime.now().timestamp()).replace('.', '')[:13]
        self.clientes[client_id] = client_socket
        self.salvar_cliente_no_db(client_id)
        print(f"Cliente registrado: {client_id}")
        client_socket.send(f"01{client_id}".encode('utf-8'))

    def salvar_grupo_no_db(self, group_id, criador_id, timestamp, members):
        conn = sqlite3.connect('mensagens.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO grupos (id, criador, timestamp) VALUES (?, ?, ?)', 
                        (group_id, criador_id, timestamp))

            for member in members:
                if len(member) == 13:  # Verifica se o ID tem 13 caracteres
                    cursor.execute('INSERT INTO grupo_membros (group_id, member_id) VALUES (?, ?)', 
                                (group_id, member))
                else:
                    print(f"Erro: ID do membro {member} inválido. Deve ter 13 caracteres.")
                    raise ValueError("ID de membro inválido")

            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Erro ao criar grupo no banco de dados: {e}")
        finally:
            conn.close()


    def acessar_conta(self, client_socket, client_id):
        if client_id in self.clientes:
            print(f"Cliente {client_id} já está conectado.")
        else:
            self.clientes[client_id] = client_socket
            print(f"Cliente {client_id} conectado.")
            client_socket.send(f"03{client_id}".encode('utf-8'))
            self.enviar_mensagens_pendentes(client_socket, client_id)

    def enviar_mensagem(self, src_id, dst_id, timestamp, data):
        if dst_id in self.clientes:
            self.clientes[dst_id].send(f'06{src_id}{dst_id}{timestamp}{data}'.encode('utf-8'))
            print(f"Mensagem de {src_id} para {dst_id} enviada.")
            # Envia a confirmação de leitura para o remetente
            self.clientes[src_id].send(f'09{dst_id}{timestamp}'.encode('utf-8'))
        else:
            self.salvar_mensagem_pendente(src_id, dst_id, timestamp, data)
            print(f"Cliente {dst_id} offline. Mensagem pendente salva.")

    def enviar_mensagem_grupo(self, client_socket, group_id, src_id, timestamp, data):
        conn = sqlite3.connect('mensagens.db')
        cursor = conn.cursor()
        cursor.execute('SELECT member_id FROM grupo_membros WHERE group_id=?', (group_id,))
        members = cursor.fetchall()
        conn.close()

        for member_id, in members:
            if member_id != src_id:
                self.enviar_mensagem(client_socket, src_id, member_id, timestamp, data)

    def criar_grupo(self, criador_id, timestamp, members):
        # Verifica se o ID do criador tem 13 caracteres
        if len(criador_id) != 13:
            print(f"Erro: ID do criador com tamanho incorreto: {criador_id}")
            return
        
        # Divide a string de membros em uma lista, assumindo que cada membro tenha 13 caracteres
        member_ids = [members[i:i+13] for i in range(0, len(members), 13)]

        # Verifica se todos os IDs dos membros têm 13 caracteres
        for member_id in member_ids:
            if len(member_id) != 13:
                print(f"Erro: ID do membro com tamanho incorreto: {member_id}")
                return

        try:
            # Insere o grupo no banco de dados
            cursor = self.conexao.cursor()

            # Insere o grupo na tabela de grupos
            cursor.execute("INSERT INTO grupos (criador_id, timestamp) VALUES (?, ?)", (criador_id, timestamp))
            group_id = cursor.lastrowid  # Obtém o ID do grupo recém-criado

            # Insere cada membro na tabela de membros do grupo
            for member_id in member_ids:
                cursor.execute("INSERT INTO membros_grupo (group_id, member_id) VALUES (?, ?)", (group_id, member_id))

            # Salva as mudanças no banco de dados
            self.conexao.commit()

            print("Grupo criado com sucesso!")
        except Exception as e:
            print(f"Erro ao criar grupo no banco de dados: {e}")
            self.conexao.rollback()  # Reverte as mudanças no caso de erro


    def salvar_grupo_no_db(self, group_id, criador_id, timestamp, members):
        conn = sqlite3.connect('mensagens.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO grupos (id, criador, timestamp) VALUES (?, ?, ?)', 
                           (group_id, criador_id, timestamp))
            for member in members:
                cursor.execute('INSERT INTO grupo_membros (group_id, member_id) VALUES (?, ?)', 
                               (group_id, member))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Erro ao criar grupo no banco de dados: {e}")
        finally:
            conn.close()

    def salvar_mensagem_pendente(self, src_id, dst_id, timestamp, data):
        conn = sqlite3.connect('mensagens.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO mensagens_pendentes (src, dst, timestamp, data) VALUES (?, ?, ?, ?)',
                           (src_id, dst_id, timestamp, data))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Erro ao salvar mensagem pendente: {e}")
        finally:
            conn.close()

    def enviar_mensagens_pendentes(self, client_socket, client_id):
        conn = sqlite3.connect('mensagens.db')
        cursor = conn.cursor()
        cursor.execute('SELECT src, timestamp, data FROM mensagens_pendentes WHERE dst=?', (client_id,))
        mensagens = cursor.fetchall()
        conn.close()

        for src, timestamp, data in mensagens:
            self.enviar_mensagem(client_socket, src, client_id, timestamp, data)
        self.deletar_mensagens_pendentes(client_id)

    def deletar_mensagens_pendentes(self, client_id):
        conn = sqlite3.connect('mensagens.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM mensagens_pendentes WHERE dst=?', (client_id,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    servidor = Servidor()

"""
Funções do cliente
- Lidar com registro do usuário (01)
- Conectar clientes (03)
- Lidar com envio das mensagens (05)
"""

import socket
import threading
import sqlite3

class Servidor():
    # para rodar com clientes de outros dispositivos tem que alterar o host para usar o IP do pc que rodar o servidor
    def __init__(self, host='localhost', port=8888, db_name='mensagens.db'):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clientes_conectados = {}
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.running = True 


    def registro_usuario(self, client_socket):
        id_usuario = str(len(self.cursor.execute('SELECT * FROM clientes').fetchall()) + 1).zfill(13)
        self.cursor.execute('INSERT INTO clientes (id) VALUES (?)', (id_usuario,))
        self.conn.commit()
        response = '02' + id_usuario
        client_socket.send(response.encode('utf-8'))

    def enviar_mensagem(self, src_id, dst_id, timestamp, data):
        if dst_id not in self.clientes_conectados: #verifica se quem vai receber a msg ta online, se não guarda no banco 
            self.cursor.execute(
                'INSERT INTO mensagens_pendentes (src, dst, timestamp, data) VALUES (?, ?, ?, ?)',
                (src_id, dst_id, timestamp, data)
            )
            self.conn.commit()
            print(f"Mensagem de {src_id} para {dst_id} armazenada.")
        else:
            self.entregar_mensagem(dst_id, src_id, timestamp, data)

    def entregar_mensagem(self, dst_id, src_id, timestamp, data):
        if dst_id in self.clientes_conectados: #verifica se ta online
            #pega o destinatario e cria um obj da msg para enviar
            client_socket = self.clientes_conectados[dst_id] 
            mensagem = f'06{src_id}{dst_id}{timestamp}{data}'
            client_socket.send(mensagem.encode('utf-8'))
            print(f"Mensagem entregue para {dst_id}")
        else:
            print(f"Falha ao entregar a mensagem para {dst_id}: cliente não está online.")

    def conectar_cliente(self, client_socket, client_id):
        self.cursor.execute('SELECT * FROM clientes WHERE id = ?', (client_id,)) #verifica se o id da na tabela já
        result = self.cursor.fetchone()
        if result:
            #se ta na tabela conecta ao servidor
            print(f"Cliente {client_id} conectado.")
            self.clientes_conectados[client_id] = client_socket
            self.cursor.execute('SELECT * FROM mensagens_pendentes WHERE dst = ?', (client_id,)) #verificar se tem alguma msg para ele receber
            mensagens_pendentes = self.cursor.fetchall()
            for msg in mensagens_pendentes: #se tem msg vai entregar todas pendentes
                self.entregar_mensagem(client_id, msg[1], msg[3], msg[4])
                self.cursor.execute('DELETE FROM mensagens_pendentes WHERE id = ?', (msg[0],))
            self.conn.commit()
            response = '03' + client_id
            client_socket.send(response.encode('utf-8'))
        else:
            print(f"Cliente {client_id} não encontrado.")
            client_socket.close()

    def handle_cliente(self, client_socket):
        #lida com as ações do usuario/cliente
        # se quer se registrar, conectar ou enviar msg
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message.startswith('01'):
                    self.registro_usuario(client_socket)
                elif message.startswith('03'):
                    client_id = message[2:15]
                    self.conectar_cliente(client_socket, client_id)
                elif message.startswith('05'):
                    src_id = message[2:15]
                    dst_id = message[15:28]
                    timestamp = message[28:38]
                    data = message[38:]
                    self.enviar_mensagem(src_id, dst_id, timestamp, data)
            except:
                client_socket.close()
                break


    #FUNÇOES QUE VÃO LIDAR COM OS GRUPOS  

    #função que deve receber o id do criador do grupo e os membros e então cria o grupo na tabela do banco
    def criar_grupo(self, client_socket, criador_id, timestamp, members):
        group_id = str(len(self.cursor.execute('SELECT * FROM grupos').fetchall()) + 1).zfill(13)
        self.cursor.execute('INSERT INTO grupos (id, criador, timestamp) VALUES (?, ?, ?)', (group_id, criador_id, timestamp))
        for member in members:
            self.cursor.execute('INSERT INTO grupo_membros (group_id, member_id) VALUES (?, ?)', (group_id, member))
        self.conn.commit()
        response = '11' + group_id + timestamp + ''.join(members)
        for member in members:
            if member in self.clientes_conectados:
                self.clientes_conectados[member].send(response.encode('utf-8'))
        client_socket.send(response.encode('utf-8'))
    
    #função que lida com as mensagens enviadas dentro do grupo
    def mensagem_grupo(self, group_id, src_id, timestamp,data):
        self.cursor.execute('SELECT member_id FROM grupo_membros WHERE group_id = ?', (group_id,))
        membros = self.cursor.fetchall()
        mensagem = f'12{group_id}{src_id}{timestamp}{data}'
        
        for membro in membros:
            member_id = membro[0]
            if member_id in self.clientes_conectados:
                self.clientes_conectados[member_id].send(mensagem.encode('utf-8'))
            else:
                # Armazena mensagem para membros desconectados
                self.cursor.execute(
                    'INSERT INTO mensagens_pendentes (src, dst, timestamp, data) VALUES (?, ?, ?, ?)',
                    (src_id, member_id, timestamp, data)
                )
            self.conn.commit()

    #Função que conecta o servidor e cria as treandings dos usuários
    def run(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"Conexão recebida de {addr}")
                cliente_logado = threading.Thread(target=self.handle_cliente, args=(client_socket,))
                cliente_logado.start()
            except:
                break

    def stop(self): # função para desligar o servidor
        self.running = False
        self.server_socket.close()
        print("Servidor desligado.")

if __name__ == '__main__':
    servidor = Servidor()
    servidor.run()

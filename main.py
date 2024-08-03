import os
import sqlite3
from threading import Thread
from server import Servidor
from client import Cliente

def criar_banco_de_dados(db_name='mensagens.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id TEXT PRIMARY KEY CHECK (length(id) = 13),
            UNIQUE (id)
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contatos (
            cliente_id TEXT,
            contato_id TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (contato_id) REFERENCES clientes(id),
            CHECK (length(cliente_id) = 13),
            CHECK (length(contato_id) = 13)
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS msg_temporaria (
            originatario TEXT NOT NULL CHECK (length(originatario) = 13),
            destinatario TEXT NOT NULL CHECK (length(destinatario) = 13),
            timestamp INTEGER NOT NULL,
            msg TEXT NOT NULL CHECK (length(msg) <= 218)
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grupos (
            id TEXT PRIMARY KEY CHECK (length(id) = 13),
            criador TEXT,
            timestamp INTEGER,
            FOREIGN KEY (criador) REFERENCES clientes(id)
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grupo_membros (
            group_id TEXT,
            member_id TEXT,
            FOREIGN KEY(group_id) REFERENCES grupos(id),
            FOREIGN KEY(member_id) REFERENCES clientes(id),
            CHECK (length(group_id) = 13),
            CHECK (length(member_id) = 13)
        )
        ''')

    conn.commit()
    conn.close()

def cliente_interface(servidor):
    cliente = Cliente()
    while True:
        print("Selecione uma opção:")
        print("1. Registrar usuário")
        print("2. Conectar cliente")
        print("3. Enviar mensagem")
        print("4. Criar grupo")
        print("5. Enviar mensagem em grupo")
        print("6. Desligar servidor e sair")
        escolha = input("Opção: ")

        if escolha == '1':
            cliente.registra_usuario()
        elif escolha == '2':
            client_id = input("Digite o ID do cliente: ")
            cliente.acessar_conta(client_id)
        elif escolha == '3':
            src_id = input("Digite o ID do remetente: ")
            dst_id = input("Digite o ID do destinatário: ")
            timestamp = input("Digite o timestamp: ")
            data = input("Digite a mensagem: ")
            cliente.enviar_mensagem(src_id, dst_id, timestamp, data)
        elif escolha == '4':
            criador_id = input("Digite o ID do criador: ")
            timestamp = input("Digite o timestamp: ")
            members = input("Digite os IDs dos membros (separados por espaço): ").split()
            cliente.criar_grupo(criador_id, timestamp, members)
        elif escolha == '5':
            group_id = input("Digite o ID do grupo: ")
            src_id = input("Digite o ID do remetente: ")
            timestamp = input("Digite o timestamp: ")
            data = input("Digite a mensagem: ")
            cliente.enviar_mensagem_grupo(group_id, src_id, timestamp, data)
        elif escolha == '6':
            print("Desligando servidor e saindo...")
            servidor.stop()
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == '__main__':
    db_name = 'mensagens.db'
    if not os.path.exists(db_name):
        criar_banco_de_dados(db_name)

    servidor = Servidor(db_name=db_name)
    servidor_thread = Thread(target=servidor.run)
    servidor_thread.start()
    print('Servidor conectado...')

    cliente_interface(servidor)

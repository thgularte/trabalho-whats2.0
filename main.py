import os
import sqlite3
from server import Servidor

def criar_banco_de_dados(db_name='mensagens.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT CHECK (length(id) = 13),
        UNIQUE (id)
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
            id TEXT PRIMARY KEY,
            criador TEXT,
            timestamp INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grupo_membros (
            group_id TEXT,
            member_id TEXT,
            FOREIGN KEY(group_id) REFERENCES grupos(id),
            FOREIGN KEY(member_id) REFERENCES clientes(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    db_name = 'mensagens.db'
    if not os.path.exists(db_name):
        criar_banco_de_dados(db_name)
    servidor = Servidor(db_name=db_name)
    print('Servidor conectado ... ')
    servidor.run()

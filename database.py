import sqlite3

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

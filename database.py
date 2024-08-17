import sqlite3

def criar_banco_de_dados(db_name='mensagens.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Cria a tabela de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id TEXT PRIMARY KEY CHECK (length(id) = 13),
            UNIQUE (id)
        )
    ''')

    # Cria a tabela de contatos
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

    # Cria a tabela de mensagens pendentes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mensagens_pendentes (
            src TEXT NOT NULL CHECK (length(src) = 13),
            dst TEXT NOT NULL CHECK (length(dst) = 13),
            timestamp INTEGER NOT NULL,
            data TEXT NOT NULL CHECK (length(data) <= 218)
        )
    ''')

    # Cria a tabela de grupos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grupos (
            id TEXT PRIMARY KEY CHECK (length(id) = 13),
            criador TEXT NOT NULL,
            timestamp INTEGER,
            FOREIGN KEY (criador) REFERENCES clientes(id)
        )
    ''')

    # Cria a tabela de membros do grupo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grupo_membros (
            group_id TEXT,
            member_id TEXT,
            PRIMARY KEY (group_id, member_id),
            FOREIGN KEY(group_id) REFERENCES grupos(id),
            FOREIGN KEY(member_id) REFERENCES clientes(id),
            CHECK (length(group_id) = 13),
            CHECK (length(member_id) = 13)
        )
    ''')

    conn.commit()
    conn.close()
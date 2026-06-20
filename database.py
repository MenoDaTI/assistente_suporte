import sqlite3
from datetime import datetime

DB_NAME = "suporte.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # =========================
    # TABELA DE SESSÕES
    # =========================

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS sessoes
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       protocolo
                       TEXT,
                       cliente
                       TEXT,
                       descricao
                       TEXT,
                       inicio
                       DATETIME,
                       fim
                       DATETIME,
                       status
                       TEXT
                   )
                   """)

    # =========================
    # TABELA DE EVENTOS
    # =========================

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS eventos
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       sessao_id
                       INTEGER,
                       data_hora
                       DATETIME,
                       janela
                       TEXT,
                       aplicativo
                       TEXT,
                       observacao
                       TEXT,
                       duracao_segundos
                       INTEGER
                       DEFAULT
                       0,
                       FOREIGN
                       KEY
                   (
                       sessao_id
                   ) REFERENCES sessoes
                   (
                       id
                   )
                       )
                   """)

    # =========================
    # TABELA DE CONTEXTO
    # =========================

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS capturas_contexto
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       sessao_id
                       INTEGER
                       NOT
                       NULL,
                       evento_id
                       INTEGER,
                       data_hora
                       DATETIME
                       NOT
                       NULL,

                       tipo
                       TEXT
                       NOT
                       NULL,
                       origem
                       TEXT
                       NOT
                       NULL,

                       chave
                       TEXT
                       NOT
                       NULL,
                       valor
                       TEXT,

                       FOREIGN
                       KEY
                   (
                       sessao_id
                   ) REFERENCES sessoes
                   (
                       id
                   ),
                       FOREIGN KEY
                   (
                       evento_id
                   ) REFERENCES eventos
                   (
                       id
                   )
                       )
                   """)

    conn.commit()
    conn.close()


def registrar_evento(
        sessao_id,
        janela,
        aplicativo,
        titulo_janela=None,
        observacao=None):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
                   INSERT INTO eventos (sessao_id,
                                        data_hora,
                                        janela,
                                        aplicativo,
                                        titulo_janela,
                                        observacao)
                   VALUES (?, datetime('now'), ?, ?, ?, ?)
                   """, (
                       sessao_id,
                       janela,
                       aplicativo,
                       titulo_janela,
                       observacao
                   ))

    conn.commit()

    evento_id = cursor.lastrowid

    conn.close()

    return evento_id


def atualizar_duracao_evento(
        evento_id,
        duracao_segundos):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
                   UPDATE eventos
                   SET duracao_segundos = ?
                   WHERE id = ?
                   """, (
                       duracao_segundos,
                       evento_id
                   ))

    conn.commit()
    conn.close()


def registrar_contexto(
        sessao_id,
        tipo,
        origem,
        chave,
        valor,
        evento_id=None):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
                   INSERT INTO capturas_contexto (sessao_id,
                                                  evento_id,
                                                  data_hora,
                                                  tipo,
                                                  origem,
                                                  chave,
                                                  valor)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   """, (
                       sessao_id,
                       evento_id,
                       datetime.now(),
                       tipo,
                       origem,
                       chave,
                       valor
                   ))

    conn.commit()
    conn.close()


def contar_sessoes_hoje():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT COUNT(*)
                   FROM sessoes
                   WHERE DATE (inicio) = DATE ('now')
                   """)

    total = cursor.fetchone()[0]

    conn.close()

    return total


def contar_eventos_sessao(sessao_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT COUNT(*)
                   FROM eventos
                   WHERE sessao_id = ?
                   """, (sessao_id,))

    total = cursor.fetchone()[0]

    conn.close()

    return total


def contar_aplicativos_sessao(sessao_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT COUNT(DISTINCT aplicativo)
                   FROM eventos
                   WHERE sessao_id = ?
                   """, (sessao_id,))

    total = cursor.fetchone()[0]

    conn.close()

    return total

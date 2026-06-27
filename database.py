"""Camada de persistencia SQLite usada por monitores, resumo e IA."""

import sqlite3
from datetime import datetime

DB_NAME = "suporte.db"


def conectar():
    """Abre conexao SQLite no arquivo local do projeto."""
    return sqlite3.connect(DB_NAME)


def criar_tabelas():
    """Cria ou atualiza o schema minimo usado pela aplicacao."""
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
    # TABELA DE Eventos
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

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS navegacao
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       sessao_id INTEGER,
                       data_hora DATETIME,
                       navegador TEXT,
                       titulo TEXT,
                       categoria TEXT,
                       url TEXT,
                       FOREIGN KEY (sessao_id) REFERENCES sessoes (id)
                   )
                   """)

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS evidencias_ocr
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       sessao_id INTEGER,
                       data_hora DATETIME,
                       origem TEXT,
                       texto_extraido TEXT,
                       FOREIGN KEY (sessao_id) REFERENCES sessoes (id)
                   )
                   """)

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS entidades
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       sessao_id INTEGER,
                       data_hora DATETIME,
                       tipo TEXT,
                       valor TEXT,
                       FOREIGN KEY (sessao_id) REFERENCES sessoes (id)
                   )
                   """)

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS ai_contexto
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       sessao_id INTEGER,
                       data_hora DATETIME,
                       contexto_json TEXT,
                       confianca REAL,
                       FOREIGN KEY (sessao_id) REFERENCES sessoes (id)
                   )
                   """)

    colunas_eventos = [
        row[1]
        for row in cursor.execute("PRAGMA table_info(eventos)")
    ]

    if "titulo_janela" not in colunas_eventos:
        # Migra bancos antigos sem perder os eventos ja gravados.
        cursor.execute("""
                       ALTER TABLE eventos
                       ADD COLUMN titulo_janela TEXT
                       """)

    conn.commit()
    conn.close()


def registrar_evento(
        sessao_id,
        janela,
        aplicativo,
        titulo_janela=None,
        observacao=None):
    """Insere evento de janela/aplicativo e devolve seu id."""
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
    """Atualiza a duracao de um evento quando a janela muda."""
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
    """Grava informacao estruturada associada a sessao e opcionalmente evento."""
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
    """Conta sessoes abertas no dia atual para o painel."""
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
    """Conta eventos capturados em uma sessao."""
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
    """Conta aplicativos distintos usados durante uma sessao."""
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
def registrar_evidencia_ocr(
        sessao_id,
        origem,
        texto_extraido):
    """Salva texto bruto obtido por OCR."""

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
                   INSERT INTO evidencias_ocr (
                       sessao_id,
                       data_hora,
                       origem,
                       texto_extraido
                   )
                   VALUES (?, ?, ?, ?)
                   """, (
                       sessao_id,
                       datetime.now(),
                       origem,
                       texto_extraido
                   ))

    conn.commit()
    conn.close()


def registrar_entidade(
        sessao_id,
        tipo,
        valor):
    """Salva uma entidade unica para a sessao."""

    if not valor:
        return

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT id
                   FROM entidades
                   WHERE sessao_id = ?
                     AND tipo = ?
                     AND valor = ?
                   LIMIT 1
                   """, (
                       sessao_id,
                       tipo,
                       valor
                   ))

    if cursor.fetchone():
        conn.close()
        return

    cursor.execute("""
                   INSERT INTO entidades (
                       sessao_id,
                       data_hora,
                       tipo,
                       valor
                   )
                   VALUES (?, ?, ?, ?)
                   """, (
                       sessao_id,
                       datetime.now(),
                       tipo,
                       valor
                   ))

    conn.commit()
    conn.close()


def registrar_entidades(
        sessao_id,
        entidades):
    """Salva uma colecao de entidades ja extraidas."""

    for tipo, valor in entidades:
        registrar_entidade(
            sessao_id,
            tipo,
            valor
        )


def registrar_navegacao(
        sessao_id,
        navegador,
        titulo,
        categoria,
        url=None):
    """Registra uma pagina ou aba de navegador visitada."""

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO navegacao (
        sessao_id,
        data_hora,
        navegador,
        titulo,
        categoria,
        url
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        sessao_id,
        datetime.now(),
        navegador,
        titulo,
        categoria,
        url
    ))

    conn.commit()
    conn.close()
def registrar_ai_contexto(
        sessao_id,
        contexto_json,
        confianca):
    """Persiste o resultado da analise por IA ou fallback local."""

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO ai_contexto (
        sessao_id,
        data_hora,
        contexto_json,
        confianca
    )
    VALUES (?, datetime('now'), ?, ?)
    """, (
        sessao_id,
        contexto_json,
        confianca
    ))

    conn.commit()
    conn.close()

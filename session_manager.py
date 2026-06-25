from datetime import datetime
from database import (
    conectar,
    registrar_evento,
    registrar_evidencia_ocr,
    registrar_navegacao
)

class SessionManager:

    def __init__(self):
        self.sessao_ativa = None
        self.protocolo_ativo = None
        self.descricao_ativa = None
        self.cliente_ativo = None

    def iniciar_sessao(
            self,
            protocolo,
            descricao,
            cliente=None):

        if self.sessao_ativa:
            print("Já existe uma sessão ativa.")
            return

        inicio = datetime.now()

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO sessoes (
            protocolo,
            cliente,
            descricao,
            inicio,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            protocolo,
            cliente,
            descricao,
            inicio,
            "EM_ANDAMENTO"
        ))

        conn.commit()

        sessao_id = cursor.lastrowid

        conn.close()

        self.sessao_ativa = sessao_id
        self.protocolo_ativo = protocolo
        self.descricao_ativa = descricao
        self.cliente_ativo = cliente

        print()
        print("================================")
        print("SESSÃO INICIADA")
        print(f"ID: {sessao_id}")
        print(f"PROTOCOLO: {protocolo}")
        print(f"CLIENTE: {cliente}")
        print("================================")
        print()

    def registrar_janela(
            self,
            janela,
            aplicativo,
            titulo_janela=None):

        if not self.sessao_ativa:
            return None

        return registrar_evento(
            sessao_id=self.sessao_ativa,
            janela=janela,
            aplicativo=aplicativo,
            titulo_janela=titulo_janela,
            observacao=None
        )

    def finalizar_sessao(self):

        if not self.sessao_ativa:
            print("Nenhuma sessão ativa.")
            return

        fim = datetime.now()

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE sessoes
        SET fim = ?,
            status = ?
        WHERE id = ?
        """, (
            fim,
            "FINALIZADA",
            self.sessao_ativa
        ))

        conn.commit()
        conn.close()

        print()
        print("================================")
        print("SESSÃO FINALIZADA")
        print(f"ID: {self.sessao_ativa}")
        print("================================")
        print()

        sessao_finalizada = self.sessao_ativa


        self.sessao_ativa = None
        self.protocolo_ativo = None
        self.descricao_ativa = None
        self.cliente_ativo = None
        return sessao_finalizada

    def registrar_ocr(
            self,
            origem,
            texto):

        if not self.sessao_ativa:
            return

        registrar_evidencia_ocr(
            self.sessao_ativa,
            origem,
            texto
        )

    def registrar_navegacao(
            self,
            navegador,
            titulo,
            categoria,
            url=None):

        if not self.sessao_ativa:
            return

        registrar_navegacao(
            self.sessao_ativa,
            navegador,
            titulo,
            categoria,
            url
        )
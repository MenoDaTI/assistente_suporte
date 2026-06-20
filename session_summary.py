import sqlite3
from database import DB_NAME


class SessionSummary:

    def __init__(self, sessao_id):

        self.sessao_id = sessao_id

    def gerar(self):

        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        # ==========================
        # SESSÃO
        # ==========================

        cursor.execute("""
        SELECT *
        FROM sessoes
        WHERE id = ?
        """, (self.sessao_id,))

        sessao = cursor.fetchone()

        if not sessao:

            conn.close()
            return None

        # ==========================
        # EVENTOS
        # ==========================

        cursor.execute("""
        SELECT *
        FROM eventos
        WHERE sessao_id = ?
        ORDER BY data_hora
        """, (self.sessao_id,))

        eventos = [
            dict(row)
            for row in cursor.fetchall()
        ]

        # ==========================
        # CONTEXTO
        # ==========================

        cursor.execute("""
        SELECT *
        FROM capturas_contexto
        WHERE sessao_id = ?
        ORDER BY data_hora
        """, (self.sessao_id,))

        contexto = [
            dict(row)
            for row in cursor.fetchall()
        ]

        # ==========================
        # NAVEGAÇÃO
        # ==========================

        cursor.execute("""
        SELECT *
        FROM navegacao
        WHERE sessao_id = ?
        ORDER BY data_hora
        """, (self.sessao_id,))

        navegacao = [
            dict(row)
            for row in cursor.fetchall()
        ]

        # ==========================
        # OCR
        # ==========================

        cursor.execute("""
        SELECT *
        FROM evidencias_ocr
        WHERE sessao_id = ?
        ORDER BY data_hora
        """, (self.sessao_id,))

        ocr = [
            dict(row)
            for row in cursor.fetchall()
        ]

        # ==========================
        # ENTIDADES
        # ==========================

        cursor.execute("""
        SELECT *
        FROM entidades
        WHERE sessao_id = ?
        ORDER BY data_hora
        """, (self.sessao_id,))

        entidades = [
            dict(row)
            for row in cursor.fetchall()
        ]

        conn.close()

        # ==========================
        # APLICATIVOS ÚNICOS
        # ==========================

        aplicativos = list(set(
            evento["aplicativo"]
            for evento in eventos
            if evento["aplicativo"]
        ))

        # ==========================
        # CATEGORIAS VISITADAS
        # ==========================

        categorias = list(set(
            nav["categoria"]
            for nav in navegacao
            if nav.get("categoria")
        ))

        # ==========================
        # RESUMO FINAL
        # ==========================

        resumo = {

            "sessao_id": sessao["id"],

            "protocolo": sessao["protocolo"],

            "cliente": sessao["cliente"],

            "descricao": sessao["descricao"],

            "inicio": sessao["inicio"],

            "fim": sessao["fim"],

            "status": sessao["status"],

            "aplicativos": aplicativos,

            "categorias_navegacao": categorias,

            "total_eventos": len(eventos),

            "total_contextos": len(contexto),

            "total_navegacoes": len(navegacao),

            "total_ocr": len(ocr),

            "total_entidades": len(entidades),

            "eventos": eventos,

            "contexto": contexto,

            "navegacao": navegacao,

            "ocr": ocr,

            "entidades": entidades
        }

        return resumo
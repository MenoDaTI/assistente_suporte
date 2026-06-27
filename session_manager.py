"""Gerencia abertura, fechamento e registros associados a uma sessao."""

import json
from datetime import datetime
from database import (
    conectar,
    registrar_evento,
    registrar_evidencia_ocr,
    registrar_navegacao,
    registrar_entidades,
    registrar_contexto
)
from entity_extractor import EntityExtractor

class SessionManager:
    """Mantem estado da sessao ativa e centraliza os registros no banco."""

    def __init__(self):
        """Inicializa a aplicacao sem sessao ativa."""
        self.sessao_ativa = None
        self.protocolo_ativo = None
        self.descricao_ativa = None
        self.cliente_ativo = None

    def iniciar_sessao(
            self,
            protocolo,
            descricao,
            cliente=None):
        """Cria uma sessao no banco e guarda seu estado em memoria."""

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

        # A descricao inicial pode conter protocolo, cliente, modulo ou acao.
        self._registrar_entidades_texto(
            "SESSAO",
            f"{protocolo} {cliente or ''} {descricao or ''}"
        )

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
        """Registra troca de janela e extrai entidades do titulo."""

        if not self.sessao_ativa:
            return None

        evento_id = registrar_evento(
            sessao_id=self.sessao_ativa,
            janela=janela,
            aplicativo=aplicativo,
            titulo_janela=titulo_janela,
            observacao=None
        )

        self._registrar_entidades_texto(
            aplicativo,
            f"{janela or ''} {titulo_janela or ''}"
        )

        return evento_id

    def finalizar_sessao(self):
        """Fecha a sessao ativa e devolve o id para analise posterior."""

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
        """Salva OCR bruto e extrai entidades do texto capturado."""

        if not self.sessao_ativa:
            return

        registrar_evidencia_ocr(
            self.sessao_ativa,
            origem,
            texto
        )

        self._registrar_entidades_texto(
            origem,
            texto
        )

    def registrar_navegacao(
            self,
            navegador,
            titulo,
            categoria,
            url=None):
        """Salva navegacao resumida e entidades vindas de titulo/URL."""

        if not self.sessao_ativa:
            return

        registrar_navegacao(
            self.sessao_ativa,
            navegador,
            titulo,
            categoria,
            url
        )

        self._registrar_entidades_texto(
            navegador,
            f"{titulo or ''} {url or ''} {categoria or ''}"
        )

    def _registrar_entidades_texto(
            self,
            origem,
            texto):
        """Extrai entidades de qualquer texto e persiste sem duplicar."""

        if not self.sessao_ativa or not texto:
            return

        entidades = EntityExtractor.extrair(texto)

        if entidades:
            registrar_entidades(
                self.sessao_ativa,
                entidades
            )

    def registrar_contexto_web(
            self,
            navegador,
            conteudo_web,
            evento_id=None):
        """Salva detalhes web como URL, texto visivel e campos de formulario."""

        if not self.sessao_ativa or not conteudo_web:
            return

        origem = (
            conteudo_web.get("url")
            or conteudo_web.get("titulo_pagina")
            or navegador
            or "WEB"
        )

        url = conteudo_web.get("url")

        if url:
            # URL e o ponto de rastreabilidade mais forte para paginas web.
            registrar_contexto(
                self.sessao_ativa,
                "WEB",
                navegador,
                "url",
                url,
                evento_id
            )

        origem_url = conteudo_web.get("origem_url")

        if origem_url:
            # Indica se a URL veio do CDP ou foi inferida pelo titulo.
            registrar_contexto(
                self.sessao_ativa,
                "WEB",
                navegador,
                "origem_url",
                origem_url,
                evento_id
            )

        texto = (
            conteudo_web.get("texto")
            or ""
        ).strip()

        if texto:
            # Texto visivel ajuda a documentar conteudo de chamados e telas.
            registrar_contexto(
                self.sessao_ativa,
                "WEB_TEXTO",
                origem,
                "texto_visivel",
                texto[:5000],
                evento_id
            )

            self._registrar_entidades_texto(
                origem,
                texto
            )

        formularios = (
            conteudo_web.get("formularios")
            or []
        )

        for campo in formularios:
            # Cada input/select/textarea vira uma captura consultavel depois.
            chave = (
                campo.get("chave")
                or campo.get("tipo")
                or "campo"
            )

            valor = campo.get("valor")

            if valor is None:
                valor = ""

            registrar_contexto(
                self.sessao_ativa,
                "FORMULARIO",
                origem,
                chave[:120],
                str(valor)[:500],
                evento_id
            )

        if formularios:
            # Campos preenchidos tambem podem conter entidades relevantes.
            self._registrar_entidades_texto(
                origem,
                json.dumps(
                    formularios,
                    ensure_ascii=False
                )
            )

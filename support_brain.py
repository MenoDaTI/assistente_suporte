import json
import sqlite3
from datetime import datetime

from database import DB_NAME, conectar, registrar_ai_contexto
from session_summary import SessionSummary
from timeline_generator import TimelineGenerator
from ai_context_analyzer import AIContextAnalyzer


class SupportBrain:

    def __init__(self, sessao_id):
        self.sessao_id = sessao_id
        self.ai = AIContextAnalyzer()

    def analisar_sessao(self):
        resumo = SessionSummary(self.sessao_id).gerar()

        if not resumo:
            return {
                "erro": "Sessão não encontrada."
            }

        timeline = TimelineGenerator(self.sessao_id).gerar()

        texto_ocr = self._unificar_ocr(
            resumo.get("ocr", [])
        )

        contexto_ia = self.ai.analisar(
            janela=self._ultima_janela(resumo),
            aplicativo=self._ultimo_aplicativo(resumo),
            texto_ocr=texto_ocr,
            protocolo=resumo.get("protocolo"),
            cliente=resumo.get("cliente"),
            descricao=resumo.get("descricao"),
            timeline=timeline,
            categorias_navegacao=resumo.get(
                "categorias_navegacao",
                []
            )
        )

        similares = self.buscar_contextos_similares(
            contexto_ia
        )

        resultado = {
            "sessao_id": self.sessao_id,
            "protocolo": resumo.get("protocolo"),
            "cliente": resumo.get("cliente"),
            "descricao": resumo.get("descricao"),
            "timeline": timeline,
            "contexto_ia": contexto_ia,
            "historico_similar": similares,
            "analisado_em": datetime.now().isoformat()
        }

        self.salvar_contexto(resultado)

        return resultado

    def _unificar_ocr(self, registros_ocr):
        textos = []

        for item in registros_ocr:
            texto = item.get("texto_extraido")

            if texto:
                textos.append(texto)

        return "\n\n".join(textos)

    def _ultima_janela(self, resumo):
        eventos = resumo.get("eventos", [])

        if not eventos:
            return ""

        return eventos[-1].get("titulo_janela") or eventos[-1].get("janela") or ""

    def _ultimo_aplicativo(self, resumo):
        eventos = resumo.get("eventos", [])

        if not eventos:
            return ""

        return eventos[-1].get("aplicativo") or ""

    def buscar_contextos_similares(self, contexto_ia):
        categoria = contexto_ia.get("categoria")
        subcategoria = contexto_ia.get("subcategoria")

        if not categoria:
            return []

        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
        SELECT *
        FROM ai_contexto
        ORDER BY data_hora DESC
        LIMIT 50
        """)

        resultados = []

        for row in cursor.fetchall():
            try:
                dados = json.loads(row["contexto_json"])
            except Exception:
                continue

            contexto = dados.get("contexto_ia", dados)

            if (
                    contexto.get("categoria") == categoria
                    or contexto.get("subcategoria") == subcategoria
            ):
                resultados.append({
                    "id": row["id"],
                    "sessao_id": row["sessao_id"],
                    "data_hora": row["data_hora"],
                    "categoria": contexto.get("categoria"),
                    "subcategoria": contexto.get("subcategoria"),
                    "tipo_atendimento": contexto.get("tipo_atendimento"),
                    "objetivo_detectado": contexto.get("objetivo_detectado")
                })

        conn.close()

        return resultados[:5]

    def salvar_contexto(self, resultado):
        contexto_json = json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2
        )

        confianca = (
            resultado
            .get("contexto_ia", {})
            .get("confianca", 0.0)
        )

        registrar_ai_contexto(
            sessao_id=self.sessao_id,
            contexto_json=contexto_json,
            confianca=confianca
        )
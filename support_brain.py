"""Orquestra resumo, timeline, IA, fallback local e historico similar."""

import json
import sqlite3
from datetime import datetime

from database import DB_NAME, conectar, registrar_ai_contexto
from session_summary import SessionSummary
from timeline_generator import TimelineGenerator
from ai_context_analyzer import AIContextAnalyzer
from entity_extractor import EntityExtractor


class SupportBrain:
    """Camada de orquestracao que gera a analise final de uma sessao."""

    def __init__(self, sessao_id):
        """Recebe a sessao alvo e prepara o analisador de IA."""
        self.sessao_id = sessao_id
        self.ai = AIContextAnalyzer()

    def analisar_sessao(self):
        """Gera resumo, timeline, contexto IA/fallback e salva o resultado."""
        resumo = SessionSummary(self.sessao_id).gerar()

        if not resumo:
            return {
                "erro": "Sessão não encontrada."
            }

        timeline = TimelineGenerator(self.sessao_id).gerar()

        texto_ocr = self._unificar_ocr(
            resumo.get("ocr", [])
        )

        # Tenta primeiro usar a IA local para interpretar o atendimento.
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

        if contexto_ia.get("categoria") == "ERRO":
            # Se Ollama falhar, ainda produz uma analise util por regras.
            contexto_ia = self._analisar_com_regras(
                resumo,
                timeline,
                texto_ocr,
                contexto_ia
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
        """Concatena todos os textos OCR da sessao para alimentar analise."""
        textos = []

        for item in registros_ocr:
            texto = item.get("texto_extraido")

            if texto:
                textos.append(texto)

        return "\n\n".join(textos)

    def _ultima_janela(self, resumo):
        """Retorna o ultimo titulo de janela conhecido da sessao."""
        eventos = resumo.get("eventos", [])

        if not eventos:
            return ""

        return eventos[-1].get("titulo_janela") or eventos[-1].get("janela") or ""

    def _ultimo_aplicativo(self, resumo):
        """Retorna o ultimo aplicativo registrado nos eventos."""
        eventos = resumo.get("eventos", [])

        if not eventos:
            return ""

        return eventos[-1].get("aplicativo") or ""

    def buscar_contextos_similares(self, contexto_ia):
        """Busca analises anteriores com categoria/subcategoria parecidas."""
        categoria = contexto_ia.get("categoria")
        subcategoria = contexto_ia.get("subcategoria")

        if not categoria or categoria == "ERRO":
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

    def _analisar_com_regras(
            self,
            resumo,
            timeline,
            texto_ocr,
            erro_original=None):
        """Classifica a sessao por heuristicas quando a IA nao responde."""

        # Une descricao, timeline, contexto web, eventos e OCR em um texto base.
        texto_base = " ".join([
            resumo.get("descricao") or "",
            " ".join(timeline),
            " ".join(resumo.get("categorias_navegacao", [])),
            " ".join(
                str(item.get("valor") or "")
                for item in resumo.get("contexto", [])
            ),
            " ".join(
                str(item.get("chave") or "")
                for item in resumo.get("contexto", [])
            ),
            " ".join(
                evento.get("titulo_janela")
                or evento.get("janela")
                or ""
                for evento in resumo.get("eventos", [])
            ),
            texto_ocr or ""
        ]).lower()

        entidades = self._organizar_entidades(
            resumo.get("entidades", []),
            texto_base
        )

        # Valores padrao usados quando nenhuma regra especifica se aplica.
        categoria = "GERAL"
        subcategoria = ""
        sistema = ""
        tipo_atendimento = "Atendimento de suporte tecnico"
        objetivo = resumo.get("descricao") or "Atendimento analisado por regras locais"
        acoes = []
        tecnologias = []
        proximo_passo = "Revisar os dados capturados e complementar campos que nao aparecem em tela."
        complexidade = "BAIXA"
        confianca = 0.45

        if any(
                termo in texto_base
                for termo in ["ura", "audio", "rota", "fila", "vsphone"]
        ):
            # Padrao comum de atendimento em modulos de telefonia/URA.
            categoria = "TELEFONIA"
            subcategoria = "URA"
            sistema = "VsPhone"
            tipo_atendimento = "Inclusao ou ajuste de opcao em URA"
            objetivo = resumo.get("descricao") or "Ajuste de URA"
            tecnologias.extend([
                "VsPhone",
                "URA",
                "Telefonia"
            ])
            confianca = 0.72

        if any(
                termo in texto_base
                for termo in ["asterisk", "sip", "pjsip", "ramal"]
        ):
            # Padrao de diagnostico tecnico VoIP/Asterisk.
            categoria = "VOIP"
            subcategoria = "ASTERISK"
            sistema = "Asterisk"
            tipo_atendimento = "Diagnostico de ambiente VoIP"
            tecnologias.extend([
                "Asterisk",
                "SIP"
            ])
            complexidade = "MEDIA"
            confianca = max(confianca, 0.76)

        acoes = self._acoes_a_partir_timeline(timeline)

        if not acoes:
            acoes = [
                "Consulta de informacoes do atendimento",
                "Analise de telas e sistemas acessados"
            ]

        if "OMNIA" in resumo.get("categorias_navegacao", []):
            tecnologias.append("VS Omnia")

        if "GLPI" in resumo.get("categorias_navegacao", []):
            tecnologias.append("GLPI")

        if "VSPHONE" in resumo.get("categorias_navegacao", []):
            tecnologias.append("VsPhone")

        observacoes = []

        if erro_original:
            observacoes.append(
                erro_original.get("objetivo_detectado", "")
            )

        return {
            "categoria": categoria,
            "subcategoria": subcategoria,
            "sistema": sistema,
            "aplicativo": self._ultimo_aplicativo(resumo),
            "tipo_atendimento": tipo_atendimento,
            "objetivo_detectado": objetivo,
            "acoes_detectadas": acoes,
            "tecnologias": list(dict.fromkeys(tecnologias)),
            "entidades": entidades,
            "proximo_passo_sugerido": proximo_passo,
            "nivel_complexidade": complexidade,
            "confianca": confianca,
            "origem_analise": "REGRAS_LOCAIS",
            "observacoes": [
                obs
                for obs in observacoes
                if obs
            ]
        }

    @staticmethod
    def _organizar_entidades(
            registros,
            texto_extra=""):
        """Agrupa entidades salvas e extrai complementos do texto agregado."""

        mapa = {
            "ips": [],
            "ramais": [],
            "comandos": [],
            "protocolos": [],
            "sistemas": [],
            "modulos": [],
            "dominios": [],
            "acoes": []
        }

        destinos = {
            "IP": "ips",
            "RAMAL": "ramais",
            "COMANDO": "comandos",
            "PROTOCOLO": "protocolos",
            "SISTEMA": "sistemas",
            "MODULO": "modulos",
            "DOMINIO": "dominios",
            "ACAO": "acoes"
        }

        for registro in registros:
            # Aproveita primeiro o que ja foi persistido durante a captura.
            tipo = registro.get("tipo")
            valor = registro.get("valor")
            destino = destinos.get(tipo)

            if destino and valor and valor not in mapa[destino]:
                mapa[destino].append(valor)

        for tipo, valor in EntityExtractor.extrair(texto_extra):
            # Depois completa lacunas extraindo entidades do texto consolidado.
            destino = destinos.get(tipo)

            if destino and valor and valor not in mapa[destino]:
                mapa[destino].append(valor)

        return mapa

    @staticmethod
    def _acoes_a_partir_timeline(timeline):
        """Traduz etapas da timeline em acoes tecnicas detectadas."""

        acoes = []

        for etapa in timeline:
            etapa_lower = etapa.lower()

            if "chamado" in etapa_lower:
                acoes.append("Consulta ao chamado")

            elif "omnia" in etapa_lower:
                acoes.append("Consulta ao VS Omnia")

            elif "ura" in etapa_lower:
                acoes.append("Cadastro ou ajuste de URA")

            elif "audio" in etapa_lower:
                acoes.append("Criacao ou cadastro de audio")

            elif "conversao" in etapa_lower:
                acoes.append("Conversao de arquivo de audio")

            elif "roteamento" in etapa_lower or "rotas" in etapa_lower:
                acoes.append("Ajuste ou consulta de roteamento")

            elif "realtime" in etapa_lower or "validacao" in etapa_lower:
                acoes.append("Validacao do fluxo em tempo real")

            elif "fila" in etapa_lower:
                acoes.append("Consulta ou ajuste de fila")

        return list(dict.fromkeys(acoes))

    def salvar_contexto(self, resultado):
        """Persiste a analise final no historico de contextos de IA."""
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
